import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, rm, symlink, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { promisify } from "node:util";

// Both the publisher and the real ClawHub CLI must reach the local registry fixture.
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";
const { publishRelease } = await import("../scripts/publish-clawhub.mjs");
const exec = promisify(execFile);
const VERSION = "1.2.3";
const OWNER = "parallel-test";
const TOKEN = "integration-test-token";
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const file = (path, content) => ({ path, size: Buffer.byteLength(content), sha256: digest(content) });
const manifest = (name) => `---\nname: ${name}\ndescription: Integration test skill\n---\n\n# ${name}\n`;

async function release(t, names = ["alpha"]) {
  const root = await mkdtemp(join(tmpdir(), "clawhub-test-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const git = async (...args) => (await exec("git", args, { cwd: root })).stdout.trim();
  await git("init", "--initial-branch=main");
  await writeFile(join(root, "VERSION"), `${VERSION}\n`);
  const files = new Map();
  for (const name of names) {
    await mkdir(join(root, "skills", name), { recursive: true });
    await writeFile(join(root, "skills", name, "SKILL.md"), manifest(name));
    files.set(name, [file("SKILL.md", manifest(name))]);
  }
  const commit = async () => {
    await git("add", ".");
    await git("-c", "user.name=Integration Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-m", "Test release");
  };
  await commit();
  await git("tag", `v${VERSION}`);
  return { root, git, commit, files, sha: await git("rev-parse", "HEAD") };
}

async function registry(t, { states = new Map(), afterSubmit = 2, readStatus, historicalMatch = false } = {}) {
  const requests = [];
  const publishes = [];
  const tickets = new Map();
  const uploads = new Map();
  let base;
  const server = createServer((request, response) => {
    (async () => {
      const url = new URL(request.url, base);
      const chunks = [];
      for await (const chunk of request) chunks.push(chunk);
      const bytes = Buffer.concat(chunks);
      const entry = { method: request.method, path: url.pathname, query: Object.fromEntries(url.searchParams), bytes };
      requests.push(entry);
      const send = (status, body) => {
        response.writeHead(status, { "Content-Type": "application/json" });
        response.end(JSON.stringify(body));
      };
      if (request.headers.authorization !== `Bearer ${TOKEN}`) return send(401, { error: "Invalid token" });
      const exact = /^\/api\/v1\/skills\/([^/]+)\/versions\/([^/]+)(\/publication)?$/.exec(url.pathname);
      if (exact) {
        assert.equal(url.searchParams.get("ownerHandle"), OWNER);
        assert.equal(exact[2], VERSION);
        const status = typeof readStatus === "function" ? readStatus(entry) : readStatus;
        if (status) return send(status, { error: "Cannot read version" });
        const state = states.get(exact[1]);
        if (!state) return send(404, { error: "Version not found" });
        if (!exact[3]) {
          state.reads = (state.reads || 0) + 1;
          if (state.kind === "pending" && state.reads > state.publishAfterReads) state.kind = "published";
          if (state.kind !== "published") return send(404, { error: "Not public" });
          return send(200, {
            skill: { slug: exact[1], displayName: exact[1] },
            version: { version: VERSION, createdAt: 1, changelog: "Test", files: state.files },
          });
        }
        return send(200, {
          skill: { slug: exact[1], displayName: exact[1] },
          publication: { version: VERSION, stage: state.stage || "pending_checks", retrying: false, updatedAt: 1 },
        });
      }
      if (url.pathname === "/api/v1/resolve") {
        assert.equal(url.searchParams.get("ownerHandle"), OWNER);
        return send(200, {
          match: historicalMatch ? { version: "1.2.2" } : null,
          latestVersion: historicalMatch ? { version: "1.2.2" } : null,
        });
      }
      if (url.pathname === "/api/v1/skills/-/upload-url" && request.method === "POST") {
        const metadata = JSON.parse(bytes);
        const id = `ticket-${tickets.size}`;
        tickets.set(id, metadata);
        return send(200, { uploadUrl: `${base}/upload/${id}`, uploadTicket: id });
      }
      if (url.pathname.startsWith("/upload/") && request.method === "POST") {
        const id = url.pathname.split("/").at(-1);
        const metadata = tickets.get(id);
        assert.ok(metadata, "upload requires a ticket");
        assert.equal(metadata.sha256, digest(bytes));
        assert.equal(metadata.size, bytes.length);
        uploads.set(id, bytes);
        return send(200, { storageId: id });
      }
      if (url.pathname === "/api/v1/skills" && request.method === "POST") {
        const body = JSON.parse(bytes);
        assert.equal(body.ownerHandle, OWNER);
        assert.equal(body.version, VERSION);
        assert.equal(body.acceptLicenseTerms, true);
        assert.equal(states.has(body.slug), false, "existing versions must not be uploaded again");
        for (const uploaded of body.files) {
          assert.ok(uploads.has(uploaded.storageId), "publish references uploaded bytes");
          assert.equal(uploaded.sha256, digest(uploads.get(uploaded.storageId)));
        }
        publishes.push(body);
        states.set(body.slug, {
          kind: "pending", publishAfterReads: afterSubmit,
          files: [...body.files, file("SKILL-CARD.md", "Generated by ClawHub")],
        });
        return send(200, { ok: true, skillId: body.slug, versionId: `${body.slug}-${VERSION}`, publicationStatus: "pending" });
      }
      return send(500, { error: `Unexpected registry request: ${request.method} ${url.pathname}` });
    })().catch((error) => {
      response.writeHead(500, { "Content-Type": "application/json" });
      response.end(JSON.stringify({ error: error.message }));
    });
  });
  await new Promise((done, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", done);
  });
  base = `http://127.0.0.1:${server.address().port}`;
  t.after(async () => {
    server.closeAllConnections();
    await new Promise((done) => server.close(done));
  });
  return { base, states, publishes, requests, uploads, tickets };
}

const publish = (checkout, remote, options = {}) => publishRelease({
  root: checkout.root, owner: OWNER, token: TOKEN, registry: remote.base,
  timeoutMs: 60_000, pollMs: 1, ...options,
});

test("publishes every skill at the repository version, waits for scans, and retries without uploads", async (t) => {
  const checkout = await release(t, ["alpha", "beta"]);
  const alpha = join(checkout.root, "skills", "alpha");
  await mkdir(join(alpha, "references"));
  await writeFile(join(alpha, "references", "guide.md"), "A supporting file\n");
  await writeFile(join(alpha, ".clawhubignore"), "private.txt\n");
  await writeFile(join(alpha, "private.txt"), "Ignored credentials\n");
  await writeFile(join(alpha, ".hidden"), "Hidden file\n");
  await writeFile(join(alpha, "SKILL-CARD.md"), "Local generated card\n");
  await symlink("SKILL.md", join(alpha, "linked.md"));
  await checkout.commit();
  await checkout.git("tag", "--force", `v${VERSION}`);
  checkout.sha = await checkout.git("rev-parse", "HEAD");
  const remote = await registry(t, { historicalMatch: true });

  await publish(checkout, remote);

  assert.equal(remote.publishes.length, 2, "explicit repository version publishes even content found in 1.2.2");
  assert.deepEqual(remote.publishes.map((body) => body.slug), ["alpha", "beta"]);
  assert.deepEqual(remote.publishes[0].files.map((entry) => entry.path).sort(), ["SKILL.md", "references/guide.md"]);
  for (const body of remote.publishes) {
    assert.equal(body.version, VERSION);
    assert.equal(body.source.commit, checkout.sha);
    assert.equal(body.source.ref, `refs/tags/v${VERSION}`);
    assert.equal(body.source.path, `skills/${body.slug}`);
    assert.deepEqual(body.tags, ["latest"]);
    assert.equal(remote.states.get(body.slug).kind, "published", "a pending upload must not count as success");
  }
  const uploadCount = remote.uploads.size;
  await publish(checkout, remote);
  assert.equal(remote.publishes.length, 2);
  assert.equal(remote.uploads.size, uploadCount, "same-version retry must skip matching source hashes");
});

test("checks all existing versions for conflicts before publishing a missing skill", async (t) => {
  const checkout = await release(t, ["alpha", "zeta"]);
  const remote = await registry(t, { states: new Map([
    ["zeta", { kind: "published", files: [file("SKILL.md", "Conflicting content")] }],
  ]) });
  await assert.rejects(publish(checkout, remote), /already contains different files/);
  assert.equal(remote.publishes.length, 0);
  assert.equal(remote.uploads.size, 0);
});

test("resumes a retained pending version and verifies its hashes without resubmitting", async (t) => {
  const checkout = await release(t);
  const remote = await registry(t, { states: new Map([
    ["alpha", { kind: "pending", publishAfterReads: 2, files: checkout.files.get("alpha") }],
  ]) });
  await publish(checkout, remote);
  assert.equal(remote.publishes.length, 0);
  assert.equal(remote.states.get("alpha").kind, "published");
});

test("fails for blocked publication and for scans that never finish", async (t) => {
  for (const stage of ["blocked", "checks_failed", "pending_checks"]) {
    await t.test(stage, async (t) => {
      const checkout = await release(t);
      const remote = await registry(t, { states: new Map([
        ["alpha", { kind: "pending", stage, publishAfterReads: Infinity, files: checkout.files.get("alpha") }],
      ]) });
      await assert.rejects(publish(checkout, remote, { timeoutMs: 50 }), stage === "pending_checks" ? /Timed out waiting/ : new RegExp(`publication ${stage}`));
      assert.equal(remote.publishes.length, 0);
    });
  }
});

test("does not mistake authentication or read failures for an absent version", async (t) => {
  for (const status of [401, 403, 429, 500]) {
    await t.test(`HTTP ${status}`, async (t) => {
      const checkout = await release(t);
      const remote = await registry(t, { readStatus: status });
      await assert.rejects(publish(checkout, remote), status === 403 ? /Cannot read/ : (error) => error.status === status);
      assert.equal(remote.publishes.length, 0);
      assert.equal(remote.uploads.size, 0);
    });
  }
});

test("recovers from a transient rate limit while checking an existing version", async (t) => {
  const checkout = await release(t);
  let attempts = 0;
  const remote = await registry(t, {
    states: new Map([["alpha", { kind: "published", files: checkout.files.get("alpha") }]]),
    readStatus: () => ++attempts === 1 ? 429 : undefined,
  });
  await publish(checkout, remote);
  assert.ok(attempts >= 2);
  assert.equal(remote.publishes.length, 0);
});

test("rejects missing publisher credentials before making requests", async () => {
  await assert.rejects(publishRelease({ root: "/missing", owner: "", token: TOKEN }), /CLAWHUB_OWNER/);
  await assert.rejects(publishRelease({ root: "/missing", owner: OWNER, token: "" }), /CLAWHUB_TOKEN/);
});

test("rejects dirty skills and a checkout that has moved beyond its release tag", async (t) => {
  const checkout = await release(t);
  const remote = await registry(t);
  await writeFile(join(checkout.root, "skills", "alpha", "SKILL.md"), "Unreleased edit\n");
  await assert.rejects(publish(checkout, remote), /clean release checkout/);
  await checkout.commit();
  await assert.rejects(publish(checkout, remote), /HEAD does not match the release tag/);
  assert.equal(remote.requests.length, 0);
});

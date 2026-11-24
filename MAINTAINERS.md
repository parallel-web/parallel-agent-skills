# Maintainers

Setup notes for people working on this repo (not consumers installing the plugin).

## Dev environment

### With Nix + direnv (recommended)

Add a `.envrc` with the following contents:

```
use flake;
```

Then run:

```
direnv allow
pre-commit install
```

## Pre-commit hooks

Markdown files are linted with [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) via [pre-commit](https://pre-commit.com/). Config lives in `.pre-commit-config.yaml` and `.markdownlint.yaml`.

Install the git hook once per clone:

```bash
pre-commit install
```

Run against all files (useful after pulling or changing the config):

```bash
pre-commit run --all-files
```

## CDN build

The live catalog at `skills.parallel.ai` is generated from `skills/` on every push to `main`.

Install JS tooling once per clone:

```bash
corepack enable
pnpm install
```

Build it locally with:

```bash
pnpm build
```

Preview the generated site locally with:

```bash
pnpm run dev
```

This writes the deployable Worker assets to `dist/` and serves them at `http://127.0.0.1:8000` during preview.

For local Wrangler deploys or other direct Wrangler commands, set these system environment variables in your shell or `.env` file:

```bash
export CLOUDFLARE_ACCOUNT_ID=<your-account-id>
export CLOUDFLARE_API_TOKEN=<your-api-token>
```

The repo intentionally does not hardcode `account_id` in `wrangler.json`; CI passes it via secrets and local maintainers should provide it via environment variables.

## Deploy + release flow

### Normal change

For ordinary skill/content/code changes:

1. Open a PR to `main`
2. CI validates pre-commit, CDN generation, and archive generation
3. Merge to `main`
4. `Deploy CDN` publishes the latest live catalog to `skills.parallel.ai`

This updates the live `main` channel only. No tag or GitHub Release is created.

### Versioned release

Releases are repo-wide semver tags backed by GitHub Release archives.

1. Start from a clean, up-to-date `main` branch:
   ```bash
   git switch main
   git pull --ff-only
   gh auth status # or: gh auth login
   ```
2. Run the local release PR helper with `patch`, `minor`, or `major`:
   ```bash
   pnpm run release:pr -- --part patch
   ```
3. Review the generated PR and merge it to `main`
4. Automation will then:
   - bump the shared repo version in all required manifests
   - create the corresponding git tag
   - publish per-skill zip files to GitHub Releases
   - refresh `skills.parallel.ai` metadata so `versions.json` and `index.json` include the new release
   - publish every skill to ClawHub at that same version, when ClawHub is configured

The helper script is the canonical maintainer flow for opening release PRs locally: it bumps the version, creates and pushes `release/vX.Y.Z`, and opens the PR via `gh`.

Live CDN content always tracks `main`. Immutable archives are published only for tagged releases.

Per-skill archive downloads at `https://skills.parallel.ai/archives/<skill>/<version>.zip` do not live in Cloudflare storage. The Worker in `src/worker.js` treats `/archives/...` as a redirect route and sends users to the matching GitHub Release asset URL. Those zip files are created during the **Publish release archives** workflow by `pnpm run build:archives`, uploaded to the GitHub Release as per-skill assets, and then exposed through the stable CDN redirect path. This is separate from GitHub's automatic repo snapshot zips like `https://github.com/<owner>/<repo>/archive/refs/tags/vX.Y.Z.zip`, which are whole-repo tag archives rather than per-skill release assets.

The automated bump updates these files:

- `VERSION`
- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `metadata.version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`
- `.codex-plugin/plugin.json` → `version`
- `plugins/antigravity/parallel/plugin.json` → `version`

If you ever need to bootstrap or recover a tag for the current `VERSION`, run the **Create release tag** workflow manually.

### Workflows overview

- **Validate PR**: runs on PRs to `main`; executes pre-commit and validates site/archive builds
- **Deploy CDN**: runs on pushes to `main`; deploys the live catalog
- **pnpm run release:pr**: local helper that bumps semver, pushes `release/v*`, and opens the release PR
- **Create release tag**: creates `vX.Y.Z` at the merged release commit (or the manually selected commit) and saves the immutable release reference as an artifact
- **Publish release archives**: builds per-skill zip files from that reference, uploads them to the GitHub Release, refreshes CDN metadata, then publishes the same release to ClawHub when configured

### ClawHub setup

ClawHub publishing is enabled by the repository variable `CLAWHUB_OWNER`. Until
that variable is set, the ClawHub job is skipped and existing releases continue.
Publishing needs a `CLAWHUB_TOKEN` Actions secret whose account can publish for
that owner. Set the secret before enabling the variable.

From this repository, install the pinned publishing tools and sign in:

```bash
pnpm install --frozen-lockfile
pnpm exec clawhub login --label parallel-agent-skills-releases
pnpm exec clawhub whoami
```

Create an organization publisher, replacing `parallel` with the handle you want:

```bash
pnpm exec clawhub publisher create parallel --display-name "Parallel"
```

If the publisher already exists, use an account with publishing access to it.
Creating a ClawHub publisher does not automatically link or verify a GitHub
organization. If your brand's handle is taken or reserved, use ClawHub's
[Org / Namespace Claim form](https://github.com/openclaw/clawhub/issues/new?template=org-namespace-claim.yml).

Save the signed-in account's token directly to GitHub, then enable publishing:

```bash
gh auth status
pnpm exec clawhub token | gh secret set CLAWHUB_TOKEN --repo parallel-web/parallel-agent-skills
gh variable set CLAWHUB_OWNER --body parallel --repo parallel-web/parallel-agent-skills
```

You can instead create a dedicated API token in ClawHub Settings → API tokens
and enter it through GitHub Settings → Secrets and variables → Actions. Keep
the token out of commits and shell history. Rotate or revoke it in ClawHub when
maintainer access changes.

ClawHub releases skills under **MIT-0**, which does not require attribution;
this repository uses MIT. Enabling publishing authorizes the CLI to accept
ClawHub's license terms for the uploaded skills. See the
[skill license rules](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md#license).

After this automation is merged, publish the current version once by running:

```bash
gh workflow run create-tag.yml --ref main --repo parallel-web/parallel-agent-skills
```

This reuses an existing `v<VERSION>` tag, or creates it if missing. The workflow
publishes the tag's original content. Future release PRs use the same automation;
ordinary merges do not create ClawHub releases. No dry-run publishing is required.

### ClawHub versions and recovery

Every directory under `skills/` containing `SKILL.md` receives the exact repo
release version, including skills whose contents have not changed. For example,
repository tag `v0.12.0` publishes every skill as `0.12.0`. Supporting files are
included using the pinned ClawHub CLI's file selection rules. Source attribution
records this repository, the exact commit, the tag, and each skill's path.

ClawHub publishes individual skills, not the plugin's MCP server configuration.
Installing a skill alone does not install the Claude or Codex plugin.

The job checks file hashes for existing versions before uploading. Matching
versions are skipped; conflicting content at the same version fails the job.
It waits up to 20 minutes for submitted versions to pass ClawHub checks and
verifies their published hashes before reporting success. Pending or blocked
uploads do not count as published. Deleted local skills are not deleted from
ClawHub.

If a publish fails, fix credentials or inspect the named skill/version in
ClawHub, then rerun the failed jobs in **Publish release archives**. Already
published skills are verified and skipped. Retained pending uploads are checked
again without resubmitting their version. A version conflict requires a new
repository release. If the release-reference artifact has expired, rerun
**Create release tag** to reconstruct it from the existing tag.

### ClawHub trusted publishing

ClawHub currently supports GitHub OIDC trusted publishing for **packages**, but
not individual **skills**. This integration therefore needs `CLAWHUB_TOKEN`.
See the [skill workflow documentation](https://github.com/openclaw/clawhub/blob/main/docs/cli.md#github-actions-1).

Organization trust and the official publisher badge are separate from OIDC.
Self-serve organization creation does not grant either status. Contact
[ClawHub support](https://community.openclaw.ai) to request publisher trust or
verification review. Include the publisher handle, `https://parallel.ai`, the
GitHub organization and this repository, plus public evidence that you control
them. ClawHub staff decide whether to grant that status; it does not remove the
skill API-token requirement.

### Useful local commands

```bash
# bump VERSION + plugin manifests locally
pnpm run release:bump -- --part patch

# create and open a release PR locally
pnpm run release:pr -- --part patch

# build GitHub Release zip archives for a specific version
pnpm run build:archives -- --version 0.3.2 --output release-assets
```

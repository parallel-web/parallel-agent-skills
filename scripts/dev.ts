#!/usr/bin/env node
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { join, normalize, resolve } from "node:path";

import { buildSite, REPO_ROOT } from "./site-lib.ts";

const contentTypes: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".zip": "application/zip",
};

function getArg(flag: string, defaultValue: string): string {
  const args = process.argv.slice(2);
  const index = args.indexOf(flag);
  return index >= 0 && args[index + 1] ? args[index + 1]! : defaultValue;
}

function hasFlag(flag: string): boolean {
  return process.argv.slice(2).includes(flag);
}

function extname(path: string): string {
  const index = path.lastIndexOf(".");
  return index >= 0 ? path.slice(index) : "";
}

async function main(): Promise<void> {
  const outputDir = resolve(REPO_ROOT, getArg("--output", "dist"));
  const port = Number.parseInt(getArg("--port", "4000"), 10);
  const host = getArg("--host", "127.0.0.1");

  if (!hasFlag("--no-build")) {
    buildSite(outputDir);
  }

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${host}:${port}`);
    const pathname = decodeURIComponent(
      url.pathname === "/" ? "/index.html" : url.pathname,
    );
    const candidatePath = resolve(outputDir, `.${normalize(pathname)}`);

    if (!candidatePath.startsWith(outputDir)) {
      response.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Forbidden");
      return;
    }

    const filePath =
      existsSync(candidatePath) && statSync(candidatePath).isFile()
        ? candidatePath
        : existsSync(join(candidatePath, "index.html"))
          ? join(candidatePath, "index.html")
          : null;

    if (!filePath) {
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Not found");
      return;
    }

    response.writeHead(200, {
      "Content-Type":
        contentTypes[extname(filePath)] ?? "application/octet-stream",
    });
    createReadStream(filePath).pipe(response);
  });

  server.listen(port, host, () => {
    console.log(`Serving ${outputDir} at http://${host}:${port}`);
  });
}

void main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});

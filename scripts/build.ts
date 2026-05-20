#!/usr/bin/env node
import { resolve } from "node:path";

import { buildArchives, buildSite, REPO_ROOT } from "./site-lib.ts";

function usage(): never {
  console.error("Usage: tsx scripts/build.ts <site|archives> [options]");
  process.exit(1);
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);

  if (command === "site") {
    const outputIndex = args.indexOf("--output");
    const output = outputIndex >= 0 ? args[outputIndex + 1] : "dist";
    buildSite(resolve(REPO_ROOT, output));
    return;
  }

  if (command === "archives") {
    const versionIndex = args.indexOf("--version");
    if (versionIndex === -1 || !args[versionIndex + 1]) usage();
    const outputIndex = args.indexOf("--output");
    const output = outputIndex >= 0 ? args[outputIndex + 1] : "release-assets";
    await buildArchives(resolve(REPO_ROOT, output), args[versionIndex + 1]!);
    return;
  }

  usage();
}

void main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});

#!/usr/bin/env node
import { bumpVersion } from "./site-lib.ts";

function usage(): never {
  console.error("Usage: tsx scripts/release.ts bump-version --part <patch|minor|major>");
  process.exit(1);
}

function main(): void {
  const [command, ...args] = process.argv.slice(2);
  if (command !== "bump-version") usage();

  const partIndex = args.indexOf("--part");
  const part = partIndex >= 0 ? args[partIndex + 1] : undefined;
  if (part !== "patch" && part !== "minor" && part !== "major") usage();

  console.log(bumpVersion(part));
}

main();

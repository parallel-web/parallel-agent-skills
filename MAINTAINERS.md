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

The helper script is the canonical maintainer flow for opening release PRs locally: it bumps the version, creates and pushes `release/vX.Y.Z`, and opens the PR via `gh`.

Live CDN content always tracks `main`. Immutable archives are published only for tagged releases.

Per-skill archive downloads at `https://skills.parallel.ai/archives/<skill>/<version>.zip` do not live in Cloudflare storage. The Worker in `src/worker.js` treats `/archives/...` as a redirect route and sends users to the matching GitHub Release asset URL. Those zip files are created during the **Publish release archives** workflow by `pnpm run build:archives`, uploaded to the GitHub Release as per-skill assets, and then exposed through the stable CDN redirect path. This is separate from GitHub's automatic repo snapshot zips like `https://github.com/<owner>/<repo>/archive/refs/tags/vX.Y.Z.zip`, which are whole-repo tag archives rather than per-skill release assets.

The automated bump updates these files:

- `VERSION`
- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `metadata.version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`
- `.codex-plugin/plugin.json` → `version`

If you ever need to bootstrap or recover a tag for the current `VERSION`, run the **Create release tag** workflow manually.

### Workflows overview

- **Validate PR**: runs on PRs to `main`; executes pre-commit and validates site/archive builds
- **Deploy CDN**: runs on pushes to `main`; deploys the live catalog
- **pnpm run release:pr**: local helper that bumps semver, pushes `release/v*`, and opens the release PR
- **Create release tag**: creates `vX.Y.Z` after a merged release PR (or manually)
- **Publish release archives**: builds per-skill zip files, uploads them to the GitHub Release, and refreshes CDN metadata

### Useful local commands

```bash
# bump VERSION + plugin manifests locally
pnpm run release:bump -- --part patch

# create and open a release PR locally
pnpm run release:pr -- --part patch

# build GitHub Release zip archives for a specific version
pnpm run build:archives -- --version 0.3.2 --output release-assets
```

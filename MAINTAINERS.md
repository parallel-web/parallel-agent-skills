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

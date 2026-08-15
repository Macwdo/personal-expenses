---
name: pingou-feature-env
description: Sets up isolated Pingou feature work with native Git worktrees plus a dedicated root .env.<feature> stack - picking the owning child repository, creating one branch and worktree per affected repo under .worktrees/, pointing BACKEND_PATH/FRONTEND_PATH/LANDING_PATH/CHAT_PATH at those checkouts, splitting work between parallel workers, and validating before integration. Use when starting any feature, bug fix, or refactor in /home/macwdo/Codes/pingou-o-que that needs its own branch, worktree, parallel agents, or a running stack.
---

# Pingou Feature Environment

Every feature gets its own branch, its own worktree in each owning repository,
and its own root environment file. Follow the steps in order.

## Use this skill when

- The user asks to start a feature, fix, or refactor and no dedicated branch or
  worktree exists yet.
- The user asks to work on more than one application at once.
- The user asks to run parallel agents or split work between workers.
- The user asks for an isolated stack for work in progress.

Do not use it for pure inspection or questions, for operating an environment
that already exists (`$pingou-env`), or for merging finished work
(`$merge-work`).

## Checklist

Copy this and keep it updated while working:

```
Feature setup:
- [ ] 1. Identify owning repositories
- [ ] 2. Audit each repository
- [ ] 3. Create branch + worktree per owning repository
- [ ] 4. Create .env.<feature>
- [ ] 5. Point *_PATH at the worktrees
- [ ] 6. Start and verify the stack
- [ ] 7. Assign ownership slices
- [ ] 8. Validate, commit, hand off
```

## 1. Identify owning repositories

| Change | Owning repository |
| --- | --- |
| Django, DRF, models, migrations, Celery, `apps/ai`, fixtures | `pingou-o-que-backend` |
| Authenticated product UI, chat UI, tables, `lib/api/*`, stores | `pingou-o-que-frontend` |
| Public marketing pages, CRM lead form | `pingou-o-que-landing-page` |
| Go SSE relay, Redis stream reader | `pingou-o-que-chat` |
| Compose, Makefile, `tools/dev/*`, workspace docs, submodule pointers | parent `pingou-o-que` |

A backend contract change plus its UI is two repositories, so it needs two
worktrees. Never implement child application code from a parent worktree.

## 2. Audit each repository

For every owning repository:

```bash
git -C <repository> status --short --branch
git -C <repository> worktree list
```

Stop and ask the user before continuing if the primary checkout is dirty in a
way that conflicts with the new work. Never stash, reset, or discard changes you
did not create.

## 3. Create branch + worktree per owning repository

Use the existing layout: worktrees live under `.worktrees/` inside the
repository that owns them.

```bash
# child repository
git -C <child-repository> worktree add \
  /home/macwdo/Codes/pingou-o-que/<child-repository>/.worktrees/<feature-slug> \
  -b <feature-branch>

# parent repository (workspace-owned work only)
git -C /home/macwdo/Codes/pingou-o-que worktree add \
  /home/macwdo/Codes/pingou-o-que/.worktrees/pingou-o-que/<feature-slug> \
  -b <feature-branch>
```

Rules:

- `<feature-slug>` is the branch name with `/` replaced by `-`.
- If the branch already exists, drop `-b` and pass the branch name as the last
  argument.
- Keep worktree directories out of commits. If `.worktrees/` is not ignored in
  that repository, add it to `<repository>/.git/info/exclude` rather than
  editing a tracked `.gitignore`.
- A parent worktree needs `git submodule update --init --recursive` before it
  can build anything.

## 4. Create `.env.<feature>`

From the workspace root:

```bash
make env-init ENV_FILE=.env.<feature> ENV_NAME=<feature>
```

`env-init` refuses to overwrite an existing file and derives a unique Compose
project name and Portless namespace, so this stack cannot collide with `.env` or
with another feature.

## 5. Point `*_PATH` at the worktrees

Edit only the lines for repositories this feature changes:

```dotenv
BACKEND_PATH=/home/macwdo/Codes/pingou-o-que/pingou-o-que-backend/.worktrees/<feature-slug>
FRONTEND_PATH=/home/macwdo/Codes/pingou-o-que/pingou-o-que-frontend/.worktrees/<feature-slug>
LANDING_PATH=/home/macwdo/Codes/pingou-o-que/pingou-o-que-landing-page/.worktrees/<feature-slug>
CHAT_PATH=/home/macwdo/Codes/pingou-o-que/pingou-o-que-chat/.worktrees/<feature-slug>
```

Leave every unaffected path on its default submodule checkout. Ask the user for
the API key required by `AI_CHAT_MODEL` if the feature touches chat; never print
or commit the file.

## 6. Start and verify the stack

Run `$pingou-env` against `.env.<feature>`, which is equivalent to:

```bash
make config ENV_FILE=.env.<feature>
make up ENV_FILE=.env.<feature>
make urls ENV_FILE=.env.<feature>
```

Confirm in `make config` output that each service builds from the intended
worktree path before spending time on a full build.

## 7. Assign ownership slices

When several agents or people work in parallel:

- one worktree per worker, never shared;
- a bounded slice per worker, stated as repository plus directories or files;
- one integration environment file shared by the whole feature.

Record who owns what before any of them starts editing.

## 8. Validate, commit, hand off

Validate inside each owning repository:

```bash
# backend
uv run ruff check . && uv run ruff format --check . && uv run pytest

# frontend / landing
bun run typecheck && bun run lint && bun run build

# chat
go build ./... && go vet ./... && go test ./...
```

Commit in the child repositories first. Only after those commits exist may the
parent record new submodule pointers, in its own commit.

Hand off with a table of repository, branch, absolute worktree path, ownership
slice, validation result, and commit SHA, plus the environment file name. Merge
finished worktrees with `$merge-work`.

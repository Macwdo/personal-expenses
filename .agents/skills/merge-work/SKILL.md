---
name: merge-work
description: Merge every linked git worktree into main (or master) and push. Use when the user asks for merge-work, to merge all worktrees, integrar worktrees na main, or push completed feature worktrees in the Pingou workspace.
---

# Merge Work

Merge **all** linked worktrees into each repository's default base branch and push that branch. Do this across the Pingou parent repo and every child repo that has worktrees.

The user intent is: merge every worktree into `main` and push.

## Repositories

Run the workflow independently in each Git repository.

| Repository | Typical base branch |
| --- | --- |
| `pingou-o-que` (parent) | `main` |
| `pingou-o-que-backend` | `main` |
| `pingou-o-que-frontend` | `main` |
| `pingou-o-que-landing-page` | `main` |
| `pingou-o-que-chat` | `master` |

Detect the base branch from `origin/HEAD`. Fall back to local `main`, then `master`. Never assume every repo uses `main`.

## Workflow

Copy this checklist and keep it updated:

```
Merge Work:
- [ ] Audit worktrees
- [ ] Merge children
- [ ] Push children
- [ ] Merge parent worktrees
- [ ] Update parent submodule pointers if children moved
- [ ] Push parent
- [ ] Report
```

### 1. Audit first

From the workspace root:

```bash
python3 .agents/skills/merge-work/scripts/list_worktrees.py
```

Also run inside each child that might have worktrees:

```bash
cd <child-repo>
git worktree list
git status --short --branch
```

Treat the first path from `git worktree list` as the primary checkout. Only linked worktrees are merge sources.

### 2. Merge children before the parent

For each child repository, on its **primary** checkout:

1. Stop if the primary checkout is dirty. Do not stash, reset, or discard.
2. Fetch `origin`.
3. Fast-forward the base branch to `origin/<base>` when possible. Stop if it diverged.
4. For each linked worktree marked `merge-and-push`:
   - Skip `skip-dirty` (uncommitted work in that worktree).
   - Skip `skip-detached`.
   - Skip `already-merged` (no merge needed).
   - For `prune`, run `git worktree prune` after reporting; do not merge a missing directory.
   - Merge from the primary checkout:

     ```bash
     git checkout <base-branch>
     git merge --no-edit <feature-branch>
     ```

   - Stop immediately on conflict. Leave the merge in progress and report the files. Do not `--abort` unless the user asks.
5. After all successful merges in that repo:

   ```bash
   git push origin <base-branch>
   ```

Do not `--force` or `--force-with-lease` to `main`/`master`. Do not skip hooks.

### 3. Parent last

Repeat the same merge+push steps for parent-linked worktrees.

If any child base branch moved, update that child's submodule pointer on the parent in a separate parent commit, then push parent `main`. Do not mix submodule pointer updates with unrelated parent dirty files.

### 4. Report

For each repository list:

- merged branches
- pushed ref
- skipped (dirty / detached / already merged / missing)
- failed (conflict or push error)

Do not remove worktrees or delete branches. That is `$cleanup-worktrees`.

## Safety

- Merge into the detected base branch only. Push that branch only.
- One repository at a time. One feature branch at a time.
- Preserve unrelated dirty files.
- Do not merge from a parent-only worktree into child application history.
- Do not rebase interactively.
- If commit, merge, or push fails, stop, report, and leave the worktree intact.

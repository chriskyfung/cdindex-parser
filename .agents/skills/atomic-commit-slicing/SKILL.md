---
name: atomic-commit-slicing
description: Re-slice work into atomic Conventional Commits that each build and pass. Use whenever the user wants to fix git history, split a big commit, or make atomic commits. Make sure to use this skill whenever the user mentions re-slicing commits, atomic commits, fixing git history, or splitting commits, even if they don't explicitly mention Conventional Commits or per-commit verification.
---

# atomic-commit-slicing

Re-slice a large commit or branch into atomic, independently-green Conventional Commits. Each commit must build, import, and pass tests on its own. This skill captures the commit-slicing methodology used during the `cdindex2-parser` restructure (16 atomic commits from `main` → `test/core`).

---

## When to use

- "Re-slice commits"
- "Atomic commits"
- "Fix git history"
- "Split commits"
- "Make commits atomic"
- "Clean up commit history"

---

## Core principle

**Atomic commit:** One logical change per commit. Each commit must be:
1. **Self-contained** — builds, imports, passes tests independently
2. **Revertable** — `git revert <sha>` produces a working state
3. **Bisectable** — `git bisect` lands on a working commit
4. **Reviewable** — small enough to review in one sitting

---

## Step 1: Audit the current state

Identify what needs re-slicing:

```bash
# See current branch commits
git log --oneline main..HEAD

# See what's changed vs main
git diff main..HEAD --stat

# Check working tree is clean
git status --short
```

**Pitfall:** Never re-slice commits that have already been pushed to a shared branch unless you coordinate with all collaborators (force-push rewrites history).

---

## Step 2: Plan commit boundaries

Before touching code, plan the commit sequence. Each commit should represent one logical change:

Example plan for a package restructure:

1. `chore(repo): add .gitattributes, fix .gitignore, add pre-commit config`
2. `build!: adopt src layout, PEP 639 license, repair console script`

---

## Step 3: Reset to base branch

Reset the working tree to the base commit (keeping changes in working tree):

```bash
git checkout main
git checkout -b re-slice/atomic-commits
git reset --soft main   # moves HEAD to main, keeps all changes staged
git reset               # unstages all changes (working tree intact)
```

Now all changes are unstaged in the working tree. You'll re-commit them atomically.

**Pitfall:** `git reset --soft` keeps changes staged; `git reset` (mixed, default) unstages. Use mixed reset to start fresh.

**Pitfall:** Never `git reset --hard` unless you're sure you don't need the changes.

---

## Step 4: Stage and commit atomically

For each planned commit:

1. Stage only the files for that commit:
   ```bash
   git add <specific-files>
   ```

2. Verify staged changes:
   ```bash
   git diff --cached --stat
   ```

3. Commit with Conventional Commit format:
   ```bash
   git commit -m "type(scope): subject"
   ```

4. Verify the commit is green:
   ```bash
   ruff check src/ tests/ && ruff format --check src/ tests/ && mypy src && pytest tests/
   ```

5. If verification fails, fix and amend:
   ```bash
   git add <fixed-files>
   git commit --amend --no-edit
   ```

**Pitfall:** Use `git add -p` (patch mode) to stage only parts of a file when a file contains changes for multiple commits.

**Pitfall:** Always verify after each commit. A red commit breaks `git bisect`.

---

## Step 5: Verify each commit independently

After all commits are made, verify each one:

```bash
# Check each commit builds and tests pass
git rebase --exec "pytest tests/ -q" main..HEAD

# Or check individually
git log --oneline main..HEAD | while read hash msg; do
  git checkout $hash
  pytest tests/ -q || echo "FAILED: $hash"
done
git checkout HEAD
```

**Pitfall:** `git rebase --exec` runs a command after each commit. If any fails, the rebase stops.

**Pitfall:** Don't skip verification — a single bad commit invalidates the entire slice.

---

## Step 6: Verify commit messages

Check Conventional Commit format:

```bash
git log --format="%s" main..HEAD
```

Each subject should:
- Start with a type (`feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `build`, `chore`, `style`, `perf`, `revert`)
- Optionally have a scope in parentheses
- Be imperative mood, lowercase, no trailing period
- Be ≤ 72 characters

**Pitfall:** Breaking changes need `!` after type/scope and a `BREAKING CHANGE:` footer.

---

## Step 7: Push and merge

Push the re-sliced branch:

```bash
git push origin re-slice/atomic-commits
```

Then open a PR and merge per policy:
- `refactor/*`, `test/*`: rebase merge
- `chore/*`, `ci/*`, `docs/*`: squash merge

**Pitfall:** After merging, delete the branch:
```bash
git push origin --delete re-slice/atomic-commits
git branch -d re-slice/atomic-commits
```

---

## Common anti-patterns

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| One giant "refactor everything" commit | Unreviewable, unbisectable | Split into atomic commits |
| Mixing formatting with logic changes | Hides the actual change | Separate `style` commit first |
| Committing with red tests | Breaks `git bisect` | Fix before committing |
| `git add .` (everything at once) | Hard to split later | Use `git add -p` or explicit paths |
| `WIP` / `fixup` on shared branch | Confuses reviewers | Squash locally before push |

---

## Verification checklist

Before declaring the slice complete:

- [ ] Every commit builds and imports
- [ ] Every commit passes tests
- [ ] Every commit follows Conventional Commit format
- [ ] No `WIP`, `fixup`, or `squash!` commits remain
- [ ] Working tree is clean
- [ ] Branch is pushed and ready for PR

---
name: python-release-pipeline
description: Set up GitHub Actions CI/CD for a Python package including lint/test matrix/build and trusted-publishing release. Use whenever the user wants CI, GitHub Actions, PyPI publishing, or a release workflow. Make sure to use this skill whenever the user mentions setting up CI, GitHub Actions, publishing to PyPI, or a release workflow, even if they don't explicitly ask for trusted publishing or OIDC.
---

# python-release-pipeline

Set up a complete GitHub Actions CI/CD pipeline for a Python package: CI matrix (lint + test + build), release workflow (TestPyPI → PyPI → GitHub Release via trusted publishing/OIDC), docs deploy, and Dependabot. This skill captures the full CI/CD automation implemented for `cdindex2-parser`.

---

## When to use

- "Set up CI"
- "GitHub Actions for Python"
- "Publish to PyPI"
- "Release workflow"
- "Trusted publishing / OIDC"
- "Automate releases"

---

## Prerequisites

- Python package with `pyproject.toml`, `src/` layout, console script
- GitHub repository with write access
- PyPI account with ability to create pending publishers (for trusted publishing)

---

## Step 1: Create CI workflow (`.github/workflows/ci.yml`)

Four jobs: `lint`, `test` (matrix), `build`, `ci-success` gate.

```yaml
name: CI

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint and type-check
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.13", cache: "pip" }
      - run: python -m pip install --upgrade pip
      - run: pip install -e ".[dev]"
      - run: ruff format --check .
      - run: ruff check .
      - run: mypy src

  test:
    name: Test on ${{ matrix.os }} / Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "${{ matrix.python-version }}", cache: "pip" }
      - run: python -m pip install --upgrade pip
      - run: pip install -e ".[dev]"
      - run: pytest --cov=cdindex2_parser --cov-branch --cov-report=xml --junitxml=junit.xml
      - uses: actions/upload-artifact@v7
        if: always()
        with:
          name: test-${{ matrix.os }}-${{ matrix.python-version }}
          path: [coverage.xml, junit.xml]

  build:
    name: Build and smoke-test wheel
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.13", cache: "pip" }
      - run: python -m pip install --upgrade pip build twine
      - run: python -m build
      - run: twine check dist/*
      - run: |
          python -m venv /tmp/venv
          /tmp/venv/bin/pip install dist/*.whl
          /tmp/venv/bin/cdindex2-parser --help
          /tmp/venv/bin/python -c "import cdindex2_parser; print(cdindex2_parser.__version__)"
        shell: bash
      - uses: actions/upload-artifact@v7
        with: { name: dist, path: dist/ }

  ci-success:
    name: CI success gate
    if: always()
    needs: [lint, test, build]
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: |
          [ "${{ needs.lint.result }}"  = "success" ] && \
          [ "${{ needs.test.result }}"  = "success" ] && \
          [ "${{ needs.build.result }}" = "success" ] || \
          (echo "CI failed" && exit 1)
```

**Pitfall:** The `ci-success` gate job is what branch protection requires. Matrix job names can change freely; only `ci-success` is referenced by protection rules.

**Pitfall:** Use `actions/checkout@v7` and `actions/setup-python@v7` (not v4/v5, which had been outdated).

**Pitfall:** `fail-fast: false` so one OS/Python combo failure doesn't cancel others.

---

## Step 2: Create release workflow (`.github/workflows/release.yml`)

Uses **trusted publishing (OIDC)** — no API tokens stored in GitHub Secrets.

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.13", cache: "pip" }
      - run: python -m pip install --upgrade pip build twine
      - name: Verify tag matches pyproject version
        run: |
          TAG="${GITHUB_REF_NAME#v}"
          VER=$(python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
          [ "$TAG" = "$VER" ] || { echo "tag $TAG != pyproject $VER"; exit 1; }
      - run: python -m build
      - run: twine check dist/*
      - uses: actions/upload-artifact@v7
        with: { name: dist, path: dist/ }

  publish-testpypi:
    name: Publish to TestPyPI
    needs: build
    runs-on: ubuntu-latest
    environment: testpypi
    permissions: { id-token: write }
    steps:
      - uses: actions/download-artifact@v7
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          skip-existing: true

  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment: pypi
    permissions: { id-token: write }
    if: ${{ !contains(github.ref_name, '-') }}
    steps:
      - uses: actions/download-artifact@v8
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    name: Create GitHub Release
    needs: publish-pypi
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: softprops/action-gh-release@v3
        with: { generate_release_notes: true }
```

**Pitfall:** Trusted publishing requires a one-time pending publisher setup on PyPI:
- Go to PyPI → Account settings → Pending publishers
- Add publisher for repo `{owner}/{repo}`, workflow `.github/workflows/release.yml`, environment `testpypi`
- Repeat for environment `pypi`

**Pitfall:** `if: ${{ !contains(github.ref_name, '-') }}` ensures PyPI (not TestPyPI only) only for non-prerelease tags.

**Pitfall:** Tag must match `pyproject.toml` `version` field — the build job verifies this.

---

## Step 3: Create docs deploy workflow (`.github/workflows/docs.yml`)

```yaml
name: Docs

on:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "src/**"
      - "mkdocs.yml"

permissions:
  contents: write

jobs:
  deploy:
    name: Deploy docs to GitHub Pages
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.13", cache: "pip" }
      - run: |
          python -m pip install --upgrade pip
          pip install -e ".[docs]"
      - run: mkdocs gh-deploy --force
```

**Pitfall:** GitHub Pages must be enabled in repository settings (Settings → Pages → Build and deployment → Source: GitHub Actions).

**Pitfall:** `permissions: contents: write` required for `mkdocs gh-deploy` to push to `gh-pages` branch.

---

## Step 4: Create Dependabot config (`.github/dependabot.yml`)

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
  - package-ecosystem: "pip"
    directory: "/"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
```

---

## Step 5: Configure branch protection on `main`

Use the GitHub API or web UI:

**Via `gh` CLI:**

```bash
# Restrict merge strategies
gh api -X PATCH repos/{owner}/{repo} --input - <<'JSON'
{
  "allow_merge_commit": false,
  "allow_squash_merge": true,
  "allow_rebase_merge": true,
  "delete_branch_on_merge": true,
  "squash_merge_commit_title": "PR_TITLE",
  "squash_merge_commit_message": "PR_BODY"
}
JSON

# Protect main branch
gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input - <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["ci-success"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```

**Pitfall:** `required_status_checks.contexts` must reference the `ci-success` gate job, not individual matrix job names (which can change).

**Pitfall:** `required_linear_history: true` enforces rebase/squash only — no merge commits.

---

## Step 6: Create pending publishers on PyPI (one-time manual step)

1. Log in to PyPI (pypi.org)
2. Go to Account settings → Pending publishers
3. Click "Add a pending publisher"
4. Fill in:
   - **PyPI project name:** `cdindex2-parser`
   - **Repository owner:** `chriskyfung`
   - **Repository name:** `cdindex2-parser`
   - **Workflow filename:** `.github/workflows/release.yml`
   - **Environment:** `testpypi`
5. Click "Add a pending publisher"
6. Repeat for environment `pypi`

**Pitfall:** Without pending publishers, trusted publishing will fail with a 403. This is a one-time manual setup.

---

## Step 7: Verify the pipeline

1. Push a test tag:
   ```bash
   git tag -a v0.3.0 -m "Release 0.3.0"
   git push origin v0.3.0
   ```

2. Check GitHub Actions tab — all jobs should pass:
   - CI → lint, test (matrix), build, ci-success
   - Release → build, publish-testpypi, publish-pypi, github-release

3. Verify on PyPI:
   ```bash
   pip install cdindex2-parser
   cdindex2-parser --help
   ```

**Pitfall:** If the tag doesn't match `pyproject.toml` version, the build job fails. Fix version mismatch and retag.

**Pitfall:** TestPyPI and PyPI are separate indexes. A package published to TestPyPI won't appear on PyPI until the `publish-pypi` job runs.

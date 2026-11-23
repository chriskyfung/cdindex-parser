---
name: python-docs-setup
description: Set up MkDocs documentation site with API reference, GitHub Pages deployment, and docs workflow. Use whenever the user wants documentation, docs site, MkDocs, mkdocstrings, or GitHub Pages deployment for a Python project. Make sure to use this skill whenever the user mentions documentation, docs site, MkDocs, mkdocstrings, or GitHub Pages deployment for a Python project, even if they don't explicitly ask for all of these.
---

# python-docs-setup

Set up a MkDocs Material documentation site with auto-generated API reference via mkdocstrings, GitHub Pages deployment via GitHub Actions, and docs CI workflow. This skill captures the docs setup implemented for `cdindex-parser`.

---

## When to use

- "Set up documentation"
- "Add MkDocs documentation site"
- "Deploy docs to GitHub Pages"
- "Add mkdocstrings API reference"
- "Setup docs CI/CD"

---

## Prerequisites

- Python package with `src/` layout and public API
- `mkdocs-material` and `mkdocstrings[python]` installed
- GitHub repository with `pages` enabled in settings
- `mkdocs` installed

---

## Step 1: Create mkdocs.yml

```yaml
site_name: <project-name>
site_description: <short description>
site_url: https://<username>.github.io/<repo>/
repo_url: https://github.com/<username>/<repo>
edit_uri: blob/main/docs/

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
    - scheme: slate
      primary: indigo
      accent: indigo
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.top
    - content.code.copy
    - content.code.annotate
    - search.suggest
    - search.highlight

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: false
            docstring_style: google
            merge_init_into_class: true
            show_root_heading: true
            show_root_full_path: false
            show_symbol_type_heading: true
            show_symbol_type_toc: true
            show_category_heading: true
            show_if_no_docstring: true
            docstring_section_style: list
            filters: ["!^_"]

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg

nav:
  - Home: index.md
  - Installation: installation.md
  - Usage: usage.md
  - File Format: file-format.md
  - API Reference: api.md
  - Troubleshooting: troubleshooting.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/<username>/<repo>
  version:
    provider: mike

copyright: Copyright © <year> <author>
```

---

## Step 2: Create documentation pages

Create these Markdown files in `docs/`:

### index.md — Homepage

Include:
- Project title and tagline
- Key features (bullet list)
- Quick start (install + CLI usage + library import)
- Navigation table linking to all pages
- License information

### installation.md — Installation guide

Include:
- PyPI installation (`pip install <package-name>`)
- Source installation (`git clone` + `pip install -e .`)
- Development extras (`pip install -e ".[dev,docs]"`)
- Python version requirement (>=3.10)

### usage.md — Usage guide

Include:
- CLI usage with all flags/options
- Output format examples (CSV/JSON)
- Python library usage with code examples
- Public API table

### file-format.md — File format specification

Document the input/output file formats with examples.

### api.md — API reference

Use mkdocstrings to auto-generate API reference:

```markdown
# API Reference

::: <package_name>.parse_catalog
::: <package_name>.Catalog
::: <package_name>.Entry
::: <package_name>.FileRecord
::: <package_name>.NameRecord

## Utilities

::: <package_name>.resolve_input_path
::: <package_name>.to_csv
::: <package_name>.to_json

## Exceptions

::: <package_name>.errors.<PackageName>Error
::: <package_name>.errors.<SpecificError>
```

### troubleshooting.md — Common issues

Document common issues and their solutions:
- Encoding issues
- Line count mismatch
- Indent mismatch
- Malformed records
- Missing files

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
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"
      - run: |
          python -m pip install --upgrade pip
          pip install -e ".[docs]"
      - run: mkdocs gh-deploy --force
```

**Pitfall:** GitHub Pages must be enabled in repository settings (Settings → Pages → Build and deployment → Source: GitHub Actions).

**Pitfall:** `permissions: contents: write` is required for `mkdocs gh-deploy` to push to `gh-pages` branch.

---

## Step 4: Verify docs build

```bash
pip install -e ".[docs]"
mkdocs build --strict
```

**Pass criteria:** "Documentation built in X seconds", exit code 0.

---

## Step 5: Commit atomically

Commit in logical steps:

1. `docs(mkdocs): add mkdocs.yml configuration`
2. `docs(home/install/usage): rewrite core documentation pages`
3. `docs(format/api/troubleshooting): rewrite format, API, and troubleshooting pages`
4. `docs(readme): add badges, docs links, and modern quick start`
5. `ci: add docs deploy workflow and Dependabot configuration`

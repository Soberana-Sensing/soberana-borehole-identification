# AGENTS.md — Soberana Borehole Identification

Rules for AI agents in this repo. Loaded every session that opens this directory.

## What this project is

Find and map water boreholes from free satellite data. Scaffold created 2026-11-17; no method or
results yet. When a plan exists it goes in `docs/PLAN.md` and binds.

## Order of attack

1. `~/.config/opencode/soberana-borehole-identification_MEMORY.md` (create on first durable fact)
2. `~/.config/opencode/pools/soberana-borehole-identification/` when it exists
3. `docs/` in this repo
4. Papers as extracted text only: `~/.config/opencode/tools/pdftext.py`. Never upload a PDF.

## Data

`data/raw/`, `data/interim/`, `data/derived/`. Contents git-ignored, folders tracked. Every dataset
reference carries its date: acquisition window, product epoch, or retrieval date. No bare data.

Check for `soberana-borehole-identification-venv/` before running Python. Never install into system
Python.

## Git

Public repo under the `Soberana-Sensing` org. No push, force-push, branch delete, or destructive git
without asking first. Commit messages: Conventional Commits, terse intent.

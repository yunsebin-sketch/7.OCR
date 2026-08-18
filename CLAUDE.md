# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A handwritten digit recognizer, developed as two independent implementations living side by side:

- **`desktop_version/`** — a Tkinter GUI app. See `desktop_version/CLAUDE.md` for commands and architecture.
- **`web_version/`** — a Flask-based browser app (canvas frontend + `/predict` API). See `web_version/CLAUDE.md` for commands and architecture.

Each subfolder is self-contained: its own venv, its own `requirements.txt`, its own `model.pkl`. There is no shared package or import between them — always read the relevant subfolder's `CLAUDE.md` before working inside it, since commands and structure differ between the two.

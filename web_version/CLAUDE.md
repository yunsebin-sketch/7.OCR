# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The web version of the handwritten digit recognizer: a browser page with an HTML `<canvas>` the user draws a digit on, backed by a Flask API that runs a scikit-learn model and returns a 0-9 prediction with confidence. This is the browser-accessible counterpart to `../desktop_version` (a Tkinter desktop app) — the two are independent implementations, not a shared codebase.

## Commands

All Python commands must use this folder's venv interpreter (`.venv`), not a global `python`. Run them with this folder (`web_version/`) as the working directory.

```powershell
# One-time environment setup (creates .venv, installs requirements.txt)
setup.bat

# Train the model — downloads MNIST via fetch_openml (~50MB, cached after first run),
# trains an MLPClassifier, writes model.pkl. ~15-30s to train once downloaded.
.venv\Scripts\python.exe train_model.py

# Run the dev server directly (for iterating on app.py) — http://127.0.0.1:5000
.venv\Scripts\python.exe app.py

# Double-click entry point: launches the server in its own console window,
# waits ~3s, then opens the default browser to it
웹앱_실행.bat
```

There is no lint/test suite in this project.

## Architecture

- **`train_model.py`** — identical in approach to `desktop_version/train_model.py`: fetches MNIST, trains an `MLPClassifier(hidden_layer_sizes=(128, 64))` on 28x28 flattened `[0,1]`-normalized pixel vectors, dumps to `model.pkl` via `joblib`. Re-run any time the model changes; `app.py` never trains, only loads at startup (and raises `FileNotFoundError` immediately if `model.pkl` is missing, rather than failing per-request).
- **`app.py`** — Flask app with two routes: `/` renders `templates/index.html`, `/predict` (POST) accepts `{"image": "<canvas dataURL>"}`, decodes the base64 PNG, and runs `preprocess()` before predicting. `preprocess()` deliberately mirrors `desktop_version/digit_recognizer.py`'s `recognize()` step for step (crop to drawn bounding box → pad to square with a margin so the digit isn't touching the edges → resize to 28x28 with `Image.LANCZOS` → normalize to `[0,1]`). **Keep these two preprocessing functions in sync** — if either drifts, predictions degrade silently rather than erroring.
- **`templates/index.html`** — single-file frontend (inline CSS/JS, no build step, no frontend framework). Canvas is black with white strokes (`BRUSH_SIZE = 16`) to match the polarity `preprocess()`/training expect. Uses Pointer Events (not separate mouse/touch handlers) so drawing works with mouse, touch, or pen. On "인식하기" it POSTs `canvas.toDataURL("image/png")` to `/predict` and renders the returned digit + confidence; on error it shows the server's error message (e.g. "먼저 숫자를 그려주세요." when the canvas is blank).

This folder is self-contained — its own `.venv`, `requirements.txt`, and `model.pkl`. It does not import from or share a model with `../desktop_version`; the two were trained separately (same method, different runs) and are not guaranteed to produce bit-identical predictions.

### Windows batch files: ASCII only

`웹앱_실행.bat` and `setup.bat` intentionally use plain ASCII/English messages, not Korean, even though the rest of the project (UI strings, docstrings, filenames) is Korean. Korean text inside `.bat` file bodies previously broke `cmd.exe`'s parsing in this project (misread `if not exist` checks, truncated later lines) regardless of `chcp 65001` — see `desktop_version/CLAUDE.md` for the original incident. Do not reintroduce non-ASCII text into `.bat` file bodies — only the filename itself is safe as Korean.

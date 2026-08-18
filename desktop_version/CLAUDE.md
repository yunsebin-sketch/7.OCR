# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The desktop version of the handwritten digit recognizer: a Tkinter GUI where the user draws a digit with the mouse and a scikit-learn model predicts 0-9. No web server, no build step — just two Python scripts and a pickled model, launched by double-clicking a `.bat` file on Windows.

## Commands

All Python commands must use this folder's venv interpreter (`.venv`), not a global `python`. Run them with this folder (`desktop_version/`) as the working directory.

```powershell
# One-time environment setup (creates .venv, installs requirements.txt)
setup.bat

# Train the model — downloads MNIST via fetch_openml (~50MB, cached after first run),
# trains an MLPClassifier, writes model.pkl. Takes roughly 15-30s to train once downloaded.
.venv\Scripts\python.exe train_model.py

# Run the GUI directly (for iterating on digit_recognizer.py)
.venv\Scripts\python.exe digit_recognizer.py

# Double-click entry point a user would launch from Explorer
숫자인식_실행.bat
```

There is no lint/test suite in this project.

## Architecture

Two-script pipeline sharing a serialized model file:

- **`train_model.py`** — offline/one-off. Fetches MNIST (`sklearn.datasets.fetch_openml("mnist_784", ...)`), trains an `MLPClassifier(hidden_layer_sizes=(128, 64))` on 28x28 flattened, [0,1]-normalized pixel vectors, and dumps it to `model.pkl` via `joblib`. Re-run this any time the model architecture or training data changes; `digit_recognizer.py` never trains, only loads.
- **`digit_recognizer.py`** — the GUI. Draws on a 280x280 Tkinter `Canvas` while mirroring every stroke onto a same-size Pillow `Image` (black background, white strokes — matches MNIST's polarity). On "인식하기" (recognize), it crops to the drawn bounding box, pads it back to square with a margin (so the digit isn't touching the edges, similar to how MNIST digits are centered), downsamples to 28x28 with `Image.LANCZOS`, flattens/normalizes it, and calls `model.predict` / `predict_proba` on `model.pkl`. **Keep this preprocessing in sync with whatever `train_model.py` feeds the model** — if one side's normalization or shape changes, predictions silently degrade rather than erroring.
- **`model.pkl`** — build artifact, not source. Safe to delete and regenerate via `train_model.py`; `숫자인식_실행.bat` auto-trains if it's missing.

This folder is self-contained — it does not import from or depend on `../web_version`. Any shared logic (e.g. the crop/pad/resize preprocessing) that eventually needs to match the web version must be kept in sync manually; there is no shared package between the two.

### Windows batch files: ASCII only

`숫자인식_실행.bat` and `setup.bat` intentionally use plain ASCII/English messages, not Korean, even though the rest of the project (UI strings, docstrings, filenames) is Korean. Korean text inside these `.bat` files previously broke `cmd.exe`'s parsing (misread `if not exist` checks, truncated later lines) regardless of `chcp 65001`. Do not reintroduce non-ASCII text into `.bat` file bodies — only the filename itself is safe as Korean.

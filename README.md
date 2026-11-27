# Hyperscript

**Hyperscript** is a **visual narrative map editor** designed for modern fiction writers (video game scriptwriters or micro-series creators).
Structure your stories **without code**, manage branching paths and export your work in a readable format to collaborate easily with your team.

![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)
![Status: In development](https://img.shields.io/badge/Statut-En%20développement-orange)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.4.0-green.svg)


---

## Features
- **Visual authoring**: Create narrative maps by adding narrative blocks via the menus and linking them with connections (rubber-band mode).
- **Agents**: Manage agents (characters or artefacts) and associate them with narrative blocks.
- **Two synchronized views**: an **Events** view (graph of states and events) and an **Agents** view (agents × states association matrix), with cross-view navigation.
- **Informative badges**: blocks display the number of associated agents (Events view) and of incoming/outgoing events (Agents view).
- **Branch management**: Visualise and organise the connections between all elements of your narrative (transitions from block to blck and relations between agents).
- **Readable export**: Share your work as hypertext pages to share it with your team (developers, filmmakers, etc.).
- **Under development**: MVP beta version in progress.


---

## Usage
### Example workflow
1. **Create a new narrative map**:
   - Add narrative blocks (scenes, branches and conditions) with basc click operations.
   - connect them and attach them to paths to form narrative arcs within a given narrative map (journeys).
2. **Export your work**:
   - Export your project’s narrative maps to read them directly in a browser.


---

## Installation

### Prerequisites
- **[uv](https://docs.astral.sh/uv/)** (recommended) — Windows: `winget install astral.uv`, Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- Or any **Python 3.10+** with pip (see *Without uv* below).

### Quick start (with uv)
From the **root of the cloned repository** (the folder containing `pyproject.toml`):

```bash
uv venv                        # create .venv/ with the pinned Python (.python-version), downloaded automatically if needed
uv sync --no-install-project   # install the runtime dependencies exactly as locked in uv.lock (PySide6)
.venv/bin/python src/main.py   # run the application (Windows: .venv\Scripts\python src\main.py)
```

Run the test suite headless:

```bash
uv pip install -r requirements-test.txt   # test dependencies (not covered by uv.lock)
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -q   # Windows: .venv\Scripts\python -m pytest tests/ -q
```

Notes:
- Always run `uv venv` from the repository root: uv reads `requires-python = ">=3.10"` from `pyproject.toml` and the pinned interpreter from `.python-version`, so the environment is guaranteed compatible and identical for everyone (both files are committed). Outside the project folder, no version check is performed.
- The application is not installed as a package — it runs from source with `python src/main.py`.
- `.venv/` is git-ignored.

### Without uv (standard library only)
```bash
python3 -m venv .venv        # check first that `python3 --version` reports 3.10 or newer
.venv/bin/pip install "PySide6>=6.4.0" -r requirements-test.txt
.venv/bin/python src/main.py
```
With plain `venv` + `pip` there is no lockfile, so dependency versions are not pinned — prefer uv for a reproducible environment.


---

## Licence
This project is licensed under the **[MIT](LICENSE)** licence.


---

## Roadmap
- [ 1 ] Beta version of the MVP (next step).


---

## Note from the creator

### 06 August 2026
Hyperscript is a redesign of the former project Planoscript. The latter can be considered the proof of concept (POC) for the former.
Planoscript was originally a learning project. Although its successor is more ambitious, it should still be viewed in that same light.
Consequently, its design and implementation are evolving in tandem as the project progresses and unforeseen complexities come to light.

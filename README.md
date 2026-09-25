# JARVIS

Local Gemini Live desktop assistant with a PyQt6 interface, voice interaction, detachable panels, and optional browser, file, screen, and messaging tools.

JARVIS also includes a dedicated presentation studio that creates, edits,
redesigns, and extends editable widescreen `.pptx` decks from documents, data,
images, audio, and video, with optional PDF export. See the
[usage guide](docs/USAGE.md#6-powerpoint-presentations) for examples.

## Requirements

You need **Python 3.11 or newer** installed to set up and run JARVIS. Confirm
your Python version before continuing:

```bash
python --version
```

## Quick start (Windows, macOS, Linux)

In Terminal, run:

```bash
git clone https://github.com/atilioobadia-cpu/JARVIS-OS-V.2.git
cd JARVIS-OS-V.2
python scripts/setup_jarvis.py
```

On Windows, you can double-click `scripts/setup_jarvis.bat` instead.

Open `.env`, add your `GEMINI_API_KEY`, then launch JARVIS:

```bash
jarvis
```

You only need to run setup once. Activate `.venv` when opening a new terminal,
then type `jarvis`.

JARVIS's core UI, Gemini connection, presentations, research, files, and CLI are
cross-platform. Some computer-control, email, media, and browser integrations
depend on permissions and available applications on each operating system.

## Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
cp .env.example .env
./scripts/install_jarvis_cli.sh
jarvis
```

Set `GEMINI_API_KEY` in `.env` before launch. Optional settings such as voice and local API keys are documented in `.env.example`.

### Launch with `jarvis`

The CLI launcher is included in this repository. After cloning and completing
the one-time setup, install it for your user with:

```bash
./scripts/install_jarvis_cli.sh
```

Open a new terminal (or reload your shell profile), then start JARVIS with:

```bash
jarvis
```

Alternatively, from an activated virtual environment, `python3 -m pip install -e .`
installs the same `jarvis` command through the standard Python package entry point.

## Documentation

- [Usage guide](docs/USAGE.md)
- [Tutorial](docs/TUTORIAL.md)
- [Complete QA and bug-audit guide](docs/QA.md)
- [Contribution notes](CONTRIBUTING.md)

## Configuration files

Template files are included for local setup:

- `.env.example`
- `config/api_keys.example.json`
- `config/layout_settings.example.json`
- `config/ui_settings.example.json`
- `memory/long_term.example.json`
- `memory/task_history.example.json`

## Publishing checklist

- Keep `.env` and local secret files out of git.
- Do not commit `memory/long_term.json` or `config/api_keys.json`.
- Run `python3 -m py_compile main.py ui.py` before tagging a release.

## License

MIT License, see [LICENSE](LICENSE).

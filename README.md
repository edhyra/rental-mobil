# Rental Mobil - FastAPI + MongoDB

Prototype aplikasi sistem rental mobil.

Features:
- FastAPI REST API (cars, customers, rentals, payments)
- MongoDB (Beanie + Motor)
- Docker Compose (app + mongo)
- VS Code devcontainer
- Tests with `pytest` (async)

Local development (without Docker)

Follow these steps to run the project locally (useful when running `mongo_gui.py` or `pytest`):

- Create and activate a Python virtual environment named `.venv`:

```powershell
python -m venv .venv
```

- Activate:

PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:
```cmd
.\.venv\Scripts\activate.bat
```

macOS / Linux:
```bash
source .venv/bin/activate
```

- Install dependencies:
```bash
pip install -r requirements.txt
```

- Make sure MongoDB is running (e.g. via Docker Compose) before running the GUI or tests:
```bash
docker compose up -d
```

- Run the Mongo GUI:
```bash
python mongo_gui.py
```

- Run tests:
```bash
pytest -q
```

Quick start (with Docker):

```bash
# build & start services
docker compose up -d --build

# open API docs
# visit http://localhost:8000/docs

# run tests (requires mongo up)
pytest -q
```

Repository structure:
- `app/` - FastAPI app, models, routers, services
- `tests/` - pytest tests
- `docs/` - class diagram & DB schema

See `docs/mapping.md` for mapping design→code.

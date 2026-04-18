# Rental Mobil - FastAPI + MongoDB

Prototype aplikasi sistem rental mobil.

Features:
- FastAPI REST API (cars, customers, rentals, payments)
- MongoDB (Beanie + Motor)
- Docker Compose (app + mongo)
- VS Code devcontainer
- Tests with `pytest` (async)

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

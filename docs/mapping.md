**Design → Code mapping**

- `Car` (class diagram) → `app.models.Car`
  - `plate_number`, `make`, `model`, `year`, `color`, `daily_rate`, `status` → fields on `Car` Document
  - API endpoints in `app.routers.cars` (`GET /cars`, `GET /cars/{id}`, `POST /cars`, `PUT /cars/{id}`)

- `Customer` → `app.models.Customer`
  - Endpoints in `app.routers.customers`

- `Rental` → `app.models.Rental` and business logic in `app.services.rental_service`
  - `POST /rentals` invokes `create_rental(...)` which atomically updates car status and creates a `Rental` document

- `Payment` → `app.models.Payment` and endpoints in `app.routers.payments`

- Database init → `app.db.init_db()` called at FastAPI startup (`app.main`)

Notes:
- MongoDB collection names are declared in each Document via `Settings.name`.
- `app.services.rental_service.create_rental` uses a `find_one_and_update` on the cars collection to avoid races when two users try to rent the same car.
- Tests in `tests/` use `httpx.AsyncClient` against the ASGI app. For reliable runs start `mongo` via `docker compose up -d`.

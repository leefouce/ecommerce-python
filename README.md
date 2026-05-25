# Ecommerce Python

Incremental FastAPI ecommerce backend learning project.

## Current phase

Phase 8: Docker deployment foundation.

Implemented so far:

- `GET /health`
- `GET /products`
- `GET /products/{product_id}`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- product data now persists in local SQLite through SQLAlchemy
- user table foundation with hashed password storage and verification helpers
- registration rejects duplicate emails and never returns password hashes
- login verifies the password and returns a bearer access token
- access tokens include expiration claims and are signed with a settings-backed secret
- `GET /auth/me` uses the bearer token to return the current authenticated user
- `POST /cart/items` lets an authenticated user add a product to their cart
- `GET /cart/items` lists the authenticated user's cart items
- `DELETE /cart/items/{product_id}` removes a product from the authenticated user's cart
- cart tests cover authentication, missing products, invalid quantities, and user isolation
- `POST /orders/checkout` creates a mock order from the authenticated user's cart and clears the cart
- `GET /orders` lists the authenticated user's order history
- users have an `is_admin` flag for authorization checks
- `POST /admin/products` lets admins create products
- `PATCH /admin/products/{product_id}` lets admins update product fields
- `DELETE /admin/products/{product_id}` lets admins delete products
- admin product endpoints require authentication and reject non-admin users
- deployment config includes a Dockerfile, Docker Compose PostgreSQL stack, `.env.example`, and container start script

## Environment configuration

Optional local development settings:

```bash
export APP_TOKEN_SECRET="replace-with-a-long-random-secret"
export APP_ACCESS_TOKEN_EXPIRE_MINUTES="30"
export APP_DATABASE_URL="postgresql+psycopg://shop:password@localhost:5432/ecommerce"
```

If `APP_DATABASE_URL` is unset, the app uses `sqlite:///./ecommerce.db` for learning-friendly local development. Do not use the default token secret outside local development.

## Database migrations

Phase 7 introduces Alembic migrations and PostgreSQL-ready configuration.

```bash
alembic upgrade head
```

For local SQLite migration testing without touching `ecommerce.db`, point `APP_DATABASE_URL` at a temporary database file before running Alembic.

## Docker Compose deployment

Create a local env file from the example and change the secrets before running containers:

```bash
cp .env.example .env
docker compose up --build
```

The `api` container waits for PostgreSQL to become healthy, runs `alembic upgrade head`, then starts `uvicorn` on port `8000`.

## Setup

Install the project with development dependencies:

```bash
python -m pip install -e '.[dev]'
```

## Run tests

```bash
pytest
```

## Start development server

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "ok"}
```

## Workflow notes

This project is also used to learn Hermes Agent workflows:

- planning before implementation
- tool-based file inspection and verification
- TDD red-green-refactor
- skills for reusable workflows
- later: multi-agent implementation and review

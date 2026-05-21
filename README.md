# Ecommerce Python

Incremental FastAPI ecommerce backend learning project.

## Current phase

Phase 3: User registration and login.

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

## Environment configuration

Optional local development settings:

```bash
export APP_TOKEN_SECRET="replace-with-a-long-random-secret"
export APP_ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

If unset, the app uses learning-friendly local defaults. Do not use the default secret outside local development.

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

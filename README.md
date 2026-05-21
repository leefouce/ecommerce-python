# Ecommerce Python

Incremental FastAPI ecommerce backend learning project.

## Current phase

Phase 3: User registration and login.

Implemented so far:

- `GET /health`
- `GET /products`
- `GET /products/{product_id}`
- product data now persists in local SQLite through SQLAlchemy
- user table foundation with hashed password storage and verification helpers

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

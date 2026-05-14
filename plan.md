# Ecommerce Backend Learning Project Plan

> **For Hermes:** This is both a FastAPI ecommerce backend implementation project and a learning project for understanding Hermes Agent workflows, including planning, tools, skills, memory, TDD, and later multi-agent work.

**Goal:** Build an ecommerce backend incrementally with FastAPI while explaining the agent workflow after each phase.

**Architecture:** Start with a minimal FastAPI application and a `/health` endpoint. Add ecommerce features gradually, beginning with mock data and SQLite where useful, then migrate toward PostgreSQL later. Keep each phase small, tested, and easy to understand.

**Tech Stack:** Python, FastAPI, pytest, SQLAlchemy, Pydantic, JWT authentication, PostgreSQL later; SQLite/mock data first where appropriate.

---

## Working Rules

1. Work incrementally.
2. Do not implement everything in one step.
3. Inspect the current directory before changing files.
4. If the directory is empty, use a clean FastAPI project structure.
5. Do not add real payment integration.
6. Use mock data or SQLite first if useful, then migrate to PostgreSQL later.
7. After each change, explain modified files and run tests or start the server.
8. Use TDD for new behavior: write a failing test first, then implement the minimal code to pass.
9. Explain Hermes workflow concepts as we go: tools, skills, memory, and multi-agent.
10. Introduce multi-agent only when the project is complex enough to benefit from it.
11. Use a git-flow style workflow: `main` stays stable, `develop` is the integration branch, and new work happens on `feature/*` branches before merging back.

---

## Phase 0: FastAPI Skeleton + Health Check

**Objective:** Create only the project skeleton and a `/health` endpoint. Do not implement ecommerce features yet.

**Files:**

- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/api/__init__.py`
- Create: `app/api/health.py`
- Create: `tests/__init__.py`
- Create: `tests/test_health.py`

### TDD workflow for Phase 0

1. Write `tests/test_health.py` first.
2. Run `pytest tests/test_health.py -v` and confirm it fails because the app does not exist yet.
3. Create the minimal FastAPI app and health route.
4. Run `pytest` and confirm the test passes.
5. Optionally start the server with `uvicorn app.main:app --reload` and verify `GET /health`.

### Expected `/health` response

```json
{"status": "ok"}
```

### Commands

```bash
pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/health
```

---

## Later Phases

### Phase 1: Product listing and detail with mock data

**Branch:** `feature/phase-1-products` from `develop`.

**Objective:** Add read-only product endpoints backed by in-memory mock data. Do not add database, admin management, cart, auth, or checkout yet.

**Endpoints:**

- `GET /products` returns the mock product list.
- `GET /products/{product_id}` returns one product.
- Missing product detail returns `404` with `{"detail": "Product not found"}`.

**Files:**

- Create: `tests/test_products.py`
- Create: `app/schemas/__init__.py`
- Create: `app/schemas/product.py`
- Create: `app/data/__init__.py`
- Create: `app/data/products.py`
- Create: `app/api/products.py`
- Modify: `app/main.py`

**TDD workflow:**

1. Write product endpoint tests first.
2. Run `pytest tests/test_products.py -v` and confirm failure because `/products` does not exist.
3. Add schema, mock data, and router.
4. Register the router in `app/main.py`.
5. Run `pytest` and confirm all tests pass.
6. Push the feature branch and open a PR into `develop`.

### Phase 2: SQLite + SQLAlchemy foundation

- Add database session setup.
- Add Product model.
- Use SQLite for local learning speed.
- Keep PostgreSQL for a later migration phase.

### Phase 3: User registration and login

- Add User model.
- Add password hashing.
- Add JWT login flow.
- Add auth tests.

### Phase 4: Shopping cart

- Add cart endpoints.
- Associate cart with authenticated users.
- Write tests for add/remove/list.

### Phase 5: Mock checkout and order history

- Convert cart to mock order.
- No real payment integration.
- Add order history endpoints.

### Phase 6: Basic admin product management

- Add admin-only product create/update/delete.
- Add role checks.
- Add authorization tests.

### Phase 7: PostgreSQL migration

- Add PostgreSQL configuration.
- Add Alembic migrations if appropriate.
- Keep tests deterministic.

---

## Hermes Learning Notes

### Tools

Hermes uses tools to inspect files, write files, run commands, and verify results. In this project, typical tools include:

- `search_files` to inspect project structure.
- `write_file` to create files.
- `read_file` to review file contents.
- `terminal` to run `pytest`, `uvicorn`, and other commands.
- `patch` to make targeted edits.

### Skills

Skills are reusable workflows. Relevant skills for this project:

- `writing-plans`: create clear implementation plans.
- `test-driven-development`: enforce RED-GREEN-REFACTOR.
- `systematic-debugging`: debug failures carefully.
- `subagent-driven-development`: later, use multi-agent implementation and review.

### Memory

Hermes memory stores durable preferences and stable facts, not temporary task progress. This project is remembered as a learning project where implementation and Hermes workflow explanation are both important.

### Multi-agent

Multi-agent is intentionally not used in Phase 0 because the task is small. Later, it can be used for implementation, test writing, code review, and security review when features become larger.

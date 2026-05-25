from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_fastapi_app_with_project_dependencies() -> None:
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()

    assert "FROM python:3.11-slim" in dockerfile
    assert "pip install --no-cache-dir ." in dockerfile
    assert "COPY . ." in dockerfile
    assert "scripts/start.sh" in dockerfile
    assert "EXPOSE 8000" in dockerfile


def test_compose_file_defines_api_and_postgres_services() -> None:
    compose = (PROJECT_ROOT / "compose.yaml").read_text()

    assert "api:" in compose
    assert "db:" in compose
    assert "postgres:16" in compose
    assert "APP_DATABASE_URL=postgresql+psycopg://" in compose
    assert "alembic upgrade head" not in compose, "migrations should live in the container start script"


def test_container_start_script_runs_migrations_before_server() -> None:
    start_script = (PROJECT_ROOT / "scripts" / "start.sh").read_text()

    migration_index = start_script.index("alembic upgrade head")
    server_index = start_script.index("uvicorn app.main:app")

    assert migration_index < server_index
    assert "exec uvicorn app.main:app" in start_script


def test_env_example_documents_required_deployment_settings() -> None:
    env_example = (PROJECT_ROOT / ".env.example").read_text()

    for key in [
        "APP_TOKEN_SECRET=",
        "APP_ACCESS_TOKEN_EXPIRE_MINUTES=",
        "APP_DATABASE_URL=",
        "POSTGRES_DB=",
        "POSTGRES_USER=",
        "POSTGRES_PASSWORD=",
    ]:
        assert key in env_example


def test_dockerignore_excludes_local_runtime_artifacts() -> None:
    dockerignore = (PROJECT_ROOT / ".dockerignore").read_text()

    for pattern in [".venv", "__pycache__", "*.db", ".env"]:
        assert pattern in dockerignore

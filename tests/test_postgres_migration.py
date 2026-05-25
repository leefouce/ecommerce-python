import importlib
from pathlib import Path

from app.core.config import get_settings


def test_database_url_can_be_configured_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "APP_DATABASE_URL",
        "postgresql+psycopg://shop:secret@localhost:5432/ecommerce",
    )

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://shop:secret@localhost:5432/ecommerce"


def test_database_engine_options_keep_sqlite_thread_override_only_for_sqlite() -> None:
    session_module = importlib.import_module("app.db.session")

    assert session_module.get_engine_options("sqlite:///./ecommerce.db") == {
        "connect_args": {"check_same_thread": False}
    }
    assert session_module.get_engine_options(
        "postgresql+psycopg://shop:secret@localhost:5432/ecommerce"
    ) == {}


def test_alembic_configuration_exists_for_schema_migrations() -> None:
    project_root = Path(__file__).resolve().parents[1]

    assert (project_root / "alembic.ini").exists()
    assert (project_root / "alembic" / "env.py").exists()
    versions = list((project_root / "alembic" / "versions").glob("*.py"))
    assert versions, "expected an initial Alembic migration file"


def test_initial_migration_creates_current_tables() -> None:
    project_root = Path(__file__).resolve().parents[1]
    migration_text = "\n".join(
        path.read_text() for path in (project_root / "alembic" / "versions").glob("*.py")
    )

    for table_name in [
        "products",
        "users",
        "cart_items",
        "orders",
        "order_items",
    ]:
        assert f'create_table("{table_name}"' in migration_text

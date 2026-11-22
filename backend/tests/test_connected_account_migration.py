from datetime import datetime, timezone

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings


PARENT_REVISION = "5d6e7f8091a2"
HEAD_REVISION = "a10c3d4e5f67"


def test_connected_account_migration_upgrade_and_downgrade_preserve_existing_email(tmp_path, monkeypatch):
    database_path = tmp_path / "migration-test.sqlite"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", database_url)
    alembic_config = Config("alembic.ini")

    command.upgrade(alembic_config, PARENT_REVISION)
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(
            "INSERT INTO users (email, hashed_password, full_name, is_active, created_at, updated_at) "
            "VALUES ('migration@example.test', 'test', 'Migration User', 1, :now, :now)"
        ), {"now": datetime.now(timezone.utc).replace(tzinfo=None)})
        connection.execute(text(
            "INSERT INTO emails (user_id, sender_name, sender_email, recipient, subject, body, received_at, "
            "category, is_read, is_important, is_deleted, attachments, created_at, updated_at) "
            "VALUES (1, 'Sender', 'sender@example.test', 'user@example.test', 'Existing', 'Body', :now, "
            "'other', 0, 0, 0, '[]', :now, :now)"
        ), {"now": datetime.now(timezone.utc).replace(tzinfo=None)})

    command.upgrade(alembic_config, HEAD_REVISION)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT subject FROM emails WHERE id = 1")).scalar_one() == "Existing"
        email_columns = {column["name"] for column in inspect(connection).get_columns("emails")}
        assert {"connected_account_id", "provider_message_id", "provider_thread_id"} <= email_columns
        assert {"connected_accounts", "oauth_states"} <= set(inspect(connection).get_table_names())
        assert "sync_started_at" in {column["name"] for column in inspect(connection).get_columns("connected_accounts")}
        assert "sync_lease_token" in {column["name"] for column in inspect(connection).get_columns("connected_accounts")}
        assert "gmail_sync_page_token" in {column["name"] for column in inspect(connection).get_columns("connected_accounts")}
        assert "is_read_user_modified" in {column["name"] for column in inspect(connection).get_columns("emails")}

    command.downgrade(alembic_config, PARENT_REVISION)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT subject FROM emails WHERE id = 1")).scalar_one() == "Existing"
        email_columns = {column["name"] for column in inspect(connection).get_columns("emails")}
        assert not {"connected_account_id", "provider_message_id", "provider_thread_id"} & email_columns
        assert not {"connected_accounts", "oauth_states"} & set(inspect(connection).get_table_names())
    engine.dispose()

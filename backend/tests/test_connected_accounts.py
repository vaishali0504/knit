from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import ConnectedAccount, Email, User
from conftest import TestingSessionLocal


def account(user_id: int, provider_account_id: str = "google-account-1") -> ConnectedAccount:
    return ConnectedAccount(
        user_id=user_id,
        provider="gmail",
        provider_account_id=provider_account_id,
        email_address=f"{provider_account_id}@example.test",
        encrypted_access_token="encrypted-access-placeholder",
        encrypted_refresh_token="encrypted-refresh-placeholder",
        granted_scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        sync_status="pending",
    )


def test_connected_account_unique_per_user_but_shared_gmail_can_belong_to_two_users(client):
    db = TestingSessionLocal()
    try:
        user_a = User(email="connected-a@example.test", hashed_password="test")
        user_b = User(email="connected-b@example.test", hashed_password="test")
        db.add_all([user_a, user_b])
        db.flush()
        db.add_all([account(user_a.id), account(user_b.id)])
        db.commit()

        db.add(account(user_a.id))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_email_provider_references_and_duplicate_prevention(client):
    db = TestingSessionLocal()
    try:
        user = User(email="connected-email@example.test", hashed_password="test")
        db.add(user)
        db.flush()
        connected = account(user.id)
        db.add(connected)
        db.flush()
        email = Email(
            user_id=user.id,
            connected_account_id=connected.id,
            provider_message_id="gmail-message-1",
            provider_thread_id="gmail-thread-1",
            sender_name="Test Sender",
            sender_email="sender@example.test",
            recipient="owner@example.test",
            subject="Test message",
            body="Test body",
            received_at=datetime.now(timezone.utc),
            category="other",
        )
        db.add(email)
        db.commit()
        assert email.connected_account_id == connected.id
        assert email.provider_thread_id == "gmail-thread-1"

        db.add(Email(
            user_id=user.id,
            connected_account_id=connected.id,
            provider_message_id="gmail-message-1",
            sender_name="Duplicate",
            sender_email="sender@example.test",
            recipient="owner@example.test",
            subject="Duplicate message",
            body="Duplicate body",
            received_at=datetime.now(timezone.utc),
            category="other",
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # Existing sample/local records remain valid with nullable provider references.
        local_email = Email(
            user_id=user.id,
            sender_name="Local Sender",
            sender_email="local@example.test",
            recipient="owner@example.test",
            subject="Local message",
            body="Local body",
            received_at=datetime.now(timezone.utc),
            category="other",
        )
        db.add(local_email)
        db.commit()
        assert local_email.connected_account_id is None
    finally:
        db.close()

import pytest
from cryptography.fernet import Fernet

from app.core.config import settings
from app.services.token_encryption import TokenEncryptionError, decrypt_token, encrypt_token


def test_token_encryption_round_trip_and_independent_ciphertexts(monkeypatch):
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))
    first = encrypt_token("access-token-one")
    second = encrypt_token("refresh-token-two")

    assert first != second
    assert "access-token-one" not in first
    assert "refresh-token-two" not in second
    assert decrypt_token(first) == "access-token-one"
    assert decrypt_token(second) == "refresh-token-two"


def test_token_encryption_fails_closed_for_missing_or_invalid_key(monkeypatch):
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", "")
    with pytest.raises(TokenEncryptionError, match="not configured"):
        encrypt_token("test-token")

    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", "not-a-fernet-key")
    with pytest.raises(TokenEncryptionError, match="configuration is invalid"):
        encrypt_token("test-token")


def test_token_decryption_rejects_tampered_ciphertext(monkeypatch):
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))
    ciphertext = encrypt_token("test-token")
    tampered = ciphertext[:-1] + ("A" if ciphertext[-1] != "A" else "B")

    with pytest.raises(TokenEncryptionError, match="decryption failed"):
        decrypt_token(tampered)

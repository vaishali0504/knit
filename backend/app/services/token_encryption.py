from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class TokenEncryptionError(Exception):
    """Raised when a provider token cannot be safely encrypted or decrypted."""


def _fernet() -> Fernet:
    key = settings.GMAIL_TOKEN_ENCRYPTION_KEY
    if not key:
        raise TokenEncryptionError("Token encryption is not configured")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError, TypeError) as exc:
        raise TokenEncryptionError("Token encryption configuration is invalid") from exc


def encrypt_token(token: str) -> str:
    if not isinstance(token, str) or not token:
        raise TokenEncryptionError("Token must be a non-empty string")
    try:
        return _fernet().encrypt(token.encode("utf-8")).decode("ascii")
    except (ValueError, UnicodeEncodeError, TypeError) as exc:
        raise TokenEncryptionError("Token encryption failed") from exc


def decrypt_token(ciphertext: str) -> str:
    if not isinstance(ciphertext, str) or not ciphertext:
        raise TokenEncryptionError("Encrypted token is invalid")
    try:
        return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, UnicodeEncodeError, TypeError) as exc:
        raise TokenEncryptionError("Token decryption failed") from exc

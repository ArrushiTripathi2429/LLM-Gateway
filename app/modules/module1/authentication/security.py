
import secrets
import hashlib
import hmac

from authentication.config import settings


def generate_key_id() -> str:
    """
    Generates a unique public identifier.
    """

    return secrets.token_hex(8)


def generate_secret() -> str:
    """
    Generates a cryptographically secure secret.
    """

    return secrets.token_urlsafe(32)


def generate_api_key():
    """
    Generates complete gateway API key.
    """

    key_id = generate_key_id()

    secret = generate_secret()

    raw_key = f"lgw_live_{key_id}_{secret}"

    return {
        "key_id": key_id,
        "secret": secret,
        "raw_key": raw_key
    }


def hash_api_key(secret: str) -> str:
    """
    Generates HMAC-SHA256 hash of API key secret.
    """

    return hmac.new(
        settings.API_KEY_PEPPER.encode(),
        secret.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_api_key(
    secret: str,
    stored_hash: str
) -> bool:
    """
    Verifies incoming secret against stored hash.
    """

    calculated_hash = hash_api_key(secret)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash
    )
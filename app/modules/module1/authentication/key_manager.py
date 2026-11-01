from datetime import datetime, timezone

from authentication.security import (
    generate_api_key,
    hash_api_key
)


def create_key_record(
    name: str,
    team_id: str,
    scopes: list[str],
    expires_at=None,
    environment: str = "live"
):
    """
    Generates an API key and creates its metadata record.
    """

    generated = generate_api_key()

    key_id = generated["key_id"]
    secret = generated["secret"]
    raw_key = generated["raw_key"]

    key_hash = hash_api_key(secret)

    record = {
        "key_id": key_id,
        "key_hash": key_hash,
        "name": name,
        "team_id": team_id,
        "environment": environment,
        "scopes": scopes,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "last_used_at": None
    }

    return record, raw_key


def check_key_expiry(record: dict) -> bool:
    """
    Returns True if key is expired.
    """

    expires_at = record.get("expires_at")

    if expires_at is None:
        return False

    return expires_at <= datetime.now(timezone.utc)


def check_key_status(record: dict) -> bool:

    return record.get("status") == "active"


def update_key_name(record: dict, new_name: str):

    record["name"] = new_name

    return record


def revoke_key(record: dict):

    record["status"] = "revoked"

    return record


def update_last_used(record: dict):

    record["last_used_at"] = datetime.now(timezone.utc)

    return record


def rotate_key(
    old_record: dict,
    name: str,
    team_id: str,
    scopes: list[str]
):
    """
    Creates a replacement key.
    The caller is responsible for saving the new key
    and managing any overlap/revocation policy.
    """

    new_record, raw_key = create_key_record(
        name=name,
        team_id=team_id,
        scopes=scopes
    )

    return new_record, raw_key
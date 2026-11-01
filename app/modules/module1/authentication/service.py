from datetime import datetime, timezone

from fastapi import HTTPException

from authentication import repository
from authentication.security import verify_api_key

from authentication.key_manager import (
    create_key_record,
    check_key_expiry,
    check_key_status,
    revoke_key,
    update_key_name,
    update_last_used
)


# ==========================================
# ORGANIZATION MANAGEMENT
# ==========================================

def create_organization(name: str):

    organization = {
        "name": name,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }

    return repository.save_organization(organization)


def get_organization(organization_id: str):

    organization = repository.get_organization(organization_id)

    if not organization:
        raise HTTPException(404, "Organization not found")

    return organization


def list_organizations():

    return repository.list_organizations()


def update_organization(organization_id: str, name: str):

    organization = get_organization(organization_id)

    organization["name"] = name

    return organization


def deactivate_organization(organization_id: str):

    organization = get_organization(organization_id)

    organization["status"] = "inactive"

    return organization


def activate_organization(organization_id: str):

    organization = get_organization(organization_id)

    organization["status"] = "active"

    return organization


# ==========================================
# TEAM MANAGEMENT
# ==========================================

def create_team(name: str, organization_id: str):

    organization = get_organization(organization_id)

    if organization["status"] != "active":

        raise HTTPException(
            403,
            "Organization is inactive"
        )

    team = {
        "name": name,
        "organization_id": organization_id,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }

    return repository.save_team(team)


def get_team(team_id: str):

    team = repository.get_team(team_id)

    if not team:
        raise HTTPException(404, "Team not found")

    return team


def list_teams(organization_id: str):

    get_organization(organization_id)

    return repository.list_teams(organization_id)


def update_team(team_id: str, name: str):

    team = get_team(team_id)

    team["name"] = name

    return team


def deactivate_team(team_id: str):

    team = get_team(team_id)

    team["status"] = "inactive"

    return team


def activate_team(team_id: str):

    team = get_team(team_id)

    organization = get_organization(team["organization_id"])

    if organization["status"] != "active":

        raise HTTPException(
            403,
            "Cannot activate team under inactive organization"
        )

    team["status"] = "active"

    return team


# ==========================================
# API KEY GENERATION
# ==========================================

def generate_team_api_key(
    team_id: str,
    name: str,
    scopes: list[str],
    expires_at=None
):

    team = get_team(team_id)

    if team["status"] != "active":

        raise HTTPException(
            403,
            "Team is inactive"
        )

    organization = get_organization(team["organization_id"])

    if organization["status"] != "active":

        raise HTTPException(
            403,
            "Organization is inactive"
        )

    if expires_at is not None:

        if expires_at.tzinfo is None:

            raise HTTPException(
                422,
                "Expiry date must include timezone information"
            )

        if expires_at <= datetime.now(timezone.utc):

            raise HTTPException(
                422,
                "Expiry date must be in the future"
            )

    valid_scopes = {
        "chat:read",
        "chat:write",
        "models:list"
    }

    if not scopes or not set(scopes).issubset(valid_scopes):

        raise HTTPException(
            422,
            "Invalid or empty API key scopes"
        )

    record, raw_key = create_key_record(
        name=name,
        team_id=team_id,
        scopes=scopes,
        expires_at=expires_at
    )

    repository.save_api_key(record)

    return {
        "key_id": record["key_id"],
        "name": record["name"],
        "api_key": raw_key,
        "message": "Save this key securely. It will not be shown again."
    }


# ==========================================
# API KEY VALIDATION
# ==========================================

def parse_api_key(raw_key: str):

    parts = raw_key.split("_", 3)

    if len(parts) != 4:

        raise HTTPException(
            401,
            "Invalid API key format"
        )

    prefix, environment, key_id, secret = parts

    if prefix != "lgw" or environment != "live":

        raise HTTPException(
            401,
            "Invalid API key format"
        )

    return key_id, secret


def validate_api_key(raw_key: str):

    key_id, secret = parse_api_key(raw_key)

    record = repository.get_api_key(key_id)

    if not record:

        raise HTTPException(
            401,
            "Invalid API key"
        )

    if not check_key_status(record):

        raise HTTPException(
            401,
            "API key is inactive or revoked"
        )

    if check_key_expiry(record):

        raise HTTPException(
            401,
            "API key has expired"
        )

    if not verify_api_key(secret, record["key_hash"]):

        raise HTTPException(
            401,
            "Invalid API key"
        )

    team = get_team(record["team_id"])

    organization = get_organization(
        team["organization_id"]
    )

    if team["status"] != "active":

        raise HTTPException(
            403,
            "Team is inactive"
        )

    if organization["status"] != "active":

        raise HTTPException(
            403,
            "Organization is inactive"
        )

    update_last_used(record)

    return {
        "api_key_id": key_id,
        "team_id": team["id"],
        "organization_id": organization["id"],
        "scopes": record["scopes"]
    }


# ==========================================
# API KEY LIFECYCLE
# ==========================================

def list_team_api_keys(team_id: str):

    get_team(team_id)

    return repository.list_api_keys(team_id)


def get_api_key(key_id: str):

    record = repository.get_api_key(key_id)

    if not record:

        raise HTTPException(
            404,
            "API key not found"
        )

    return record


def revoke_api_key(key_id: str):

    record = get_api_key(key_id)

    if record["status"] == "revoked":

        raise HTTPException(
            400,
            "API key already revoked"
        )

    return revoke_key(record)


def rename_api_key(key_id: str, new_name: str):

    record = get_api_key(key_id)

    if record["status"] != "active":

        raise HTTPException(
            400,
            "Cannot rename inactive API key"
        )

    return update_key_name(record, new_name)


def rotate_api_key(key_id: str):

    old_record = get_api_key(key_id)

    if old_record["status"] != "active":

        raise HTTPException(
            400,
            "Only active API keys can be rotated"
        )

    team_id = old_record["team_id"]

    new_record, raw_key = create_key_record(
        name=old_record["name"],
        team_id=team_id,
        scopes=old_record["scopes"]
    )

    repository.save_api_key(new_record)

    # Revoke old key after creating new key
    revoke_key(old_record)

    return {
        "key_id": new_record["key_id"],
        "api_key": raw_key,
        "message": "Key rotated successfully. Save the new key securely."
    }


# ==========================================
# PERMISSION MANAGEMENT
# ==========================================

def get_team_permissions(team_id: str):

    get_team(team_id)

    permissions = set()

    for record in repository.list_api_keys(team_id):

        if (
            record["status"] == "active"
            and not check_key_expiry(record)
        ):
            permissions.update(record["scopes"])

    return list(permissions)
from fastapi import HTTPException


def check_scope(
    team_data: dict,
    required_scope: str
):

    scopes = team_data.get("scopes", [])

    if required_scope not in scopes:

        raise HTTPException(
            status_code=403,
            detail=f"Missing required permission: {required_scope}"
        )

    return True


def check_model_access(
    allowed_models: list[str],
    requested_model: str
):

    if requested_model not in allowed_models:

        raise HTTPException(
            status_code=403,
            detail="Model access denied"
        )

    return True


def check_permissions(
    team_data: dict,
    required_scope: str
):

    return check_scope(
        team_data,
        required_scope
    )
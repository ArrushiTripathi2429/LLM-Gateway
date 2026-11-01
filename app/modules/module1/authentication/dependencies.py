from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from authentication.service import validate_api_key


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_team(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    if credentials is None:

        raise HTTPException(
            status_code=401,
            detail="API key required"
        )

    raw_key = credentials.credentials

    return validate_api_key(raw_key)


def get_current_organization(
    team_data: dict = Depends(get_current_team)
):

    return team_data["organization_id"]


def get_current_api_key(
    team_data: dict = Depends(get_current_team)
):

    return team_data["api_key_id"]


def require_scope(required_scope: str):

    def scope_dependency(
        team_data: dict = Depends(get_current_team)
    ):

        from authentication.permissions import check_scope

        check_scope(team_data, required_scope)

        return team_data

    return scope_dependency
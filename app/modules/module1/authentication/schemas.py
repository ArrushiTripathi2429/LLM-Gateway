from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# ORGANIZATION

class OrganizationCreate(BaseModel):

    name: str = Field(min_length=2, max_length=150)


class OrganizationUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )


# TEAM

class TeamCreate(BaseModel):

    name: str = Field(min_length=2, max_length=150)

    organization_id: str


class TeamUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )


# API KEY

class APIKeyCreate(BaseModel):

    name: str = Field(min_length=2, max_length=100)

    scopes: list[str] = Field(
        default_factory=lambda: ["chat:write"]
    )

    expires_at: datetime | None = None


class APIKeyRename(BaseModel):

    name: str = Field(min_length=2, max_length=100)


class OrganizationResponse(BaseModel):

    id: str
    name: str
    status: str


class TeamResponse(BaseModel):

    id: str
    name: str
    organization_id: str
    status: str


class APIKeyResponse(BaseModel):

    key_id: str
    name: str
    team_id: str
    status: str
    scopes: list[str]

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreatedResponse(BaseModel):

    key_id: str
    name: str
    api_key: str
    message: str
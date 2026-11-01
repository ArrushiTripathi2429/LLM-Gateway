import uuid


organizations = {}

teams = {}

api_keys = {}


# ORGANIZATION OPERATIONS

def save_organization(data: dict):

    organization_id = str(uuid.uuid4())

    data["id"] = organization_id

    organizations[organization_id] = data

    return data


def get_organization(organization_id: str):

    return organizations.get(organization_id)


def list_organizations():

    return list(organizations.values())


def delete_organization(organization_id: str):

    return organizations.pop(organization_id, None)


# TEAM OPERATIONS

def save_team(data: dict):

    team_id = str(uuid.uuid4())

    data["id"] = team_id

    teams[team_id] = data

    return data


def get_team(team_id: str):

    return teams.get(team_id)


def list_teams(organization_id: str):

    return [
        team for team in teams.values()
        if team["organization_id"] == organization_id
    ]


# API KEY OPERATIONS

def save_api_key(record: dict):

    api_keys[record["key_id"]] = record

    return record


def get_api_key(key_id: str):

    return api_keys.get(key_id)


def list_api_keys(team_id: str):

    return [
        key for key in api_keys.values()
        if key["team_id"] == team_id
    ]


def delete_api_key(key_id: str):

    return api_keys.pop(key_id, None)
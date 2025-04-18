from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import msal
import requests

import internal.config.config as config

router = APIRouter(
    prefix="/entra_id",
    tags=["Entra ID"]
)

CLIENT_ID = config.ENTRA_ID_CLIENT_ID
CLIENT_SECRET = config.ENTRA_ID_CLIENT_SECRET
AUTHORITY = config.ENTRA_ID_BASE_URL + "common"  # This is the common endpoint for all tenants

# User scope (delegated)
USER_SCOPE = config.ENTRA_ID_USER_SCOPE.split(",")
# Application scope
APPLICATION_SCOPE = config.ENTRA_ID_APPLICATION_SCOPE.split(",")

REDIRECT_URI = config.BACKEND_API_HOST + ":" + config.BACKEND_API_PORT + config.BACKEND_API_DEFAULT_ROUTE + "/auth/callback"
# MSAL Client
msal_client = msal.ConfidentialClientApplication(
    CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

@router.get("/login")
async def login():
    auth_url = msal_client.get_authorization_request_url(
        USER_SCOPE,
        redirect_uri=REDIRECT_URI,
        response_type="code"
    )
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(code: str):
    result = msal_client.acquire_token_by_authorization_code(
        code,
        scopes=USER_SCOPE,
        redirect_uri=REDIRECT_URI
    )
    if "access_token" in result:
        return {"access_token": result["access_token"]}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to obtain token")

#####

@router.get("/app-token")
async def get_app_token():
    result = msal_client.acquire_token_for_client(scopes=APPLICATION_SCOPE)
    if "access_token" in result:
        return {"access_token": result["access_token"]}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to obtain application token")

def get_access_token():
    result = msal_client.acquire_token_for_client(scopes=APPLICATION_SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to obtain token")

@router.get("/groups")
async def get_groups():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Request specific properties using $select
    params = {
        "$select": "id,displayName,description"
    }
    response = requests.get("https://graph.microsoft.com/v1.0/groups", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch groups")

@router.get("/groups/{group_id}/members")
async def get_group_members(group_id: str):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Request specific properties using $select
    params = {
        "$select": "id,displayName,mail,userPrincipalName"
    }
    response = requests.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}/members", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch group members")

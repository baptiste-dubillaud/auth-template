from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import msal
import requests
import secrets

from internal.database.models import get_db, User, OAuthAccount
from internal.auth.schemas import Token, UserResponse, OAuthURL
from internal.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import internal.config.config as config

router = APIRouter(
    prefix="/microsoft",
    tags=["Microsoft OAuth"]
)

######## Configuration ########
CLIENT_ID = config.ENTRA_ID_CLIENT_ID
CLIENT_SECRET = config.ENTRA_ID_CLIENT_SECRET
AUTHORITY = config.ENTRA_ID_BASE_URL + "common"  # This is the common endpoint for all tenants

# User scope (delegated)
USER_SCOPE = config.ENTRA_ID_USER_SCOPE.split(",")
# Application scope
APPLICATION_SCOPE = config.ENTRA_ID_APPLICATION_SCOPE.split(",")

REDIRECT_URI = f"http://{config.BACKEND_API_HOST}:{config.BACKEND_API_PORT}{config.BACKEND_API_DEFAULT_ROUTE}/auth/microsoft/callback"

# MSAL Client
msal_client = msal.ConfidentialClientApplication(
    CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

@router.get("/login", response_model=OAuthURL)
async def microsoft_login():
    """Initiate Microsoft OAuth login."""
    state = secrets.token_urlsafe(32)
    auth_url = msal_client.get_authorization_request_url(
        USER_SCOPE,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        state=state
    )
    return {
        "auth_url": auth_url,
        "state": state
    }

@router.get("/callback", response_model=Token)
async def microsoft_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """Handle Microsoft OAuth callback."""
    try:
        result = msal_client.acquire_token_by_authorization_code(
            code,
            scopes=USER_SCOPE,
            redirect_uri=REDIRECT_URI
        )
        
        if "access_token" not in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Failed to obtain token"
            )
        
        access_token = result["access_token"]
        
        # Get user info from Microsoft Graph
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Microsoft"
            )
        
        user_info = response.json()
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == "microsoft",
            OAuthAccount.provider_user_id == user_info.get("id")
        ).first()
        
        if oauth_account:
            # Update existing account
            oauth_account.access_token = access_token
            oauth_account.refresh_token = result.get("refresh_token")
            if result.get("expires_in"):
                oauth_account.expires_at = datetime.utcnow() + timedelta(seconds=int(result["expires_in"]))
            
            user = oauth_account.user
        else:
            # Check if user exists by email
            user_email = user_info.get("mail") or user_info.get("userPrincipalName")
            user = None
            if user_email:
                user = db.query(User).filter(User.email == user_email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_email,
                    full_name=user_info.get("displayName"),
                    is_verified=True  # OAuth users are considered verified
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create OAuth account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="microsoft",
                provider_user_id=user_info.get("id"),
                provider_email=user_email,
                access_token=access_token,
                refresh_token=result.get("refresh_token")
            )
            if result.get("expires_in"):
                oauth_account.expires_at = datetime.utcnow() + timedelta(seconds=int(result["expires_in"]))
            
            db.add(oauth_account)
        
        db.commit()
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )

# Keep the existing app-token and groups endpoints for backward compatibility
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

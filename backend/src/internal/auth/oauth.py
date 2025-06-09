from authlib.integrations.base_client import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

from internal.config.config import (
    BACKEND_API_HOST, BACKEND_API_PORT, BACKEND_API_DEFAULT_ROUTE,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
)

class OAuthProvider:
    def __init__(self, client_id: str, client_secret: str, authorize_url: str, 
                 token_url: str, user_info_url: str, scopes: list):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.user_info_url = user_info_url
        self.scopes = scopes
        self.redirect_uri = f"http://{BACKEND_API_HOST}:{BACKEND_API_PORT}{BACKEND_API_DEFAULT_ROUTE}/auth/{{provider}}/callback"

    async def get_authorization_url(self, provider_name: str, state: str) -> str:
        """Generate OAuth authorization URL."""
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri.format(provider=provider_name)
        )
        
        authorization_url, _ = client.create_authorization_url(
            self.authorize_url,
            scope=' '.join(self.scopes),
            state=state
        )
        return authorization_url

    async def exchange_code_for_token(self, provider_name: str, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri.format(provider=provider_name)
        )
        
        try:
            token = await client.fetch_token(
                self.token_url,
                code=code
            )
            return token
        except OAuthError as e:
            raise Exception(f"Failed to exchange code for token: {str(e)}")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(self.user_info_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")
                
            return response.json()

# OAuth provider configurations
OAUTH_PROVIDERS = {
    "google": OAuthProvider(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
        scopes=["openid", "email", "profile"]
    ),
    "facebook": OAuthProvider(
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
        token_url="https://graph.facebook.com/v18.0/oauth/access_token",
        user_info_url="https://graph.facebook.com/me?fields=id,name,email,picture",
        scopes=["email", "public_profile"]
    ),
    "strava": OAuthProvider(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        authorize_url="https://www.strava.com/oauth/authorize",
        token_url="https://www.strava.com/oauth/token",
        user_info_url="https://www.strava.com/api/v3/athlete",
        scopes=["read", "profile:read_all"]
    )
}

def get_oauth_provider(provider_name: str) -> OAuthProvider:
    """Get OAuth provider configuration."""
    if provider_name not in OAUTH_PROVIDERS:
        raise ValueError(f"Unsupported OAuth provider: {provider_name}")
    return OAUTH_PROVIDERS[provider_name]

def normalize_user_data(provider_name: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize user data from different OAuth providers."""
    if provider_name == "google":
        return {
            "provider_user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "full_name": user_data.get("name"),
            "avatar_url": user_data.get("picture"),
            "provider_email": user_data.get("email")
        }
    elif provider_name == "facebook":
        return {
            "provider_user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "full_name": user_data.get("name"),
            "avatar_url": user_data.get("picture", {}).get("data", {}).get("url"),
            "provider_email": user_data.get("email")
        }
    elif provider_name == "strava":
        return {
            "provider_user_id": str(user_data.get("id")),
            "email": None,  # Strava doesn't provide email in basic scope
            "full_name": f"{user_data.get('firstname', '')} {user_data.get('lastname', '')}".strip(),
            "avatar_url": user_data.get("profile"),
            "provider_email": None
        }
    else:
        return user_data

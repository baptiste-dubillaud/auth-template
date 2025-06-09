from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets

from internal.database.models import get_db, User, OAuthAccount
from internal.auth.schemas import Token, UserResponse, OAuthURL
from internal.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from internal.auth.oauth import get_oauth_provider, normalize_user_data

router = APIRouter(
    prefix="/strava",
    tags=["Strava OAuth"]
)

@router.get("/login", response_model=OAuthURL)
async def strava_login():
    """Initiate Strava OAuth login."""
    provider = get_oauth_provider("strava")
    state = secrets.token_urlsafe(32)
    
    auth_url = await provider.get_authorization_url("strava", state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }

@router.get("/callback", response_model=Token)
async def strava_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """Handle Strava OAuth callback."""
    provider = get_oauth_provider("strava")
    
    try:
        # Exchange code for token
        token_data = await provider.exchange_code_for_token("strava", code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Get user info from Strava
        user_info = await provider.get_user_info(access_token)
        normalized_data = normalize_user_data("strava", user_info)
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == "strava",
            OAuthAccount.provider_user_id == normalized_data["provider_user_id"]
        ).first()
        
        if oauth_account:
            # Update existing account
            oauth_account.access_token = access_token
            oauth_account.refresh_token = token_data.get("refresh_token")
            if token_data.get("expires_in"):
                oauth_account.expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))
            
            user = oauth_account.user
        else:
            # For Strava, we need to handle the case where email might not be provided
            # We'll create a unique email based on the Strava user ID if no email is available
            user_email = normalized_data.get("email")
            if not user_email:
                user_email = f"strava_{normalized_data['provider_user_id']}@strava.local"
            
            # Check if user exists by email
            user = db.query(User).filter(User.email == user_email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_email,
                    full_name=normalized_data.get("full_name"),
                    avatar_url=normalized_data.get("avatar_url"),
                    is_verified=True  # OAuth users are considered verified
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create OAuth account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="strava",
                provider_user_id=normalized_data["provider_user_id"],
                provider_email=normalized_data.get("provider_email"),
                access_token=access_token,
                refresh_token=token_data.get("refresh_token")
            )
            if token_data.get("expires_in"):
                oauth_account.expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))
            
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

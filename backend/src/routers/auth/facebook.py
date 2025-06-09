from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets

from internal.database.models import get_db, User, OAuthAccount
from internal.auth.schemas import Token, UserResponse, OAuthURL
from internal.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from internal.auth.oauth import get_oauth_provider, normalize_user_data

router = APIRouter(
    prefix="/auth/facebook",
    tags=["Facebook OAuth"]
)

@router.get("/login", response_model=OAuthURL)
async def facebook_login():
    """Initiate Facebook OAuth login."""
    provider = get_oauth_provider("facebook")
    state = secrets.token_urlsafe(32)
    
    auth_url = await provider.get_authorization_url("facebook", state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }

@router.get("/callback", response_model=Token)
async def facebook_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """Handle Facebook OAuth callback."""
    provider = get_oauth_provider("facebook")
    
    try:
        # Exchange code for token
        token_data = await provider.exchange_code_for_token("facebook", code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Get user info from Facebook
        user_info = await provider.get_user_info(access_token)
        normalized_data = normalize_user_data("facebook", user_info)
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == "facebook",
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
            # Check if user exists by email
            user = None
            if normalized_data.get("email"):
                user = db.query(User).filter(User.email == normalized_data["email"]).first()
            
            if not user:
                # Create new user
                user = User(
                    email=normalized_data.get("email"),
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
                provider="facebook",
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
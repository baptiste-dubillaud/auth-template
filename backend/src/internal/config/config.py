import os
from dotenv import load_dotenv

from internal.enum.auth_source_enum import AuthSourceEnum

# Load environment variables from .env file
load_dotenv()

def check_env_variable(key: str) -> str:
    """
    Checks if a specific environment variable exists and returns its value.
    Raises an exception if the variable is not found.
    """
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Environment variable '{key}' is not set in the .env file.")
    return value

### BACKEND API CONFIGURATION ###
BACKEND_API_HOST = check_env_variable("BACKEND_API_HOST")
BACKEND_API_PORT = check_env_variable("BACKEND_API_PORT")
BACKEND_API_DEFAULT_ROUTE = check_env_variable("BACKEND_API_DEFAULT_ROUTE")

### AUTHENTICATION CONFIGURATION ###
# Authentication methods
AUTH_EMAIL_PASSWORD = check_env_variable("AUTH_EMAIL_PASSWORD")
AUTH_MICROSOFT = check_env_variable("AUTH_MICROSOFT")
AUTH_GOOGLE = check_env_variable("AUTH_GOOGLE")
AUTH_FACEBOOK = check_env_variable("AUTH_FACEBOOK")
AUTH_STRAVA = check_env_variable("AUTH_STRAVA")

# Microsoft authentication
ENTRA_ID_CLIENT_ID = check_env_variable("ENTRA_ID_CLIENT_ID")
ENTRA_ID_CLIENT_SECRET = check_env_variable("ENTRA_ID_CLIENT_SECRET")
ENTRA_ID_BASE_URL = "https://login.microsoftonline.com/"
ENTRA_ID_USER_SCOPE = "User.Read,Group.Read.All,GroupMember.Read.All"
ENTRA_ID_APPLICATION_SCOPE = "https://graph.microsoft.com/.default"

# Google authentication
GOOGLE_CLIENT_ID = check_env_variable("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = check_env_variable("GOOGLE_CLIENT_SECRET")

# Facebook authentication
FACEBOOK_CLIENT_ID = check_env_variable("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = check_env_variable("FACEBOOK_CLIENT_SECRET")

# Strava authentication
STRAVA_CLIENT_ID = check_env_variable("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = check_env_variable("STRAVA_CLIENT_SECRET")

# JWT Configuration
JWT_SECRET_KEY = check_env_variable("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

### DATA CONFIGURATION ###
DATABASE_NAME = check_env_variable("DATABASE_NAME")
DATABASE_USER = check_env_variable("DATABASE_USER")
DATABASE_PASSWORD = check_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = check_env_variable("DATABASE_HOST")
DATABASE_PORT = check_env_variable("DATABASE_PORT")

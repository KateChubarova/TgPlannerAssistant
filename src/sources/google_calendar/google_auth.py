import json
import os

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from shared.models.user import TgUser

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = os.getenv("WEB_GOOGLE_CREDENTIALS")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def load_client_info() -> {str}:
    """
    Load client credentials for Google OAuth from the credentials file.

    This function reads the OAuth client configuration from the JSON file
    defined in the environment and returns the relevant fields required for
    building OAuth flows.

    Return:
        tuple[str, str, str, str]: A tuple containing client_id, client_secret,
            token_uri, and auth_uri used for OAuth configuration.
    """
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)["web"]

    client_id = data["client_id"]
    client_secret = data["client_secret"]
    token_uri = data["token_uri"]
    auth_uri = data["auth_uri"]

    return client_id, client_secret, token_uri, auth_uri


CLIENT_ID, CLIENT_SECRET, TOKEN_URI, AUTH_URI = load_client_info()


def create_flow(state: str = None) -> Flow:
    """
    Create an OAuth2 Flow object for handling Google authentication.

    This function initializes a Google OAuth2 Flow using client secret files,
    the requested scopes, and the redirect URI. Optionally, a state value
    may be provided for user identification.

    Args:
        state (str): Optional state parameter used to persist user-specific data
            through the OAuth process.

    Return:
        Flow: An initialized OAuth2 Flow object ready to generate auth URLs
            or exchange authorization codes.
    """
    return Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state,
    )


def build_auth_url(user_id: int) -> str:
    """
    Generate a Google OAuth authorization URL for the given user.

    This function creates an OAuth2 flow, builds the authorization URL, and
    attaches the user ID as the state parameter for later identification
    after the redirect.

    Args:
        user_id (int): The unique Telegram user ID used as the OAuth state.

    Return:
        str: A fully constructed URL that the user should open to log into
            Google Calendar and grant permissions.
    """
    flow = create_flow()

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=str(user_id),
    )

    return authorization_url


def exchange_code_for_tokens(code: str, state: str) -> Credentials:
    """
    Exchange an authorization code for OAuth2 access and refresh tokens.

    This function finalizes the OAuth login by sending the received code to
    Google, retrieving the tokens, and returning them as a Credentials object.

    Args:
        code (str): The authorization code returned by Google after user login.
        state (str): The OAuth state string used to validate the session.

    Return:
        Credentials: A Google OAuth2 credentials object containing access and
            refresh tokens along with token metadata.
    """
    flow = create_flow(state=state)
    flow.fetch_token(code=code)
    creds: Credentials = flow.credentials
    return creds


def get_creds(user: TgUser) -> Credentials:
    """
    Construct a Google Credentials object from a stored user record.

    This function takes user data saved in the database and converts it into a
    usable Credentials instance, including token expiry when available.

    Args:
        user (TgUser): The Telegram user whose stored OAuth tokens should be loaded.

    Return:
        Credentials: A Google OAuth2 credentials object with access, refresh,
            and expiry information.
    """
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    if user.token_expiry:
        creds.expiry = user.token_expiry
    return creds

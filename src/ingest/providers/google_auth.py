import json
import os
from typing import Optional

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from shared.models.user import TgUser

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = os.getenv("WEB_GOOGLE_CREDENTIALS")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def _load_client_info() -> {str}:
    """
    Загружает данные клиентского приложения Google (client_id, client_secret, token_uri, auth_uri)
    из файла credentials.json и возвращает их в виде кортежа.
    """
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)["web"]

    client_id = data["client_id"]
    client_secret = data["client_secret"]
    token_uri = data["token_uri"]
    auth_uri = data["auth_uri"]

    return client_id, client_secret, token_uri, auth_uri


CLIENT_ID, CLIENT_SECRET, TOKEN_URI, AUTH_URI = _load_client_info()


def _create_flow(state: str | None = None) -> Flow:
    """
    Создаёт OAuth2 Flow для авторизации в Google API,
    используя client secrets, заданные разрешения и redirect URI.
    """
    return Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state,
    )


def build_auth_url_for_user(user_id: int) -> str:
    """
    Формирует URL для авторизации пользователя в Google Calendar
    с передачей user_id в параметре state.
    """
    flow = _create_flow()

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=str(user_id),
    )

    return authorization_url


def exchange_code_for_tokens(code: str, state: str) -> Credentials:
    """
    Обменивает код авторизации (authorization code) на OAuth2 токены Google.
    """
    flow = _create_flow(state=state)
    flow.fetch_token(code=code)
    creds: Credentials = flow.credentials
    return creds


def get_creds(user: TgUser) -> Optional[Credentials]:
    """
    Восстанавливает объект Google Credentials из данных пользователя,
    включая access token, refresh token и срок истечения.
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

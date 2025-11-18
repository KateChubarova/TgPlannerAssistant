import json
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from sqlalchemy.orm import Session

from shared.models.user import TgUser


def _load_client_info():
    with open(CREDENTIALS_PATH, "r") as f:
        data = json.load(f)["installed"]
    return data["client_id"], data["client_secret"], data["token_uri"]


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS")
CLIENT_ID, CLIENT_SECRET, TOKEN_URI = _load_client_info()


def _creds_from_user(user: TgUser) -> Optional[Credentials]:
    if not user.google_access_token:
        return None

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    if user.token_expiry:
        creds.expiry = user.token_expiry
    return creds


def _get_valid_creds_from_user(user: TgUser) -> Optional[Credentials]:
    creds = _creds_from_user(user)
    if creds is None:
        return None

    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        return creds

    return None


def get_or_create_creds(session: Session, user: TgUser) -> Credentials:
    creds = _get_valid_creds_from_user(user)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES
        )
        creds = flow.run_local_server(port=0)

    user.google_access_token = creds.token
    user.google_refresh_token = creds.refresh_token
    user.token_expiry = creds.expiry

    session.add(user)
    session.commit()

    return creds

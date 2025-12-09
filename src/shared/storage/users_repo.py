from shared.models.user import TgUser
from shared.storage.db import SessionLocal


def get_user(user_id: int) -> TgUser:
    """
    Retrieve a Telegram user record from the database by its unique identifier.

    This function opens a new database session, fetches the user using its primary key,
    and returns the corresponding `TgUser` instance. If the user does not exist,
    the function returns `None`.

    Args:
        user_id (int): The unique identifier of the Telegram user to retrieve.

    Returns:
        TgUser | None: The user object if found, otherwise None.
    """
    with SessionLocal() as session:
        user = session.get(TgUser, user_id)
    return user


def create_user(user_id: int, first_name: str, last_name: str, username: str):
    """
    Create a new Telegram user entry in the database.

    This function initializes a `TgUser` object with the provided basic profile
    information, persists it to the database, and refreshes the instance to ensure
    all auto-generated fields are populated before returning it.

    Args:
        user_id (int): The user's Telegram ID, used as the primary key.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        username (str): The Telegram username of the user.

    Returns:
        TgUser: The newly created and fully persisted database record.
    """
    with SessionLocal() as session:
        user = TgUser(
            id=user_id, first_name=first_name, last_name=last_name, username=username
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def save_tokens(user_id: id, access: str, refresh: str, expiry: str):
    """
    Store or update Google OAuth tokens for a specific Telegram user.

    This function retrieves the user from the database, updates their Google
    access token, refresh token, and expiry timestamp, and commits the changes.
    It raises an exception if the user does not exist. This information is used
    to authenticate subsequent synchronization operations with Google Calendar.

    Args:
        user_id (int): The unique identifier of the Telegram user whose tokens are being updated.
        access (str): The Google OAuth access token.
        refresh (str): The Google OAuth refresh token.
        expiry (str): The expiration timestamp of the access token.

    Raises:
        ValueError: If the specified user cannot be found in the database.
    """
    with SessionLocal() as session:
        user = session.get(TgUser, user_id)
        if not user:
            raise ValueError("User not found")

        user.google_access_token = access
        user.google_refresh_token = refresh
        user.token_expiry = expiry

        session.commit()

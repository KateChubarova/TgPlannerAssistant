from shared.storage.db import SessionLocal
from shared.models.user import TgUser


def get_user(user_id: int) -> TgUser:
    with SessionLocal() as session:
        user = session.get(TgUser, user_id)
    return user


def create_user(user_id: int, first_name: str, last_name: str, username: str):
    with SessionLocal() as session:
        user = TgUser(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def save_tokens(user_id: id, access: str, refresh: str, expiry: str):
    with SessionLocal() as session:
        user = session.get(TgUser, user_id)
        if not user:
            raise ValueError("User not found")

        user.google_access_token = access
        user.google_refresh_token = refresh
        user.token_expiry = expiry

        session.commit()

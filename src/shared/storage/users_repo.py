from shared.db import SessionLocal
from shared.models.user import TgUser


def get_user(session, user_id: int) -> TgUser | None:
    return session.get(TgUser, user_id)


def create_user(session, user_id, first_name, last_name, username):
    user = TgUser(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username
    )
    session.add(user)
    return user


def save_tokens(user_id, access, refresh, expiry):
    with SessionLocal() as session:
        user = session.get(TgUser, user_id)
        if not user:
            raise ValueError("User not found")

        user.google_access_token = access
        user.google_refresh_token = refresh
        user.token_expiry = expiry

        session.commit()


def save_tokens(user):
    print("save tokens")
    with SessionLocal() as session:
        session.add(user)
        session.commit()

from sqlalchemy import TIMESTAMP, BigInteger, Column, String, Text, func

from shared.storage.db import Base


class TgUser(Base):
    __tablename__ = "tg_users"

    id = Column(BigInteger, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)

    google_access_token = Column(Text)
    google_refresh_token = Column(Text)
    token_expiry = Column(TIMESTAMP())

    created_at = Column(TIMESTAMP(), server_default=func.now())
    updated_at = Column(TIMESTAMP(), server_default=func.now(), onupdate=func.now())

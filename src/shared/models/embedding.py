from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ARRAY, TIMESTAMP, BigInteger, Column, String, Text

from shared.storage.db import Base


class Embedding(Base):
    __tablename__ = "tg_embeddings"

    id = Column(String, primary_key=True)

    event_id = Column(String)
    participants = Column(ARRAY(String))
    combined_text = Column(Text)
    calendar_name = Column(Text)
    updated_at = Column(TIMESTAMP())
    source = Column(Text)
    message = Column(VECTOR)
    status = Column(Text)
    location = Column(Text, nullable=True)
    end_ts = Column(TIMESTAMP(), nullable=True)
    start_ts = Column(TIMESTAMP(), nullable=True)
    user_id = Column(BigInteger)
    updated = Column(TIMESTAMP(timezone=True), nullable=True)
    organizer_email = Column(String, nullable=True)
    organizer_display_name = Column(String, nullable=True)

import os
from sqlalchemy import create_engine, MetaData, Table

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, future=True)
meta = MetaData()

tbl = Table("tg_embeddings", meta, autoload_with=engine, schema="public")

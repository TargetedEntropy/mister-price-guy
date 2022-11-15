from sqlalchemy import Column, Table, Integer, String
import datetime
from db.config import metadata, engine

now = datetime.datetime.utcnow


item = Table(
    "item",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String(255), nullable=True),
    Column("type", String(255), nullable=True),
    Column("level", Integer, nullable=True),
    Column("rarity", String(255), nullable=True),
    Column("vendor_value", Integer, nullable=True),
    Column("game_types", String(255), nullable=True),
    Column("flags", String(255), nullable=True),
    Column("restrictions", String(255), nullable=True),
    Column("chat_link", String(255), nullable=True),
    Column("icon", String(255), nullable=True),
   
)


metadata.create_all(bind=engine)



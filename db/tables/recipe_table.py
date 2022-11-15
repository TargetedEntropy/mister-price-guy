from sqlalchemy import Column, Table, Integer, String, Text
import datetime
from db.config import metadata, engine

now = datetime.datetime.utcnow


recipe = Table(
    "recipe",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(255), nullable=True),
    Column("output_item_id", Integer),
    Column("output_item_count", Integer),
    Column("time_to_craft_ms", Integer),
    Column("disciplines", Text),
    Column("min_rating", Integer),
    Column("flags", Text),
    Column("ingredients", Text),
    Column("chat_link", String(255), nullable=True),
    Column("guild_ingredients", Text)
)


metadata.create_all(bind=engine)



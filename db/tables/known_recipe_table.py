from sqlalchemy import Column, Table, Integer, String
import datetime
from db.config import metadata, engine

now = datetime.datetime.utcnow


known_recipe = Table(
    "known_recipe",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("player_id", String(255)),
)


metadata.create_all(bind=engine)



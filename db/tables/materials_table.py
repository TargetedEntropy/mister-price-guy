from sqlalchemy import Column, Table, Integer, String
import datetime
from db.config import metadata, engine

now = datetime.datetime.utcnow


material = Table(
    "material",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("player_id", String(255)),
    Column("category", Integer),
    Column("binding", String(255), nullable=True),
    Column("count", Integer)
)


metadata.create_all(bind=engine)



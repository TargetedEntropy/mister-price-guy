from sqlalchemy import Column, Integer, String
from db.config import Base


class Recipe(Base):
    __tablename__ = 'recipe'    
    id = Column(Integer, primary_key=True)
    type = Column(String)
    output_item_id = Column(Integer)
    output_item_count = Column(Integer)
    time_to_craft_ms = Column(Integer)
    disciplines = Column(String)
    min_rating = Column(Integer)
    flags = Column(String)
    ingredients = Column(String)
    chat_link = Column(String)
    guild_ingredients = Column(String)


    class Conifg:
        orm_mode = True

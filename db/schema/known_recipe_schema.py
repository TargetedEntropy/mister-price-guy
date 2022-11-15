from db.config import Base
from sqlalchemy import Column, Integer, String

class KnownRecipe(Base):
    __tablename__ = 'known_recipe'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    player_id = Column(String)
    
    class Conifg:
        orm_mode = True

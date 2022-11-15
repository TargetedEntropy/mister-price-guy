from db.config import Base
from sqlalchemy import Column, Integer, String

class Material(Base):
    __tablename__ = 'material'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    player_id = Column(String)
    category  = Column(Integer)
    binding  = Column(String)
    count = Column(Integer)
    
    
    class Conifg:
        orm_mode = True

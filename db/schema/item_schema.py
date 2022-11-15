from db.config import Base

from sqlalchemy import Column, Integer, String


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    type = Column(String)
    level = Column(Integer)
    rarity = Column(String)
    vendor_value = Column(Integer)
    game_types = Column(String)
    flags = Column(String)
    restrictions = Column(String)
    chat_link = Column(String)
    icon = Column(String)

    class Conifg:
        orm_mode = True

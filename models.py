from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#8104879861:AAEu8DGjBeocnwQ4xkyp48GOoC0kZshwf30
Base = declarative_base()
engine = create_engine('sqlite:///properties.db', echo=True)
Session = sessionmaker(bind=engine)


class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    district = Column(String, nullable=False)
    rooms = Column(Integer, nullable=False)
    area = Column(Integer, nullable=False)
    budget = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    phone_number = Column(String, nullable=False)
    photos = Column(Text, nullable=False)


def init_db():
    Base.metadata.create_all(engine)

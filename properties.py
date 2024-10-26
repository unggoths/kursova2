from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Property

STEPS = ['district', 'room', 'area', 'budget']

engine = create_engine('sqlite:///properties.db')
Session = sessionmaker(bind=engine)
session = Session()


def extract_number(text):
    import re
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None


def filter_properties(chat_id, user_data):
    filtered_properties = []
    user_selections = user_data[chat_id]
    user_rooms = extract_number(user_selections['room'])
    user_area = extract_number(user_selections['area'])
    user_budget = extract_number(user_selections['budget'])

    properties = session.query(Property).filter(
        Property.district == user_selections['district'],
        Property.rooms == user_rooms,
        Property.area <= user_area,
        Property.budget <= user_budget
    ).all()

    return properties

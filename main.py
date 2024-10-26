import os
import telebot
from telebot import types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Property
from keyboards import create_district_keyboard, get_keyboard, \
    create_budget_keyboard  # Імпортуємо функції з keyboards.py

# Підключення до бази даних SQLite
DATABASE_URL = "sqlite:///properties.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Ініціалізація Telegram бота
TOKEN = "8104879861:AAEu8DGjBeocnwQ4xkyp48GOoC0kZshwf30"
bot = telebot.TeleBot(TOKEN)

user_data = {}
STEPS = ['district', 'room', 'area', 'budget']


# Інші функції залишаються без змін
def get_prev_step(chat_id):
    current_index = STEPS.index(user_data[chat_id]['current_step'])
    return STEPS[max(0, current_index - 1)]


def send_filtered_properties(chat_id, filtered_properties):
    if not filtered_properties:
        bot.send_message(chat_id, "На жаль, за вашими критеріями нічого не знайдено. ☹️")
        return

    for prop in filtered_properties:
        message = (f"Опис: {prop.description}\n"
                   f"Район: {prop.district}\n"
                   f"Кімнат: {prop.rooms}\n"
                   f"Площа: {prop.area} кв.м\n"
                   f"Бюджет: {prop.budget} грн\n"
                   f"Контактний номер: {prop.phone_number}\n")
        bot.send_message(chat_id, message)

        photos = prop.photos.split('|')
        media_group = []
        for photo in photos:
            if os.path.exists(photo):
                media_group.append(types.InputMediaPhoto(open(photo, 'rb')))
            else:
                bot.send_message(chat_id, "[Фото недоступне]")

        if media_group:
            bot.send_media_group(chat_id, media=media_group)


def apply_filters(query, filter_name, filter_value):
    if filter_name == 'district':
        district = filter_value.split(' ')[0]  # Знімаємо емодзі для коректного порівняння
        return query.filter(Property.district == district)
    elif filter_name == 'room':
        rooms = int(filter_value.split('-')[0])
        return query.filter(Property.rooms == rooms)
    elif filter_name == 'area':
        if filter_value.isdigit():
            max_area = int(filter_value)
            return query.filter(Property.area <= max_area)
        elif 'від' in filter_value:
            min_area = int(filter_value.split(' ')[1])
            return query.filter(Property.area >= min_area)
    elif filter_name == 'budget':
        budget_value = int(filter_value.split(' ')[0])
        if 'від' in filter_value:
            return query.filter(Property.budget >= budget_value)
        else:
            return query.filter(Property.budget <= budget_value)
    return query


def filter_properties(session, user_data):
    query = session.query(Property)
    print(f"Фільтруємо за даними: {user_data}")

    for key in ['district', 'room', 'area', 'budget']:
        if key in user_data:
            filter_value = user_data[key]
            query = apply_filters(query, key, filter_value)
            print(f"Додаємо фільтр за {key}: {filter_value}")
            print(f"Поточний SQL запит: {query}")

    filtered_properties = query.all()
    print(f"Знайдені властивості: {filtered_properties}")
    return filtered_properties


def handle_choice(chat_id, data, message_id):
    current_step = user_data[chat_id]['current_step']
    user_data[chat_id][current_step] = data.split('_')[1]

    next_step_index = STEPS.index(current_step) + 1
    if next_step_index < len(STEPS):
        next_step = STEPS[next_step_index]
        user_data[chat_id]['current_step'] = next_step
        next_message = {
            "district": "Вкажіть кількість кімнат, яка вам потрібна.",
            "room": "Чудово, тепер вкажіть площу в квадратних метрах.",
            "area": "Тепер вкажіть Ваш бюджет."
        }
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Вибрано {data.split('_')[1]}. {next_message[current_step]}",
            reply_markup=get_keyboard(next_step)
        )
    else:
        session = Session()
        filtered_properties = filter_properties(session, user_data[chat_id])
        send_filtered_properties(chat_id, filtered_properties)
        session.close()


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == 'back':
        prev_step = get_prev_step(chat_id)
        user_data[chat_id]['current_step'] = prev_step
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"Повертаємось на крок: {prev_step}", reply_markup=get_keyboard(prev_step))
    else:
        handle_choice(chat_id, data, call.message.message_id)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'current_step': 'district'}
    welcome_message = ("👋 Привіт!"
                       " Ласкаво просимо до нашого ріелторського бота!\n"
                       "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті.\n"
                       
                       "В якому районі Ви плануєте винаймати квартиру? 🤔")
    bot.send_message(chat_id, welcome_message, reply_markup=create_district_keyboard())


@bot.message_handler(commands=['test'])
def handle_test(message):
    bot.send_message(message.chat.id, "Тестове повідомлення.")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('current_step') == 'area')
def handle_area(message):
    chat_id = message.chat.id
    area = message.text

    if not area.isdigit():
        bot.send_message(chat_id, "Будь ласка, введіть коректне значення площі житла.")
        return

    user_data[chat_id]['area'] = area
    user_data[chat_id]['current_step'] = 'budget'
    bot.send_message(chat_id, "Площа помешкання вказана. Тепер вкажіть Ваш бюджет.", reply_markup=create_budget_keyboard())


if __name__ == '__main__':
    bot.polling(none_stop=True)

import os
import telebot
from telebot import types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Property
from keyboards import create_district_keyboard, get_keyboard, \
    create_budget_keyboard, create_main_menu_keyboard

DATABASE_URL = "sqlite:///properties.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

TOKEN = "8104879861:AAEu8DGjBeocnwQ4xkyp48GOoC0kZshwf30"
bot = telebot.TeleBot(TOKEN)

user_data = {}
STEPS = ['district', 'room', 'area', 'budget']

def ensure_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'current_step': 'district'}

def get_prev_step(chat_id):
    current_index = STEPS.index(user_data[chat_id]['current_step'])
    return STEPS[max(0, current_index - 1)]

def send_filtered_properties(bot, chat_id, filtered_properties):
    if not filtered_properties:
        bot.send_message(chat_id, "На жаль, за вашими критеріями нічого не знайдено. ☹️",
                         reply_markup=create_main_menu_keyboard())
        return

    for prop in filtered_properties:
        caption = (f"📝 Опис: {prop.description}\n"
                   f"📍 Район: {prop.district}\n"
                   f"🛏️ Кімнат: {prop.rooms}\n"
                   f"📐 Площа: {prop.area} кв.м\n"
                   f"💵 Бюджет: {prop.budget} $\n"
                   f"📞 Контактний номер: {prop.phone_number}\n")

        photos = prop.photos.split('|')
        media_group = []
        for index, photo in enumerate(photos):
            if os.path.exists(photo):
                if index == 0:
                    # Add caption only to the first photo
                    media_group.append(types.InputMediaPhoto(open(photo, 'rb'), caption=caption))
                else:
                    media_group.append(types.InputMediaPhoto(open(photo, 'rb')))
            else:
                bot.send_message(chat_id, "[Фото недоступне ☹️]")

        if media_group:
            bot.send_media_group(chat_id, media=media_group)

def apply_filters(query, filter_name, filter_value):
    if filter_name == 'district':
        district = filter_value.strip()
        return query.filter(Property.district.ilike(district))
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
        filter_value = filter_value.lower().strip()
        if filter_value.startswith('до'):
            try:
                budget_value = int(filter_value.split(' ')[1])
                return query.filter(Property.budget <= budget_value)
            except ValueError:
                pass
        elif filter_value.startswith('від'):
            try:
                budget_value = int(filter_value.split(' ')[1])
                return query.filter(Property.budget >= budget_value)
            except ValueError:
                pass
        else:
            try:
                budget_value = int(filter_value)
                return query.filter(Property.budget <= budget_value)
            except ValueError:
                pass
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
    ensure_user_data(chat_id)
    current_step = user_data[chat_id]['current_step']
    selection = data.split('_')[1]
    user_data[chat_id][current_step] = selection

    room_messages = {
        '1': '1-кімнатну',
        '2': '2-кімнатну',
        '3': '3-кімнатну',
        '4': '4-кімнатну'
    }

    selected_message = room_messages.get(selection, selection)

    next_step_index = STEPS.index(current_step) + 1
    if next_step_index < len(STEPS):
        next_step = STEPS[next_step_index]
        user_data[chat_id]['current_step'] = next_step
        next_message = {
            "district": "Вкажіть кількість кімнат, яка Вам потрібна 🏠 ",
            "room": "Чудово, тепер вкажіть площу в квадратних метрах 📏",
            "area": "Тепер вкажіть Ваш бюджет 💸"
        }
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Вибрано {selected_message}. {next_message[current_step]}",
            reply_markup=get_keyboard(next_step)
        )
    else:
        session = Session()
        filtered_properties = filter_properties(session, user_data[chat_id])
        send_filtered_properties(bot, chat_id, filtered_properties)
        session.close()

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    data = call.data

    ensure_user_data(chat_id)

    if data == 'main_menu':
        user_data[chat_id] = {'current_step': 'district'}
        welcome_message = ("👋 Привіт! Ласкаво просимо до нашого ріелторського бота!\n"
                           "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті\n\n"
                           "В якому районі Ви плануєте винаймати квартиру? 🤔")
        bot.send_message(chat_id, welcome_message, reply_markup=create_district_keyboard())
    elif data == 'back':
        prev_step = get_prev_step(chat_id)
        user_data[chat_id]['current_step'] = prev_step
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"Повертаємось на крок: {prev_step}", reply_markup=get_keyboard(prev_step))
    else:
        handle_choice(chat_id, data, call.message.message_id)

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id] = {'current_step': 'district'}
    welcome_message = ("👋 Привіт! Ласкаво просимо до нашого ріелторського бота!\n"
                       "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті\n\n"
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
        bot.send_message(chat_id, "🤨 Будь ласка, введіть коректне значення площі житла.")
        return

    user_data[chat_id]['area'] = area
    user_data[chat_id]['current_step'] = 'budget'
    bot.send_message(chat_id, "📏 Площа помешкання вказана. Тепер вкажіть Ваш бюджет.",
                     reply_markup=create_budget_keyboard())

if __name__ == '__main__':
    bot.polling(none_stop=True)

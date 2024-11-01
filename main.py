import os
import telebot
from telebot import types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Property, District, Contact, PropertyContact, Photo  # Import necessary models
from keyboards import create_district_keyboard, get_keyboard, create_budget_keyboard, create_main_menu_keyboard

DATABASE_URL = "sqlite:///properties.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

TOKEN = "8104879861:AAEu8DGjBeocnwQ4xkyp48GOoC0kZshwf30"  # Змініть на свій токен
bot = telebot.TeleBot(TOKEN)

user_data = {}
STEPS = ['district', 'room', 'area', 'budget']
STEP_MESSAGES = {
    'district': "Вибору району 📍",
    'room': "Вибору кількості кімнат 🔑",
    'area': "Введення площі 📐",
    'budget': "Вибору бюджету 💵"
}


def ensure_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'current_step': 'district'}


def get_prev_step(chat_id):
    current_index = STEPS.index(user_data[chat_id]['current_step'])
    return STEPS[max(0, current_index - 1)]


def send_filtered_properties(bot, chat_id, filtered_properties, session):
    if not filtered_properties:
        bot.send_message(
            chat_id,
            "На жаль, за вашими критеріями нічого не знайдено. ☹️",
            reply_markup=create_main_menu_keyboard()
        )
        return

    for prop in filtered_properties:
        contact_query = session.query(Contact.phone_number).join(PropertyContact).filter(
            PropertyContact.property_id == prop.property_id)
        contact_number = contact_query.first().phone_number if contact_query.count() > 0 else "Немає контактів"

        caption = (f"📝 Опис: {prop.description}\n"
                   f"📍 Район: {prop.district.district_name}\n"
                   f"🔑 Кімнат: {prop.rooms}\n"
                   f"📐 Площа: {prop.area} кв.м\n"
                   f"💵 Бюджет: {prop.budget} $\n"
                   f"📞 Контактний номер: {contact_number}\n")

        photos = prop.photos if prop.photos else []
        files = []
        media_group = []  # Initialize media_group as an empty list
        try:
            for index, photo in enumerate(photos):
                photo_path = getattr(photo, 'photo_path', None)
                if photo_path and os.path.exists(photo_path):
                    file = open(photo_path, 'rb')
                    files.append(file)
                    if index == 0:
                        media_group.append(types.InputMediaPhoto(file, caption=caption))
                    else:
                        media_group.append(types.InputMediaPhoto(file))
                else:
                    bot.send_message(chat_id, "[Фото недоступне ☹️]")

            if media_group:
                bot.send_media_group(chat_id, media=media_group)
        finally:
            for file in files:
                file.close()

    bot.send_message(
        chat_id,
        "✅ Це всі знайдені квартири за вашими критеріями.",
        reply_markup=create_main_menu_keyboard()
    )


def apply_filters(query, filter_name, filter_value):
    if filter_name == 'district':
        district_name = filter_value.strip()
        query = query.join(District).filter(District.district_name.ilike(f"%{district_name}%"))
    elif filter_name == 'room':
        rooms = int(filter_value)
        query = query.filter(Property.rooms == rooms)
    elif filter_name == 'area':
        try:
            if 'до ' in filter_value:
                max_area = float(filter_value.replace("до ", "").replace(",", "").strip())
                query = query.filter(Property.area <= max_area)
            elif 'від ' in filter_value:
                min_area = float(filter_value.replace("від ", "").replace(",", "").strip())
                query = query.filter(Property.area >= min_area)
            else:
                max_area = float(filter_value)
                query = query.filter(Property.area <= max_area)
        except ValueError:
            pass  # Handle the case where the conversion to float fails
    elif filter_name == 'budget':
        try:
            if 'до ' in filter_value:
                max_budget = float(filter_value.replace("до ", "").replace(",", "").strip())
                query = query.filter(Property.budget <= max_budget)
            elif 'від ' in filter_value:
                min_budget = float(filter_value.replace("від ", "").replace(",", "").strip())
                query = query.filter(Property.budget >= min_budget)
            else:
                max_budget = float(filter_value)
                query = query.filter(Property.budget <= max_budget)
        except ValueError:
            pass  # Handle the case where the conversion to float fails
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

    emoji_mapping = {
        'district': '📍',
        'room': '🔑',
        'area': '📐',
        'budget': '💵'
    }

    step_messages = {
        'district': "Тепер вкажіть скільки кімнат Вам потрібно 🔑",
        'room': "Чудово, тепер вкажіть площу помешкання, яка Вам потрібна 📐\n\n"
                "🔴 Примітка: Введіть площу цілим числом, і бот підбере квартири з такою ж або меншою площею.",
        'area': "Тепер вкажіть Ваш бюджет 💵"
    }

    room_messages = {
        '1': '1 кімната',
        '2': '2 кімнати',
        '3': '3 кімнати',
        '4': '4 кімнати'
    }

    selected_message = room_messages.get(selection, selection)

    next_step_index = STEPS.index(current_step) + 1
    if next_step_index < len(STEPS):
        next_step = STEPS[next_step_index]
        user_data[chat_id]['current_step'] = next_step

        emoji = emoji_mapping.get(current_step, '')  # Update emoji
        next_step_message = step_messages.get(current_step, STEP_MESSAGES[next_step])

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Вибрано: {selected_message} {emoji}\n{next_step_message}",
            reply_markup=get_keyboard(next_step) if next_step in ['district', 'room', 'budget'] else None
        )
    else:
        session = Session()
        filtered_properties = filter_properties(session, user_data[chat_id])
        send_filtered_properties(bot, chat_id, filtered_properties, session)
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
                              text=f"🔴 Повертаємось на крок: {STEP_MESSAGES[prev_step]}",
                              reply_markup=get_keyboard(prev_step))
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
        bot.send_message(chat_id, "🤨 Будь ласка, введіть ціле число для значення площі житла.")
        return

    user_data[chat_id]['area'] = area
    user_data[chat_id]['current_step'] = 'budget'
    bot.send_message(chat_id, "Площа помешкання вказана 📐\n"
                              "Тепер вкажіть Ваш бюджет 💵",
                     reply_markup=create_budget_keyboard())


if __name__ == '__main__':
    bot.polling(none_stop=True)

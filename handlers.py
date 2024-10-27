import os
from telebot import TeleBot, types
import properties

user_data = {}


def get_prev_step(chat_id):
    current_index = properties.STEPS.index(user_data[chat_id]['current_step'])
    return properties.STEPS[max(0, current_index - 1)]


def send_filtered_properties(bot, chat_id, filtered_properties):
    if not filtered_properties:
        bot.send_message(chat_id, "На жаль, за вашими критеріями нічого не знайдено. ☹️")
        return
    for property in filtered_properties:
        message = (f"Опис: {property['description']}\n"
                   f"Район: {property['district']}\n"
                   f"Кімнат: {property['rooms']}\n"
                   f"Площа: {property['area']}м²\n"
                   f"Бюджет: ${property['budget']}\n"
                   f"Контактний номер: {property['phone_number']}\n")
        bot.send_message(chat_id, message)

        media_group = []
        for photo in property['photos']:
            if os.path.exists(photo):
                media_group.append(types.InputMediaPhoto(open(photo, 'rb')))
            else:
                bot.send_message(chat_id, "[Фото недоступне]")

        if media_group:
            bot.send_media_group(chat_id, media=media_group)


def handle_choice(bot, chat_id, data, message_id):
    current_step = user_data[chat_id]['current_step']
    user_data[chat_id][current_step] = data.split('_')[1]

    next_step_index = properties.STEPS.index(current_step) + 1
    if next_step_index < len(properties.STEPS):
        next_step = properties.STEPS[next_step_index]
        user_data[chat_id]['current_step'] = next_step
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=f"Вибрано {data.split('_')[1]}. Ваш наступний вибір:",
                              reply_markup=get_keyboard(next_step))
    else:
        filtered_properties = properties.filter_properties(chat_id, user_data)
        send_filtered_properties(bot, chat_id, filtered_properties)


def handle_query(call, bot):
    chat_id = call.message.chat.id
    data = call.data
    if data == 'back':
        prev_step = get_prev_step(chat_id)
        user_data[chat_id]['current_step'] = prev_step
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"Повертаємось на крок: {prev_step}", reply_markup=get_keyboard(prev_step))
    else:
        handle_choice(bot, chat_id, data, call.message.message_id)


def handle_start(message, bot):
    chat_id = message.chat.id
    user_data[chat_id] = {'current_step': 'district'}
    welcome_message = ("Привіт!👋\n"
                       "Ласкаво просимо до нашого ріелторського бота!🏡\n"
                       "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті.\n"
                       "В якому районі Ви плануєте мешкати?🤔")
    bot.send_message(chat_id, welcome_message, reply_markup=create_district_keyboard())


def handle_test(message, bot):
    bot.send_message(message.chat.id, "Тестове повідомлення.")


def create_district_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    districts = ["Сихівський район 🌳", "Галицький район 🏰", "Залізничний район 🚉", "Франківський район 🏞️",
                 "Личаківський район 🍀", "Шевченківський район 🌆"]
    buttons = [types.InlineKeyboardButton(text=district, callback_data=f'district_{district}') for district in
               districts]
    keyboard.add(*buttons)
    return keyboard


def create_room_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    rooms = ["1-кімнатна", "2-кімнатна", "3-кімнатна", "4-кімнатна"]
    buttons = [types.InlineKeyboardButton(text=room, callback_data=f'room_{room}') for room in rooms]
    keyboard.add(*buttons)
    return keyboard


def create_area_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    areas = ["до 30 кв.м", "до 40 кв.м", "до 50 кв.м", "до 70 кв.м", "до 90 кв.м", "до 110 кв.м", "до 130 кв.м",
             "до 150 кв.м", "до 170 кв.м", "до 190 кв.м", "від 200 кв.м"]
    buttons = [types.InlineKeyboardButton(text=area, callback_data=f'area_{area}') for area in areas]
    keyboard.add(*buttons)
    return keyboard


def create_budget_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    budgets = ["до 400$", "до 500$", "до 600$", "до 700$", "до 800$", "до 900$", "до 1000$", "до 1100$",
               "до 1200$", "до 1300$", "до 1400$", "від 1400$"]
    buttons = [types.InlineKeyboardButton(text=budget, callback_data=f'budget_{budget}') for budget in budgets]
    keyboard.add(*buttons)
    return keyboard


def get_keyboard(step):
    keyboard = types.InlineKeyboardMarkup()
    if step != 'district':
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))

    if step == 'district':
        return create_district_keyboard()
    elif step == 'room':
        return create_room_keyboard()
    elif step == 'area':
        return create_area_keyboard()
    elif step == 'budget':
        return create_budget_keyboard()

    return keyboard

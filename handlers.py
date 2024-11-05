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

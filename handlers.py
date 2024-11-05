import properties
from models import Contact, PropertyContact
from keyboards import create_district_keyboard, get_keyboard_by_step, create_budget_keyboard, create_main_menu_keyboard

user_data = {}


def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        chat_id = call.message.chat.id
        data = call.data
        properties.ensure_user_data(chat_id, user_data)

        if data == 'main_menu':
            user_data[chat_id] = {'current_step': 'district'}
            welcome_message = ("👋 Привіт! Ласкаво просимо до нашого ріелторського бота!\n"
                               "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті\n\n"
                               "В якому районі Ви плануєте винаймати квартиру? 🤔")
            bot.send_message(chat_id, welcome_message, reply_markup=create_district_keyboard())
        elif data == 'back':
            prev_step = properties.get_prev_step(chat_id, user_data)
            user_data[chat_id]['current_step'] = prev_step
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=f"🔴 Повертаємось на крок: {properties.STEP_MESSAGES[prev_step]}",
                                  reply_markup=get_keyboard_by_step(prev_step))
        else:
            properties.handle_choice(bot, chat_id, data, call.message.message_id, user_data)

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        chat_id = message.chat.id
        properties.ensure_user_data(chat_id, user_data)
        user_data[chat_id] = {'current_step': 'district'}
        welcome_message = ("👋 Привіт! Ласкаво просимо до нашого ріелторського бота!\n"
                           "Ми тут, щоб допомогти Вам знайти ідеальне житло в ідеальному місті\n\n"
                           "В якому районі Ви плануєте винаймати квартиру? 🤔")
        bot.send_message(chat_id, welcome_message, reply_markup=create_district_keyboard())

    @bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('current_step') == 'area')
    def handle_area(message):
        chat_id = message.chat.id
        area = message.text

        if not area.isdigit():
            bot.send_message(chat_id, "🤨 Будь ласка, введіть ціле число для значення площі житла.")
            return

        properties.handle_area_step(bot, chat_id, area, user_data)

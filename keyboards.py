from telebot import types


def create_district_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    districts = ["Сихівський район", "Галицький район", "Залізничний район", "Франківський район", "Личаківський район",
                 "Шевченківський район"]
    buttons = [types.InlineKeyboardButton(text=district, callback_data=f'district_{district}') for district in
               districts]
    keyboard.add(*buttons)
    return keyboard


def create_room_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    rooms = ["1", "2", "3", "4"]
    buttons = [types.InlineKeyboardButton(text=room + "-кімнатна", callback_data=f'room_{room}') for room in rooms]
    keyboard.add(*buttons)
    return keyboard


def create_budget_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    budgets = ["400", "500", "600", "700", "800", "900", "1000"]
    buttons = [types.InlineKeyboardButton(text=budget + " $", callback_data=f'budget_{budget}') for budget in budgets]
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
    elif step == 'budget':
        return create_budget_keyboard()

    return keyboard

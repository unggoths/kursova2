from telebot import types


def create_district_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    districts = ["Сихівський район", "Галицький район", "Залізничний район", "Франківський район", "Личаківський район",
                 "Шевченківський район"]
    buttons = [types.InlineKeyboardButton(text=district, callback_data=f'district_{district}') for district in
               districts]
    keyboard.add(*buttons)
    return keyboard


def create_main_back_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    main_menu_button = types.InlineKeyboardButton(text="На головну", callback_data='main_menu')
    back_button = types.InlineKeyboardButton(text="Назад", callback_data='back')
    keyboard.add(main_menu_button, back_button)
    return keyboard


def create_main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("На головну", callback_data="main_menu")
    keyboard.add(button)
    return keyboard


def create_room_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    rooms = ["1", "2", "3", "4"]
    buttons = [types.InlineKeyboardButton(text=room + "-кімнатна", callback_data=f'room_{room}') for room in rooms]
    back_button = types.InlineKeyboardButton(text="Назад", callback_data='back')
    keyboard.add(*buttons)
    keyboard.add(back_button)
    return keyboard


def create_budget_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    budgets = ["до 400", "до 500", "до 600", "до 700", "до 800", "до 900", "до 1000", "від 1000"]
    buttons = [types.InlineKeyboardButton(text=budget + " $", callback_data=f'budget_{budget}') for budget in budgets]
    back_button = types.InlineKeyboardButton(text="Назад", callback_data='back')
    keyboard.add(*buttons)
    keyboard.add(back_button)
    return keyboard


def get_keyboard(step):
    if step == 'district':
        return create_district_keyboard()
    elif step == 'room':
        return create_room_keyboard()
    elif step == 'area':
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton(text="Назад", callback_data='back')
        keyboard.add(back_button)
        return keyboard
    elif step == 'budget':
        return create_budget_keyboard()

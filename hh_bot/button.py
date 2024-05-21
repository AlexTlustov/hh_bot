from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_keyboard_start():
    hh_keyboard = [[
        InlineKeyboardButton("Погода", callback_data='weather'), 
        InlineKeyboardButton("Списки", callback_data='my_list'),
        InlineKeyboardButton("Шоу", callback_data='my_show'),
        InlineKeyboardButton("Бюбджет", callback_data='budget'),
        InlineKeyboardButton("Справка", callback_data='help')
        ]]
    reply_markup = InlineKeyboardMarkup(hh_keyboard)
    return reply_markup

def get_keyboard_plist():
    hh_keyboard = [[
        InlineKeyboardButton("Все списки", callback_data='all_plist'), 
        InlineKeyboardButton("Добавить список", callback_data='plist'),
        InlineKeyboardButton("Последний список", callback_data='see_last_plist'),
        InlineKeyboardButton("В начало", callback_data='start')
        ]]
    reply_markup = InlineKeyboardMarkup(hh_keyboard)
    return reply_markup

def get_keyboard_video():
    hh_keyboard = [[
        InlineKeyboardButton("Все шоу", callback_data='all_show'), 
        InlineKeyboardButton("Добавить шоу", callback_data='add_new_show'),
        InlineKeyboardButton("Новые шоу", callback_data='new_show'),
        InlineKeyboardButton("В начало", callback_data='start')
        ]]
    reply_markup = InlineKeyboardMarkup(hh_keyboard)
    return reply_markup
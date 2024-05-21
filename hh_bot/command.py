import asyncio
import telebot
import time
from database.db import get_all_plist, get_last_plist, get_last_products, get_user_id, update_product_prices, writing_to_product, writing_to_product_list, writing_to_users
from hh_bot.button import *
from hh_bot.utils import created_product_json
from openweathermap.weather import get_weather
from parser_price import get_price_for_product
from settings import KEY_BOT, KEY_WEATHER
from yandex.yandex_map import get_city
from geopy.geocoders import Nominatim
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes


key_weather = KEY_WEATHER
geolocator = Nominatim(user_agent="https://t.me/myHoHeBot")
bot = telebot.TeleBot(KEY_BOT)

VIDEO_SELECTION, PLIST_SELECTION, CITY_SELECTION, START_STATE = range(4)

# Обрабочтик команды TEST
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message_dict = update.effective_message.to_dict()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_dict, reply_markup=None)

# Обрабочтик команды LOCATION_WEATHER
async def location_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    latitude = message_dict['location']['latitude']
    longitude = message_dict['location']['longitude']
    location = geolocator.reverse(f"{latitude}, {longitude}")
    address = location.address
    city = get_city(address)
    weather_info = get_weather(city)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=weather_info)
    reply_keyboard = get_keyboard_start()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ещё что-то надо? Не стесняйся...", reply_markup=reply_keyboard)
    return START_STATE

# Обрабочтик команды START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_keyboard_start()
    message_dict = update.effective_message.to_dict()
    if message_dict['from']['first_name'] == message_dict['chat']['first_name']:
        user_id = message_dict['from']['id']
        first_name = message_dict['from']['first_name']
        last_name = message_dict['from']['last_name']
    else:
        user_id = message_dict['chat']['id']
        first_name = message_dict['chat']['first_name']
        last_name = message_dict['chat']['last_name']
    db_user_id = get_user_id(user_id)
    if not db_user_id:
        writing_to_users(user_id, first_name, last_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{first_name}, я готов тебе помочь.\nВыбирай что тебе нужно?', reply_markup=reply_keyboard)
    return START_STATE

# Обрабочтик команды HELP
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('readme.txt', 'r', encoding='utf-8') as file:
            help_text = file.read()
    except FileNotFoundError:
        help_text = 'К сожалению, файл readme.txt не найден.'
    second_text = f'Ещё читаем?'
    final_text =  f'Теперь жми /start и начнем заново.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
    time.sleep(5)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=second_text)
    time.sleep(2)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=final_text)
    return START_STATE
    
# Обрабочтик команды WEATHER
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'Пожалуйста, укажите город или отправьте данные геолокации.\n\n(данные геолокации можно отправить через "скрепку")', 
                                   reply_markup=ReplyKeyboardRemove())
    return CITY_SELECTION

# Обрабочтик CITY_WEATHER
async def city_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    city = message_dict.get("text")
    if len(city) > 3 and len(city) < 20 and not any(char.isdigit() for char in city) and city.isalnum():
        weather_info = get_weather(city)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=weather_info)
        reply_keyboard = get_keyboard_start() 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ещё что-то надо? Не стесняйся...", reply_markup=reply_keyboard)
        return START_STATE
    else:
        msg_error = f'{city} - это некорректное название города.\n\nПридется начать сначала указав существующий город.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg_error)
        reply_keyboard = get_keyboard_start()  # Получаем клавиатуру с кнопками
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ещё что-то надо? Не стесняйся...", reply_markup=reply_keyboard)
        return START_STATE

# Обрабочтик TEXT
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass 

# Обрабочтик команды CANCEL
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_error = f'Не знаю что тебе не понравилось... давай попробуем еще раз.'
    reply_keyboard = get_keyboard_start()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg_error, reply_markup=reply_keyboard)
    return START_STATE

# Обрабочтик команды PLIST
async def plist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'Хорошо, напиши список покупок.\nВ списке каждый новый элемент нужно указывать с новой строки.\n\nНапример:\nХлеб\nПорошок\nФиле курицы 0.5\nПомидоры 1\n\n\nЭто уже не имеет смысла? Жми /cancel', 
                                   reply_markup=ReplyKeyboardRemove())
    return PLIST_SELECTION

# Обрабочтик команды PLIST
async def my_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_keyboard_plist()
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'Давай объясню, что ты можешь здесь:\n - Все списки - посмотреть все свои списки продуктов\n - Добавить список - создать и записать новый список продуктов\n - Показать последний - посмотреть последний список продуктов\n - В начало - вернутся в начало /start', 
                                   reply_markup=reply_keyboard)
    return START_STATE

# Получение цен товаров
async def get_prices(event):
    data = get_price_for_product()
    update_product_prices(data)
    event.set()

# Обрабочтик команды PLIST
async def add_plist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    plist = message_dict.get("text")
    user_id = message_dict['from']['id']
    bd_user_id = get_user_id(user_id)
    if bd_user_id == False:
        first_name = message_dict['from']['first_name']
        last_name = message_dict['from']['last_name']
        writing_to_users(user_id, first_name, last_name) 
        bd_user_id = get_user_id(user_id)  
    try:
        writing_to_product_list()
        num_list = get_last_plist()
        json_plist = created_product_json(plist, num_list, bd_user_id)
        writing_to_product(json_plist)
        reply_keyboard = get_keyboard_plist() 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Записал этот список под номером {num_list}.\nЦены товаров будут обновлены через 5 минут.\nЕщё что-то надо? Не стесняйся...", reply_markup=reply_keyboard)
        event = asyncio.Event()
        task = asyncio.create_task(get_prices(event))
        await event.wait()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Цены товаров обновлены.")
        return START_STATE
    except:
        reply_keyboard = get_keyboard_plist() 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Что-то пошло не так...", reply_markup=reply_keyboard)
        return START_STATE

# Обрабочтик команды ALL_PLIST
async def all_plist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    user_id = message_dict['chat']['id']
    bd_user_id = get_user_id(user_id)
    my_all_plist = get_all_plist(bd_user_id)
    sum_price = []
    for element in my_all_plist:
        list_id = element
        product_list = my_all_plist[element]
        text_answer = f'В списке №{list_id} следующие продукты:\n'
        for product in product_list:
            name = product['name']
            quantity = product['quantity']
            price = product['price']
            sum_price.append(price)
            similar_name = product['similar_name']
            text_answer += f'{name} {quantity} кол. {price} руб.\n-{similar_name}\n\n'
        text_answer += f'Итого сумма: {sum(sum_price)} руб.\n'
        sum_price.clear()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_answer)
        time.sleep(0.5)
    reply_keyboard = get_keyboard_plist()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Это все списки товаров которые есть.\nЕщё что-то надо? Не стесняйся...', reply_markup=reply_keyboard)

# Обрабочтик команды SEE_LAST_PLIST
async def see_last_plist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    user_id = message_dict['chat']['id']
    last_plist = get_last_plist()
    text_answer = get_last_products(last_plist, user_id)
    reply_keyboard = get_keyboard_plist()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_answer)
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Ещё что-то надо? Не стесняйся...', reply_markup=reply_keyboard)

# Обрабочтик ALL_SHOW
async def all_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# Обрабочтик ADD_SHOW
async def add_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# Обрабочтик NEW_SHOW
async def new_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# Обрабочтик MY_SHOW
async def my_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_keyboard_video()
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'Давай объясню, что ты можешь здесь:\n - Все шоу - посмотреть все отслеживаемые шоу\n - Добавить шоу - добавить в отслеживание новое шоу\n - Новые шоу - узнать о новых сериях своих шоу\n - В начало - вернутся в начало /start', 
                                   reply_markup=reply_keyboard)
    return START_STATE

# Обрабочтик команды PLIST
async def add_new_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'Хорошо, напиши название нового шоу.\nНазвание должно быть таким же как оно есть на YouTube или VKvideo\n\nНапример:\nТейбл Тайм\n\n\nЭто уже не имеет смысла? Жми /cancel', 
                                   reply_markup=ReplyKeyboardRemove())
    return VIDEO_SELECTION

# Обрабочтик BUDGET
async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_dict = update.effective_message.to_dict()
    first_name = message_dict['chat']['first_name']
    reply_keyboard = get_keyboard_start()
    url = 'https://docs.google.com/spreadsheets/d/1wL3M35c5r1XeMPQA3a6Vri_96qBPcBzyEXuIZZEqXv8/edit#gid=69021765'
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f'{first_name} бюджет ведется в Google Tab. Вот ссылка:\n{url}', 
                                   reply_markup=reply_keyboard)
    return START_STATE

# Обрабочтик BUTTON
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await help(update, context)
        return START_STATE
    elif query.data == 'weather':
        await weather(update, context)
        return CITY_SELECTION
    elif query.data == 'plist':
        await plist(update, context)
        return PLIST_SELECTION
    elif query.data == 'all_plist':
        await all_plist(update, context)
        return START_STATE
    elif query.data == 'start':
        await start(update, context)
        return START_STATE
    elif query.data == 'my_list':
        await my_list(update, context)
        return START_STATE
    elif query.data == 'see_last_plist':
        await see_last_plist(update, context)
        return START_STATE
    elif query.data == 'all_show':
        await all_show(update, context)
        return START_STATE
    elif query.data == 'new_show':
        await new_show(update, context)
        return START_STATE
    elif query.data == 'my_show':
        await my_show(update, context)
        return START_STATE
    elif query.data == 'add_new_show':
        await add_new_show(update, context)
        return VIDEO_SELECTION
    elif query.data == 'budget':
        await budget(update, context)
        return START_STATE
    
    return START_STATE


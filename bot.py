import requests, wikipedia, telebot
from telebot import types
from datetime import datetime
from deep_translator import GoogleTranslator
city_flag = False
wiki_flag = False


def bank(data):
    db = data.json()
    keys = db['Valute'].keys()
    temp = ''
    for key in keys:
        val, pre_cost, coast = key, round(db['Valute'][key]['Previous'], 2), round(db['Valute'][key]['Value'], 2)
        if val in ('EUR','USD'):
            temp += f'🟢{val} {pre_cost}→{coast}' + '\n'
        else:
            temp += f'🔹{val} {pre_cost}→{coast}' + '\n'
    return temp


def get_weather(city):
    city_ru = GoogleTranslator(source='ru', target='en').translate(city)
    params = {'appid': api_key, 'q': city_ru}
    r_weather = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
    d = r_weather.json()
    Co = round(d['main']['temp'] - 273.15)
    Co_human = round(d['main']['feels_like'] - 273.15)
    humidity = str(d['main']['humidity'])
    pressure = str(d['main']['pressure'])
    wind = d['wind']['speed']
    sunrise = d['sys']['sunrise']
    sunset = d['sys']['sunset']
    weather = d['weather'][0]['description']
    weather_ru = GoogleTranslator(source='en', target='ru').translate(weather)
    sunrise = datetime.fromtimestamp(sunrise).time()
    sunset = datetime.fromtimestamp(sunset).time()
    return f'''
    🌐Город {city}
    🧭{weather_ru.capitalize()}
    🌡Температура {Co}°C
    🌡Ощущается как {Co_human}°C
    💧Влажность {humidity}%
    💢Атмосферное давление {pressure}гПа
    💨Скорость ветра {wind}м/с
    🌅Время восхода {sunrise}
    🌄Время заката {sunset}'''


def get_wiki(word):
    try:
        wikipedia.set_lang("ru")
        page = wikipedia.page(word)
        s = page.content[:1000]
        text = s.split('.')[:3]
        return '.'.join(text)+'.'
    except Exception as error:
        return 'Спроси что-нибуть другое'


token = "5286329173:AAHsGXkLDZLVS-rLXdSvu7HdoKzlK8ieI3Q"
api_key = "b847bd80878220877cd07bce3b091fcd"
r_bank = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('/button')
    item2 = types.KeyboardButton('/help')
    markup.row(item1)
    markup.row(item2)
    bot.send_message(message.chat.id, 'Привет', reply_markup=markup)


@bot.message_handler(commands=['help'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup()
    item = types.KeyboardButton('/button')
    markup.row(item)
    bot.send_message(message.chat.id, '''Сейчас...\n/start - Перезапустить бота\n/button - Запустить бота\n/help - Помощь
    
                                      ''', reply_markup=markup)

@bot.message_handler(commands=['button'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Валюты")
    item2 = types.KeyboardButton("Погода в вашем городе")
    item3 = types.KeyboardButton("Справочник слов из википедии")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    bot.send_message(message.chat.id, 'Не вопрос', reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):
    global city_flag
    global wiki_flag
    if message.text == "Валюты":
        answer = bank(r_bank)
        bot.send_message(message.chat.id, answer)

    elif message.text == "Погода в вашем городе":
        bot.send_message(message.chat.id, 'В каком городе?')
        city_flag = True

    elif message.text == "Справочник слов из википедии":
        bot.send_message(message.chat.id, 'Напиши слово')
        wiki_flag = True

    elif city_flag:
        answer = get_weather(message.text)
        bot.send_message(message.chat.id, answer)
        city_flag = False

    elif wiki_flag:
        answer = get_wiki(message.text)
        bot.send_message(message.chat.id, answer)
        wiki_flag = False
    else:
        bot.reply_to(message, "Что?")
        pass


bot.infinity_polling()

import requests
from pycbrf import ExchangeRates
import datetime
from keyboards import client_keyboards
from database import Postgres
from create_bot import bot
import atexit

connection = Postgres.open_connection()
atexit.register(Postgres.close_connection, connection)


@bot.message_handler(commands=['start'])
def start(message):
    connection = Postgres.open_connection()
    result_users = Postgres.list_user(connection)
    Postgres.close_connection(connection)
    if not result_users or message.chat.id not in list(result_users[0]):
        bot.send_message(message.chat.id, "Как я могу к вам обращаться?")
        bot.register_next_step_handler(message, add_name_database)
    else:
        bot.send_message(message.chat.id, "Вы уже авторизованы, если хотите сменить имя, напишите \n'/rename' ",
                         reply_markup=client_keyboards.markup_start)
    print(message)


def add_name_database(message):
    try:
        connection = Postgres.open_connection()
        Postgres.add_user(connection, message.text, message.chat.id, message.chat.username)
        Postgres.close_connection(connection)
        bot.send_message(message.chat.id, f'Приятно познакомиться, {message.text}!')
        bot.send_message(message.chat.id, "Выберите способ задания интересующего региона:",
                         reply_markup=client_keyboards.markup_region)
    except Exception as e:
        print("произошла ошибка", e)
        bot.send_message(message.chat.id, 'Слишком длинное имя. Пожалуйста, введите короткое имя.')
        bot.register_next_step_handler(message, add_name_database)


@bot.message_handler(func=lambda message: message.text == 'Используя список регионов')
def list_region(message):
    bot.send_message(message.chat.id, text='Список регионов', reply_markup=client_keyboards.choice_region())


@bot.message_handler(func=lambda message: message.text == 'Отправить геопозицию')
def list_region(message):
    bot.send_message(message.chat.id, text='Дурак', reply_markup=client_keyboards.choice_region())

@bot.message_handler(commands=['currency'])
def currency(message):
    currency = ExchangeRates(datetime.datetime.now())
    usd = round(currency.rates[13].rate, 2)
    eur = round(currency.rates[14].rate, 2)
    data = currency.date_received
    bot.send_message(message.chat.id,
                     f'Актуальный курс ЦБ РФ на {str(data).split(" ")[0]}  \n 🇺🇸 Курс доллара: {usd}руб. '
                     f'\n 🇪🇺 Курс евро: {eur}руб.', reply_markup=client_keyboards.markup_start)


@bot.message_handler(commands=['rename'])
def print_rename(message):
    # Отправляем сообщение без клавиатуры ответа
    bot.send_message(message.chat.id, "Введите имя, на которое хотите изменить",
                     reply_markup=client_keyboards.types.ReplyKeyboardRemove())
    # Зарегистрируем обработчик следующего шага
    bot.register_next_step_handler(message, rename)



def rename(message):
    if len(message.text) > 40:
        bot.send_message(message.chat.id, 'Слишком длинное имя. Пожалуйста, введите короткое имя.')
        bot.register_next_step_handler(message, rename)
    else:
        connection = Postgres.open_connection()
        Postgres.rename_user(connection, message.text, message.chat.id)
        Postgres.close_connection(connection)
        bot.send_message(message.chat.id, f"Ваше имя успешно сохранено, {message.text}")
        bot.send_message(message.chat.id, "Выберите что вас интересует:", reply_markup=client_keyboards.markup_start)


@bot.message_handler(commands=['change_region'])
def print_change_region(message):
    bot.send_message(message.chat.id, "Выберите способ задания интересующего региона:",
                       reply_markup=client_keyboards.markup_region)


def change_region(message):
    if message.text:
        region = message.text
        bot.send_message(message.chat.id, f"Ваш регион: {region}", reply_markup=client_keyboards.markup_category)
        connection = Postgres.open_connection()
        Postgres.change_region(connection, message.text, message.chat.id)
        Postgres.close_connection(connection)
    elif message.location:
        gps_location(message)


@bot.message_handler(commands=['help'])
def start(message):
    help_text = ("Данный чат-бот предназначен для просмотра новостей по заданной категории и региону.\n\n"
                 "Для изменения региона - /change_region \n Для вывода курса валют - /currency \n"
                 "Для того, чтобы изменить имя /rename \n")
    bot.send_message(message.chat.id, text=help_text, parse_mode='html',
                     reply_markup=client_keyboards.types.ReplyKeyboardRemove())



# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.text == 'Курс валют')
def reply_to_hello(message):
    currency(message)


@bot.message_handler(func=lambda message: message.text == 'Новости')
def news(message):
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=client_keyboards.markup_category)


@bot.callback_query_handler(func=lambda call: call.data in Postgres.get_list_region(connection))
def otv(call):
    Postgres.change_region(connection, call.data, call.message.chat.id)
    region = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f'Выбранный регион {region}!')
    bot.send_message(call.message.chat.id, "Выберите что вас интересует:", reply_markup=client_keyboards.markup_start)


@bot.message_handler(func=lambda message: message.text in ['Экономика', 'Политика', 'Общество', 'События'])
def categories(message):
    bot.send_message(chat_id=message.chat.id,text=f"Выбранная категория: {message.text}",
                     reply_markup=client_keyboards.markup_start, parse_mode="Markdown")
    connection = Postgres.open_connection()
    region = Postgres.get_region_user(connection, message.chat.id)
    Postgres.change_category(connection, message.text, message.chat.id)
    news_list = Postgres.get_news(connection, region, message.text)
    Postgres.close_connection(connection)
    page = 0
    if not news_list:
        bot.send_message(message.chat.id, "К сожалению, новостей по заданному региону и категории не найдено.")
    else:
        chunks = split_text(news_list[0][0])
        for chunk in chunks:
            # print(chunk)
            print(len(chunk))
            header, body = chunk.split('\n', 1)
            bot.send_message(message.chat.id,  f"*{header}*\n{body}",
                             reply_markup=client_keyboards.first_pagination(page), parse_mode="Markdown")
    print(region)


def split_text(text, max_length=4096):
    chunks = []
    len_url = 40
    print("Длина текста до изменения", len(text))
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        else:
            # Находим индекс ближайшего символа переноса строки,
            # который не превышает максимальную длину текста
            index = text.rfind('\n', 0, max_length - len_url)
            if index == -1:
                index = max_length  # Если символ переноса строки не найден, разбиваем по максимальной длине
            chunk = text[:index] + "\n"
            index_url = text.rfind('\n')
            chunk += text[index_url:]
            chunks.append(chunk)
            print("Длина текста после изменения", len(chunk))
            break
    return chunks


@bot.callback_query_handler(func=lambda call: call.data.startswith("NumberPage"))
def callback_handler(call):
    connection = Postgres.open_connection()
    region = Postgres.get_region_user(connection, call.message.chat.id)
    category_input = Postgres.get_category_news(connection, call.message.chat.id)
    news_list = Postgres.get_news(connection, region, category_input)
    Postgres.close_connection(connection)
    if not news_list:
        bot.send_message(call.message.chat.id, "К сожалению, новостей по заданному региону не найдено.")
    else:
        page = (call.data.split('_')[0]).split(':')[1]
        news_item = news_list[int(page)]
        chunks = split_text(news_item[0])
        for chunk in chunks:
            if news_item == news_list[-1]:
                header, body = chunk.split('\n', 1)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"*{header}*\n{body}",
                                      reply_markup=client_keyboards.last_pagination(page), parse_mode="Markdown")
            elif news_item == news_list[0]:
                header, body = chunk.split('\n', 1)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"*{header}*\n{body}",
                                      reply_markup=client_keyboards.first_pagination(page), parse_mode="Markdown")
            else:
                header, body = chunk.split('\n', 1)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"*{header}*\n{body}",
                                      reply_markup=client_keyboards.pagination(page), parse_mode="Markdown")

@bot.message_handler(content_types='text')
def text(message):
    print(message.text)
    bot.reply_to(message, text="Я не знаю такую команду")


@bot.message_handler(content_types=['location'])
def gps_location(message):
    if (message.reply_to_message is not None and
            message.reply_to_message.text == "Выберите способ задания интересующего региона:"):
        headers = {"accept": "application/json"}
        latitude = message.location.latitude
        longitude = message.location.longitude
        address = requests.get(f'https://eu1.locationiq.com/v1/reverse.php?key=pk.c8fe742bdf75864d0a31edef1671e54d&lat={latitude}&lon={longitude}&accept-language=rus&format=json', headers=headers).json()
        print(address['address'].get('state'))
        region = address['address'].get('state')
        bot.send_message(message.chat.id, f'Выбранный регион {region}!')
        bot.send_message(message.chat.id, "Выберите что вас интересует:", reply_markup=client_keyboards.markup_start)
        print(address)
        connection = Postgres.open_connection()
        Postgres.change_region(connection, region, message.chat.id)
        Postgres.close_connection(connection)
    else:
        bot.send_message(message.chat.id, "Я вас не понимаю", reply_markup=client_keyboards.markup_start)



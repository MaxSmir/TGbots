from telebot import types
from database import Postgres


markup_start = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
currency_btn = types.KeyboardButton('Курс валют')
news_btn = types.KeyboardButton('Новости')
markup_start.add(currency_btn, news_btn)

markup_category = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
category1_btn = types.KeyboardButton('Экономика')
category2_btn = types.KeyboardButton('Политика')
category3_btn = types.KeyboardButton('Общество')
category4_btn = types.KeyboardButton('События')
markup_category.add(category1_btn, category2_btn, category3_btn, category4_btn)

markup_region = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
region_manually_btn = types.KeyboardButton('Используя список регионов')
region_GPS_btn = types.KeyboardButton('Отправить геопозицию', request_location=True)
markup_region.add(region_manually_btn, region_GPS_btn)


def pagination(page):
    flipping_news = types.InlineKeyboardMarkup(row_width=3)
    last_news = types.InlineKeyboardMarkup()
    next_btn = types.InlineKeyboardButton(text='>>', callback_data="NumberPage\":" + str(int(page) + 1))
    page_number = types.InlineKeyboardButton(text=str(int(page) + 1), callback_data='page_number')
    previous_btn = types.InlineKeyboardButton(text='<<', callback_data="NumberPage\":" + str(int(page) - 1))
    flipping_news.add(previous_btn, page_number, next_btn)
    last_news.add(previous_btn, page_number)
    return flipping_news


def last_pagination(page):
    last_page = types.InlineKeyboardMarkup(row_width=3)
    page_number = types.InlineKeyboardButton(text=str(int(page) + 1), callback_data='page_number')
    previous_btn = types.InlineKeyboardButton(text='<<', callback_data="NumberPage\":" + str(int(page) - 1))
    last_page.add(previous_btn,page_number)
    return last_page


def first_pagination(page):
    first_page = types.InlineKeyboardMarkup(row_width=3)
    page_number = types.InlineKeyboardButton(text=str(int(page) + 1), callback_data='page_number')
    next_btn = types.InlineKeyboardButton(text='>>', callback_data="NumberPage\":" + str(int(page) + 1))
    first_page.add(page_number, next_btn)
    return first_page


def choice_region():
    choice_list_region = types.InlineKeyboardMarkup(row_width=1)
    connection = Postgres.open_connection()
    list_region = Postgres.get_list_region(connection)
    Postgres.close_connection(connection)
    for i in range(len(list_region)):
        region = types.InlineKeyboardButton(text=list_region[i], callback_data=list_region[i])
        choice_list_region.add(region)
    return choice_list_region



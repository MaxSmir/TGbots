import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


def open_connection():
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name)
    print("Connection open")
    return connection


def add_user(connection, text, user_id, username):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("INSERT INTO users (name, id_tg, username) VALUES ('%s', '%s', '%s')" % (text, user_id, username))
    connection.commit()
    cursor.close()
    print("Cursor close")


def list_user(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id_tg FROM users")
    print("Cursor open")
    users = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    result_users = list(zip(*users))
    return result_users


def change_category(connection, category, user_id):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("""UPDATE users SET id_category = (SELECT id FROM categories WHERE categories.category = %s)
                   WHERE id_tg = %s""", (category, user_id))
    connection.commit()
    cursor.close()
    print("Cursor close")


def get_region_user(connection, id_tg):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("""SELECT regions.region  FROM users left join regions on users.id_region = regions.id
                    WHERE users.id_tg = '%s'""" % id_tg)
    region_user = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    return region_user[0]


def get_list_region(connection):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("""SELECT region FROM regions""")
    list_region = [region[0] for region in cursor.fetchall()]
    cursor.close()
    print("Cursor close")
    return list_region


def rename_user(connection, text, user_id):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("UPDATE users SET name = '%s' WHERE id_tg = '%s'" % (text, user_id))
    connection.commit()
    cursor.close()
    print("Cursor close")


def change_region(connection, region, user_id):
    cursor = connection.cursor()
    print("cursor open")
    cursor.execute("""UPDATE users SET id_region = (SELECT id FROM regions WHERE regions.region = %s)
    WHERE id_tg = %s """, (region, user_id))
    connection.commit()
    cursor.close()
    print("Cursor close")


def delete_user(connection, user_id):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("DELETE FROM users WHERE id_tg = '%s' " % user_id)
    connection.commit()
    cursor.close()
    print("Cursor close")


def add_news(connection, region, category, news, url, date):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute(""" INSERT INTO news (id_region, id_category, text, url, news_date) SELECT regions.id, categories.id,
    %s, %s, %s FROM regions JOIN categories ON regions.region = %s AND categories.category = %s""",
                   (news, url, date, region, category))
    connection.commit()
    cursor.close()
    print("Cursor close")


def get_news(connection, region, category):
    cursor = connection.cursor()
    cursor.execute("""select news.text from news left join regions
                    on news.id_region = regions.id left join categories on news.id_category = categories.id 
                   WHERE regions.region = %s AND categories.category = %s""", (region, category))
    print("Cursor open")
    news = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    print(str(news))
    return news


def get_date_news(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT news_date FROM news")
    print("Cursor open")
    date_news = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    return date_news


def get_url_news(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM news")
    print("Cursor open")
    url = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    return url


def delete_news(connection, news_date):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("DELETE FROM news WHERE news_date = '%s'" % news_date)
    connection.commit()
    cursor.close()
    print("Cursor close")


def get_category_news(connection, id_tg):
    cursor = connection.cursor()
    print("Cursor open")
    cursor.execute("""SELECT categories.category FROM users left JOIN categories on users.id_category = categories.id
     WHERE users.id_tg = '%s'""" % id_tg)
    category = cursor.fetchall()
    cursor.close()
    print("Cursor close")
    return category[0]


def close_connection(connection):
    if connection is not None:
        connection.close()
        print("Connection close\n")




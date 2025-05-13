import schedule
import time
import newsbot
import pars_new
import threading

def start_bot():
    try:
        newsbot.bot.polling()
    except Exception as e:
        print("Произошла ошибка при запуске бота:", e)
        start_bot()
    finally:
        start_bot()


def start_pars_new():
    pars_new.main()


if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    # Планируем задачу на каждый день
    #schedule.every().day.at("20:09").do(start_pars_new)
    #schedule.every(1).hours.do(start_pars_new)
    schedule.every().hours.at(":09").do(start_pars_new)
    #schedule.every(3).seconds.do(my_task)
    while True:
        schedule.run_pending()
        time.sleep(1)
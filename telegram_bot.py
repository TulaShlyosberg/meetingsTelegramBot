import lec_db_methods as lec_meth
from telegram.ext import Updater, CommandHandler
import numpy

def start(bot, update):
    update.message.reply_text(
        'Привет, {}!'.format(update.message.from_user.first_name))
    update.message.reply_text('Чтобы узнать, какие лекции в Москве можно посетить в ближайшее время,\
    введи /lectures')


def main_answer(bot, update, args, rand=0):
    # Получаем город, в котором будем искать лекции
    # Передаем его в качестве аргумента запроса БД
    # Аргумент не задан - ищем по Москве
    if len(args) == 0:
        city = 'Москва'
    else:
        city = ' '.join(args)
    result = lec_meth.get_lectures_from_city(city)

    # Смотрим, выводим ли мы все лекции или только три случайных
    if rand != 0:
        numbers = numpy.random.randint(0, len(result), rand)
    else:
        numbers = range(0, len(result))

    # Обрабатываем запрос БД
    if not(result):
        update.message.reply_text("В городе под названием {} лекций не проводится".format(city))
    else:
        for i in numbers:
            row = result[i]
            ans = 'Вы можете прослушать: {}\n'.format(row[0])
            ans += '{} с {} до {}\n'.format(row[1], row[2], row[3])
            ans += 'По адресу: {}\n'.format(row[6])
            ans += 'Стоимость билета от {} рублей\n'.format(row[5])
            ans += 'Для записи пройдити по ссылке: {}'.format(row[4])
            update.message.reply_text(ans)


# Выводит три случайные лекции
def get_three_random_lectures(bot, update, args):
    main_answer(bot, update, args, 3)


def help(bot, update):
    update.message.reply_text("/help - вызвать помощь")
    update.message.reply_text("/lectures [город] - вывести все лекции в заданном городе,\
    если город не задан - вывести лекции в Москве")
    update.message.reply_text("/rand_lectures [город] - вывести три случайные лекции в\
    заданном городе, если город не задан - вывести лекции в Москве")


# Выводит все лекции в заданном городе
def get_lectures_from_city(bot, update, args):
   main_answer(bot, update, args)


# Обновляет базу данных       
def update_db(bot, job):
    lec_meth.update_db()


def main():
    with open('token.txt', 'r') as token:
        updater = Updater(token.readline())
    updater.job_queue.run_daily(update_db, 0)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('lectures', get_lectures_from_city, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('rand_lectures', 
                                                  get_three_random_lectures, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



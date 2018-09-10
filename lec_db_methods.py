import sqlite3 as sql
import urllib.request as req
from lxml import etree
from io import StringIO
import datetime


# По названию месяца получаем его номер
def get_month(month_name):
    return {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12'
        }[month_name]


# Процедура, извлекающая необходимую информацию с сайта
def parse_inform():
    response = req.urlopen("https://my.timepad.ru/all/categories/nauka/events?approved=true&date=&mode=&online=true&paid=true")
    html = response.read().decode('utf-8')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)
    org_inform = tree.xpath('//div[@class = "row-fluid b-event__info-elem"]\
    //span[@class = "b-unit__text_size_small b-unit__text_color_black"]/text()')
    lectures_themes = tree.xpath('//h2[@class = "b-unit__header_size_small b-event__header"]/a/text()')
    org_names = tree.xpath('//div[@class = "span9"]/span[@class = "b-unit__text_size_small b-unit__text_color_black"]/a/text()')
    urls = tree.xpath("//div[@class = 'b-event']//a[@class='b-event__go-button']/@href")
    return org_inform, lectures_themes, org_names, urls


# Добавляет новые организации
def update_org_adresses(cur, org_names, adresses):
    pattern_sel = "SELECT office_id FROM org_adresses WHERE org_name = ?"
    pattern_ins = "INSERT INTO org_adresses (org_name, adress, city) VALUES (?, ?, ?)"
    cur_max = cur.execute("SELECT MAX(office_id) FROM org_adresses")
    cur_max = cur_max.fetchone()
    if not(cur_max[0]):
        cur_max = 1
    else:
        cur_max = cur_max[0] + 1
    indexes = list()
    for org_name, adress in zip(org_names, adresses):
        org_adress = adress[1:]
        city = org_adress[:org_adress.find(',')]
        cur.execute(pattern_sel, (org_name,))
        result = cur.fetchone()
        if not(result):
            cur.execute(pattern_ins, (org_name, org_adress, city))
            cur_id = cur_max
            cur_max += 1
        else:
            cur_id = result[0]
        indexes.append(cur_id)
    return indexes # Возвращает массив id организаций


# Добавляет новые лекции
def update_time_table(cur, times, indexes, lectures_themes, prices, urls):
    pattern_ins = '''INSERT INTO time_table (lecture_date, time_begin, time_end, office_id,
    theme, url, price) VALUES (?, ?, ?, ?, ?, ?, ?)'''
    pattern_sel = '''SELECT lecture_id 
                    FROM time_table
                    WHERE lecture_date = ? AND theme = ? AND office_id = ?'''
    for item in zip(times, indexes, lectures_themes, urls, prices):
        time_list = item[0].split()
        time_begin = time_list[4]
        time_end = time_list[6]
        price = item[-1].split()[1]
        date = '{}-{}-{}'.format(time_list[2], get_month(time_list[1]), time_list[0])
        cur.execute(pattern_sel, (date, item[2], item[1]))
        result = cur.fetchone()
        if not(result):
            cur.execute(pattern_ins, (date, time_begin, time_end) + item[1:-1] +(price,))



def update_db():
    # Извлекаем информацию с сайта
    org_inform, lectures_themes, org_names, urls = \
        parse_inform()
    adresses = list(filter(lambda x: x.count(',') > 1 and x.count(':') < 2, org_inform))
    times = list(filter(lambda x: x.count(':') == 2, org_inform))
    prices = list(filter(lambda x: x.find('руб.') != -1, org_inform))
    
    # Обновляем базу данных
    d_base = sql.connect('open_lectures.db')
    cur = d_base.cursor()
    #  Добавляем новые лектории и лекции
    indexes = update_org_adresses(cur, org_names, adresses)
    update_time_table(cur, times, indexes, lectures_themes, prices, urls)
    # Удаляем устаревшие лекции
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    cur.execute("DELETE FROM time_table WHERE lecture_date < {}".format(today))
    cur.close()
    d_base.commit()
    d_base.close()


# Выводит все лекции, проходящие в данном городе
def get_lectures_from_city(city):
    d_base = sql.connect('open_lectures.db')
    cur = d_base.cursor()
    cur.execute(
        '''
        SELECT theme, lecture_date, time_begin, time_end,
        url, price, adress
        FROM time_table JOIN org_adresses ON (time_table.office_id = org_adresses.office_id)
        WHERE city = ?001 OR ?001 = 'All'
        ''', (city,)
        )
    result = cur.fetchall()
    d_base.commit()
    d_base.close()
    return result


# Создание базы данных
def create_db():
    d_base = sql.connect('open_lectures.db')
    cur = d_base.cursor()
    with open("CREATE_DB.SQL", "r") as fin:
        script = (' '.join(fin.readlines())).split(';')
        for command in script:
            cur.execute(command.strip())
    cur.close()
    d_base.commit()
    d_base.close()  

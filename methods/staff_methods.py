import datetime
import random

from database.design_database import c, db
from methods.usersSetting import getFullName


def getPerms(user_id):
    c.execute(f"SELECT perms FROM staff_perms WHERE user_id = '{user_id}'")
    db.commit()
    if c.fetchone() is not None:
        return c.fetchall()
    else:
        return ""

def getWorker(type, sort):
    c.execute(f"SELECT user_id FROM staff WHERE can_work_{type} = 1 ORDER BY '{sort}_no_does'")
    responce = c.fetchall()
    manager = responce[random.randint(0, len(responce) - 1)][0]
    c.execute(f"SELECT name FROM staff WHERE user_id = '{manager}'")
    return [manager, c.fetchone()[0]]

def getDesigner(service):
    c.execute(f"SELECT user_id FROM designer_service WHERE service = '{service}'")
    responce = c.fetchall()
    designer = responce[random.randint(0, len(responce) - 1)][0]
    c.execute(f"SELECT name FROM staff WHERE user_id = '{designer}'")
    return [designer, c.fetchone()[0], getRaything(designer, "designer")]

def addStats(user_id, column):
    c.execute(f"UPDATE staff SET {column}_all = {column}_all + 1, {column}_no_does = {column}_no_does + 1 WHERE user_id = '{user_id}'")
    db.commit()

def getRaything(user_id, type):
    c.execute(f"SELECT raything FROM raything_list WHERE user_id = '{user_id}' AND type = '{type}'")
    responce = c.fetchall()
    raything = 0
    for i in range(len(responce)):
        raything+=responce[i][0]
    raything = round(raything / len(responce), 3)
    c.execute(f"UPDATE staff SET raything = {raything} WHERE user_id = '{user_id}'")
    db.commit()
    return raything

def addBalance(user_id, balance, type, number):
    c.execute(f"UPDATE staff SET balance = balance + '{balance}' WHERE user_id = '{user_id}'")
    c.execute(f"INSERT INTO balance_list VALUES ({user_id}, {balance}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}', '{type}', {number})")
    db.commit()

def addRaything(user_id, raything, type, number):
    c.execute(f"INSERT INTO raything_list VALUES ({user_id}, {raything}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}', '{type}', {number})")
    db.commit()

def closeOrderAddBalance(user_id):
    c.execute(f"SELECT money, designer, bet FROM pay_list WHERE user_id = '{user_id}'")
    responce = c.fetchall()
    db.commit()
    c.execute(f"SELECT number, service FROM orders WHERE user_id = '{user_id}'")
    order_info = c.fetchall()
    db.commit()
    for i in range(len(responce)):
        money = responce[i][0] - (responce[i][0] * responce[i][2] / 100)
        addBalance(responce[i][1], money, "designer", order_info[0][0])
    c.execute(f"SELECT manager_id FROM orders WHERE user_id = '{user_id}'")
    db.commit()
    manager_id = c.fetchone()[0]
    c.execute("SELECT manager_bet FROM bet")
    addBalance(manager_id, c.fetchone()[0], "manager", order_info[0][0])

def getOrders(user_id):
    c.execute(
        f"SELECT number, service, data, status FROM orders WHERE designer_id = '{user_id}' ORDER by data")
    db.commit()
    response = c.fetchall()
    orders = ""
    orders2 = ""
    count = 0
    for i in range(len(response)):
        if response[i][3] == "Выполняется":
            orders = orders + f"#{response[i][0]} | {response[i][1]} {response[i][3]} ({response[i][2]})\n"
            count += 1
        elif response[i][3] == 'В очереди' or response[i][3] == 'Переделывается':
            orders2 = orders2 + f"#{response[i][0]} | {response[i][1]} - {response[i][3]} ({response[i][2]})\n"
            count += 1
    return f"@id{user_id}({getFullName(user_id)['first_name']}), Ваши заказы:\n\n{orders}\n\n————————————————\n\n{orders2}\n\nВсего: {count}"

def getOrdersNeedDid():
    c.execute(
        f"SELECT number, service, data, status FROM orders ORDER by data")
    db.commit()
    response = c.fetchall()
    orders = ""
    orders2 = ""
    count = 0
    for i in range(len(response)):
        if response[i][3] == "Выполняется":
            orders = orders + f"#{response[i][0]} | {response[i][1]} {response[i][3]} ({response[i][2]})\n"
            count += 1
        elif response[i][3] == 'В очереди' or response[i][3] == 'Переделывается':
            orders2 = orders2 + f"#{response[i][0]} | {response[i][1]} - {response[i][3]} ({response[i][2]})\n"
            count += 1
    return f"Выполняются:\n\n{orders}\n\n————————————————\n\n{orders2}\n\nВсего: {count}"

def getOrdersBeLate():
    c.execute("SELECT number, service, data, status, designer_id FROM orders WHERE status = 'Выполняется' or status = 'В очереди' or status = 'Переделывается' ORDER by data")
    db.commit()
    responce = c.fetchall()
    answer = "Задержанные заказы:"
    for i in range(len(responce)):
        date = responce[i][2]
        date = date.replace('.', ' ').replace(':', ' ').split(' ')
        date = list(map(int, date))
        date = datetime.datetime(day=date[0], month=date[1], year=date[2], hour=date[3],
                                 minute=date[4], second=date[5])
        date += datetime.timedelta(days=3)
        c.execute(f"SELECT name FROM staff WHERE user_id = '{responce[i][4]}'")
        db.commit()
        if date < datetime.datetime.now():
            answer = answer + f"#{responce[i][0]} | {responce[i][1]} - {responce[i][3]} ({responce[i][2]}) → @id{responce[i][4]}({c.fetchone()[0]})"
    return answer

def getOrdersNoManager():
    c.execute("SELECT number, service, data, status FROM orders WHERE have_manager = 0 AND chat_id != 0")
    db.commit()
    responce = c.fetchall()
    orders = ""
    count = 0
    for i in range(len(responce)):
        orders = orders + f"#{responce[i][0]} | {responce[i][1]} {responce[i][3]} ({responce[i][2]})\n"
        count +=1
    return f"Заказы без менеджеров:\n\n{orders}\n\nВсего {count}"

def getDialogNoManager():
    c.execute("SELECT number_dialog, date_create FROM manager_dialog WHERE have_manager = 0 AND chat_id != 0")
    db.commit()
    responce = c.fetchall()
    orders = ""
    count = 0
    for i in range(len(responce)):
        orders = orders + f"#{responce[i][0]} | {responce[i][1]}\n"
        count +=1
    return f"Диалоги без менеджеров:\n\n{orders}\n\nВсего {count}"

def getOrdersNoClose():
    c.execute(f"SELECT user_id, date_last_message FROM control_close_orders")
    responce = c.fetchall()
    db.commit()
    order = ""
    count = 0
    for i in range(len(responce)):
        c.execute(f"SELECT number, service, data, status FROM orders WHERE user_id = '{responce[i][0]}'")
        db.commit()
        order_info = c.fetchall()
        if order_info[0][3] == 'Готов':
            date = responce[i][1]
            date = date.replace('.', ' ').replace(':', ' ').split(' ')
            date = list(map(int, date))
            date = datetime.datetime(day=date[0], month=date[1], year=date[2], hour=date[3],
                                     minute=date[4], second=date[5])
            date += datetime.timedelta(days=1)
            if date < datetime.datetime.now():
                order = order + f"#{order_info[0][0]} | {order_info[0][1]} {order_info[0][3]} ({order_info[0][2]})\n"
            count+=1
    return f"Незакрытые заказы: \n\n{order}\n\nВсего {count}"
def getBalance(user_id):
    c.execute(f"SELECT balance FROM staff WHERE user_id = '{user_id}'")
    db.commit()
    return f"@id{user_id}({getFullName(user_id)['first_name']}), Ваш баланс {c.fetchone()[0]}₽"

def getRaythingAll(user_id):
    c.execute(f"SELECT raything FROM raything_list WHERE user_id = '{user_id}' AND type = 'designer'")
    designer_raything = c.fetchall()
    db.commit()
    c.execute(f"SELECT raything FROM raything_list WHERE user_id = '{user_id}' AND type = 'manager'")
    manager_raything = c.fetchall()
    db.commit()
    message = ""
    if len(designer_raything) > 0:
        message = f"Дизайнерский: {getRaything(user_id, 'designer')}⭐"
    if len(manager_raything) > 0:
        message = message + f"\nМенеджерский: {getRaything(user_id, 'manager')}⚡"
    return f"Ваши рейтинги: \n{message}"

def getStats(user_id):
    c.execute(f"SELECT can_work_designer, orders_all, orders_did, orders_no_does, name FROM staff WHERE user_id = {user_id}")
    designer_stats = c.fetchall()
    db.commit()
    c.execute(f"SELECT can_work_manager, dialog_all, dialog_did, dialog_no_does FROM staff WHERE user_id = {user_id}")
    manager_stats = c.fetchall()
    answer = f"{designer_stats[0][4]}, Ваша статистика: "
    if designer_stats[0][0] == 1:
        answer = answer + f"\n\n→ Дизайнерская: \n× Рейтинг: {getRaything(user_id, 'designer')} ⭐\n\n× Заказы:\n » Всего: {designer_stats[0][1]}\n » Сделано: {designer_stats[0][2]}\n » Выполняются: {designer_stats[0][3]}"
    if manager_stats[0][0] == 1:
        answer = answer + f"\n\n→ Менеджерская: \n× Рейтинг: {getRaything(user_id, 'manager')} ⚡\n\n× Диалоги:\n » Всего: {manager_stats[0][1]}\n » Сделано: {manager_stats[0][2]}\n » Выполняются: {manager_stats[0][3]}"
    return answer

def getStaff():
    c.execute("SELECT blokopad_id, name, staff_group, staff_date, user_id FROM staff")
    responce = c.fetchall()
    db.commit()
    answer = "⚡ | Персонал Nowke\n\n"
    admins = "Высшая администрация"
    managers = "Менеджеры"
    moders = "Модераторы"
    designers = "Дизайнеры"
    for i in range(len(responce)):
        if responce[i][2] == 'admin':
            admins = admins + f"\n → ID: {responce[i][0]} @id{responce[i][4]}({responce[i][1]}) | {responce[i][3]}"
        elif responce[i][2] == 'manager':
            managers = managers + f"\n → ID: {responce[i][0]} @id{responce[i][4]}({responce[i][1]}) | {responce[i][3]}"
        elif responce[i][2] == 'moder':
            moders = moders + f"\n → ID: {responce[i][0]} @id{responce[i][4]}({responce[i][1]}) | {responce[i][3]}"
        elif responce[i][2] == 'designer':
            designers = designers + f"\n → ID: {responce[i][0]} @id{responce[i][4]}({responce[i][1]}) | {responce[i][3]}"
    return answer + admins + "\n\n" + managers + "\n\n" + moders + "\n\n" + designers + "\n\n"


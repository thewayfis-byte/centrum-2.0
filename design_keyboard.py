import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from database.design_database import c, db

def start():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label='Начать', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()
def menuKeyboard(user_id):
    c.execute("SELECT on_free_avatar FROM design_settings")
    db.commit()
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Заказать", color=VkKeyboardColor.POSITIVE, payload=json.dumps("new_order"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Отзывы", color=VkKeyboardColor.PRIMARY, payload=json.dumps("reviews"))
    keyboard.add_callback_button(label="FAQ", color=VkKeyboardColor.PRIMARY, payload=json.dumps("faq"))
    if c.fetchone()[0] == 1:
        keyboard.add_line()

        keyboard.add_callback_button(label="Бесплатный Аватар", color=VkKeyboardColor.SECONDARY,
                                     payload=json.dumps("new_order_free"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Помощь", color=VkKeyboardColor.SECONDARY, payload=json.dumps("help"))
    c.execute(f"SELECT mailling FROM users WHERE user_id = '{user_id}'")
    db.commit()
    if c.fetchone()[0] == 1:
        keyboard.add_line()
        keyboard.add_callback_button(label="Не получать рассылки", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("cancelMailling"))
    else:
        keyboard.add_line()
        keyboard.add_callback_button(label="Получать рассылки", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("enableMailling"))
    keyboard.add_openlink_button(label="Заказ через человека", link="https://vk.me/ilezovofficial")
    return keyboard.get_keyboard()

def back_to_menu():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Назад в меню", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("back_to_menu"))
    return keyboard.get_keyboard()

def arms():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Alex", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Руки Alex"))
    keyboard.add_callback_button(label="Steve", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Руки Steve"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Отменить оформление заказа", color=VkKeyboardColor.NEGATIVE,
                                 payload=json.dumps("cancelOrder"))
    return keyboard.get_keyboard()

def avatar():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Head", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Аватар Head"))
    keyboard.add_callback_button(label="3D", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Аватар 3D"))
    keyboard.add_callback_button(label="Totem", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Аватар Totem"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Кубик", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Аватар Кубик"))
    keyboard.add_callback_button(label="Round", color=VkKeyboardColor.SECONDARY, payload=json.dumps("Аватар Round"))
    keyboard.add_callback_button(label="Отменить оформление заказа", color=VkKeyboardColor.NEGATIVE,
                                 payload=json.dumps("cancelOrder"))
    return keyboard.get_keyboard()

def carousel_callback(service):
    keyboard = [{"action": {"type": "callback", "label": f"{service}", "payload": json.dumps(f"{service}")}, "color": "positive"}, {"action": {"type": "callback", "label": f"Назад к категориям", f"payload": json.dumps("back_to_categorie")}, "color": "negative"}, {"action": {"type": "open_link", "label": "Заказ через человека", "link": "https://vk.me/ilezovofficial"}}]
    return keyboard
def nextPage(page):
    keyboard = [{"action": {"type": "callback", "label": f"Следующая страница", f"payload": json.dumps(page)}, "color": "positive"}, {"action": {"type": "callback", "label": f"Назад к категориям", f"payload": json.dumps("back_to_categorie")}, "color": "negative"}, {"action": {"type": "open_link", "label": "Заказ через человека", "link": "https://vk.me/ilezovofficial"}}]
    return keyboard
def lastPage(page):
    keyboard = [{"action": {"type": "callback", "label": f"Предыдущая страница", f"payload": json.dumps(page)}, "color": "positive"}, {"action": {"type": "callback", "label": f"Назад к категориям", f"payload": json.dumps("back_to_categorie")}, "color": "negative"}, {"action": {"type": "open_link", "label": "Заказ через человека", "link": "https://vk.me/ilezovofficial"}}]
    return keyboard

def categoris():
    keyboard = VkKeyboard(inline=True)
    c.execute("SELECT alias FROM services")
    responce = c.fetchall()
    alias = []
    a = 0
    keyboard.add_callback_button(label="Все", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"type": "categoris", "categoris": f"all"}))
    keyboard.add_line()
    for i in range(len(responce)):
        if responce[i][0] not in alias and responce[i][0] != '':
            alias.append(responce[i][0])
    for i in range(len(alias)):
        a+=1
        if a == 3:
            keyboard.add_line()
            a = 0
        keyboard.add_callback_button(label=alias[i], color=VkKeyboardColor.SECONDARY, payload=json.dumps({"type": "categoris", "categoris": f"{alias[i]}"}))
    keyboard.add_line()
    keyboard.add_callback_button(label="Назад в меню", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("back_to_menu"))
    return keyboard.get_keyboard()
def services_list(list=0, price = 1, alias = '1'):
    if price == 0:
        if alias != '1':
            c.execute(f"SELECT * FROM services WHERE price = 0 AND alias = '{alias}' ORDER BY priority")
            db.commit()
        else:
            c.execute(f"SELECT * FROM services WHERE price = 0 ORDER BY priority")
            db.commit()
    else:
        if alias != '1':
            c.execute(f"SELECT * FROM services WHERE price != 0 AND alias = '{alias}' ORDER BY priority")
            db.commit()
        else:
            c.execute(f"SELECT * FROM services WHERE price != 0 ORDER BY priority")
            db.commit()
        db.commit()
    response = c.fetchall()
    elements = []
    i = 0
    a = -1
    b = 0
    while a != list:
        b = b + 8
        a = a + 1
    i = b - 8
    if len(response) / (list + 1) * 16 > 1 and list > 0:
            elements.append({"title": "Предыдущая страница", "description": f"Перейти к странице {a}",
                             "action": {"type": "open_link", "link": "https://vk.com/blokopad"},
                             "photo_id": f"-224824486_456239183", "buttons": lastPage(list-1)})
    while i != b:
        try:
            elements.append({"title": response[i][0], "description": f"Цена от {response[i][2]}₽",
                                 "action": {"type": "open_link", "link": f"{response[i][5]}"},
                                 "photo_id": f"{response[i][3]}", "buttons": carousel_callback(response[i][0])})
        except Exception:
            pass
        i = i + 1
    if len(response) / (list + 1) * 9 > 1:
            elements.append({"title": "Следующая страница", "description": f"Перейти к странице {a+2}",
                             "action": {"type": "open_link", "link": "https://vk.com/blokopad"},
                             "photo_id": f"-224824486_456239053", "buttons": nextPage(list+1)})
    returner = {"type": "carousel", "elements": elements}
    return json.dumps(returner, ensure_ascii=False)

def closeTicket():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Закрыть тикет", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("close_ticket"))
    return keyboard.get_keyboard()

def raything(manager_id, chat_id, number):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="5", color=VkKeyboardColor.POSITIVE, payload=json.dumps({"raything": 5, "manager_id": manager_id, "chat_id": chat_id, "number": number}))
    keyboard.add_callback_button(label="4", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"raything": 4, "manager_id": manager_id, "chat_id": chat_id, "number": number}))
    keyboard.add_callback_button(label="3", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"raything": 3, "manager_id": manager_id, "chat_id": chat_id, "number": number}))
    keyboard.add_callback_button(label="2", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"raything": 2, "manager_id": manager_id, "chat_id": chat_id, "number": number}))
    keyboard.add_callback_button(label="1", color=VkKeyboardColor.NEGATIVE, payload=json.dumps({"raything": 1, "manager_id": manager_id, "chat_id": chat_id, "number": number}))
    return keyboard.get_keyboard()

def managerDialog():
    keyboard = VkKeyboard()
    keyboard.add_callback_button(label="Сообщения", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_manager_message"))
    return keyboard.get_keyboard()

def orderDialog():
    keyboard = VkKeyboard()
    keyboard.add_callback_button(label="Сообщения", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_order_message"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Опишите подробнее", color=VkKeyboardColor.SECONDARY, payload=json.dumps("request-about"))
    keyboard.add_callback_button(label="Отправьте файлом", color=VkKeyboardColor.SECONDARY, payload=json.dumps("request-file"))
    keyboard.add_line()
    keyboard.add_callback_button(label="В очереди", color=VkKeyboardColor.SECONDARY, payload=json.dumps("waiting"))
    keyboard.add_callback_button(label="Готов", color=VkKeyboardColor.POSITIVE, payload=json.dumps("ready"))
    keyboard.add_callback_button(label="Выполняется", color=VkKeyboardColor.SECONDARY, payload=json.dumps("progress"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Закрыть заказ", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("close_order_designer"))
    return keyboard.get_keyboard()

def startOrder():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Выбрать эту услугу!", color=VkKeyboardColor.POSITIVE, payload=json.dumps("startOrder"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Продолжить выбор", color=VkKeyboardColor.SECONDARY, payload=json.dumps("continueSelection"))
    return keyboard.get_keyboard()

def cancelOrder(further=False, inline=False):
    if inline == True:
        keyboard = VkKeyboard(inline=True)
    else:
        keyboard = VkKeyboard()
    if further == True:
        keyboard.add_callback_button(label="Далее", color=VkKeyboardColor.SECONDARY, payload=json.dumps("further"))
        keyboard.add_line()
    keyboard.add_callback_button(label="Отменить оформление заказа", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("cancelOrder"))
    return keyboard.get_keyboard()

def clearKeyboard():
    keyboard = VkKeyboard()
    return keyboard.get_empty_keyboard()

def payKeyboard(link, promocode=False):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Оплатить", color=VkKeyboardColor.PRIMARY, payload={"type": "open_link", "link": f"{link}"})
    if promocode == True:
        keyboard.add_callback_button(label="Активировать промокод", color=VkKeyboardColor.PRIMARY, payload=json.dumps("promocode"))
        keyboard.add_line()
    keyboard.add_callback_button(label="Проверить оплату", color=VkKeyboardColor.POSITIVE, payload=json.dumps("check_pay"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Ссылка устарела", color=VkKeyboardColor.NEGATIVE,
                                 payload=json.dumps("new_link"))
    keyboard.add_callback_button(label="Отменить заказ", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("cancelOrder"))
    return keyboard.get_keyboard()

def noPromocode():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Нет промокода", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("no_promocode"))
    return keyboard.get_keyboard()
def waitOrder():
    keyboard = VkKeyboard()
    keyboard.add_callback_button(label="Очередь", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_queue"))
    keyboard.add_callback_button(label="Статус заказа", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_status"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Закрыть заказ", color=VkKeyboardColor.POSITIVE, payload=json.dumps("close_order"))
    return keyboard.get_keyboard()

def closeOrder():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Закрыть заказ", color=VkKeyboardColor.POSITIVE,
                                 payload=json.dumps("close_order_confirm"))
    return keyboard.get_keyboard()

def designChat(admin=False):
    keyboard = VkKeyboard()
    keyboard.add_callback_button(label="Заказы", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_orders_designer"))
    keyboard.add_callback_button(label="Баланс", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_balance_designer"))
    keyboard.add_callback_button(label="Рейтинг", color=VkKeyboardColor.SECONDARY, payload=json.dumps("get_raything_designer"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Статистика", color=VkKeyboardColor.PRIMARY, payload=json.dumps("get_stats"))
    if admin == True:
        keyboard.add_line()
        keyboard.add_callback_button(label="«Заказы»", color=VkKeyboardColor.SECONDARY, payload=json.dumps("admin_orders"))
        keyboard.add_callback_button(label="«Настройки»", color=VkKeyboardColor.SECONDARY, payload=json.dumps("admin_settings"))
    return keyboard.get_keyboard()



def noWouldRewievs():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Не хочу :(", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("no-would-rewievs"))
    return keyboard.get_keyboard()

def dopPay(payform, money, link, designer, bet):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Доплатить", color=VkKeyboardColor.PRIMARY, payload={"type": "open_link", "link": f"{link}"})
    keyboard.add_callback_button(label="Проверить оплату", color=VkKeyboardColor.POSITIVE,
                                 payload=json.dumps({"payload": "check_pay", "payform": payform, "money": money, "designer": designer, "bet": bet}))
    keyboard.add_line()
    keyboard.add_callback_button(label="Отказаться от оплаты", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("cancelDopPay"))
    return keyboard.get_keyboard()

def chapterAdmin(type):
    keyboard = VkKeyboard()
    if type == "orders":
        keyboard.add_callback_button(label="Раздел Заказы", color=VkKeyboardColor.PRIMARY, payload=json.dumps("null"))
        keyboard.add_line()
        keyboard.add_callback_button(label="Нужно сделать", color=VkKeyboardColor.SECONDARY, payload=json.dumps("orders_need_did"))
        keyboard.add_callback_button(label="Задерживаются", color=VkKeyboardColor.SECONDARY, payload=json.dumps("orders_be_late"))
        keyboard.add_callback_button(label="Без менеджера", color=VkKeyboardColor.SECONDARY, payload=json.dumps("no_have_manager"))
        keyboard.add_callback_button(label="Незакрытые", color=VkKeyboardColor.SECONDARY, payload=json.dumps("no_close"))
    elif type == "settings":
        keyboard.add_callback_button(label="Раздел Настройки", color=VkKeyboardColor.PRIMARY, payload=json.dumps("null"))
        keyboard.add_line()
        c.execute("SELECT * FROM design_settings")
        responce = c.fetchall()
        if responce[0][0] == 0:
            keyboard.add_callback_button(label="Бесплатный Аватар", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("free_avatar_on"))
        else:
            keyboard.add_callback_button(label="Бесплатный Аватар", color=VkKeyboardColor.POSITIVE,
                                         payload=json.dumps("free_avatar_off"))
        if responce[0][1] == 0:
            keyboard.add_callback_button(label="Обязательный отзыв", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("reviews_on"))
        else:
            keyboard.add_callback_button(label="Обязательный отзыв", color=VkKeyboardColor.POSITIVE,
                                         payload=json.dumps("reviews_off"))
    keyboard.add_line()
    keyboard.add_callback_button(label="Назад", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("back_admin"))
    return keyboard.get_keyboard()

def cancelMailling():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Не получать рассылки", color=VkKeyboardColor.NEGATIVE, payload=json.dumps("cancelMailling"))
    return keyboard.get_keyboard()


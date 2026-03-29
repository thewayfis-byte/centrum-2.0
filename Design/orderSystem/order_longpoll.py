import datetime
import json
import time

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from Design.ЮKassa.payment import checkstatus, createpay, getMoney
from config.config import design_token, design_group_id
from methods.createChat import createChat
from methods.design_message import error, messageSendUser, deleteMessage, messageSendChat, updateMessage, addReview
from Design.design_message import help, order
from database.design_database import c, db
from keyboards.design_keyboard import raything, menuKeyboard, startOrder, cancelOrder, clearKeyboard, waitOrder, \
    payKeyboard, noPromocode, closeOrder, services_list, noWouldRewievs, arms, avatar, categoris
from methods.staff_methods import getWorker, addStats, getRaything, getDesigner, closeOrderAddBalance, addRaything

vk_session = vk_api.VkApi(token=design_token)
longpoll = VkBotLongPoll(vk_session, design_group_id)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_EVENT:
                event_id = event.object.event_id
                user_id = event.object.user_id
                peer_id = event.object.peer_id
                payload = event.object.payload
                c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
                db.commit()
                if c.fetchone() is not None:
                    c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
                    db.commit()
                    flag = c.fetchone()[0]
                else:
                    flag = ""
                if flag == 'choice-service' and peer_id == user_id:
                    if payload == 'back_to_categorie':
                        vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Выберите категорию'})}"})
                        updateMessage(user_id, message="Выберите нужную категорию услуги 🔥", keyboard=categoris())
                    elif type(payload) is int:
                            updateMessage(user_id, f"Выберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥 \n\nСтраница: {payload + 1}", template=services_list(payload))
                    elif payload == '0':
                            updateMessage(user_id, f"Выберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥 \n\nСтраница: {int(payload) + 1}", template=services_list(0))
                    elif payload != 'back_to_menu' and "type" not in payload:
                                c.execute(f"SELECT about, price, attachment FROM services WHERE service = '{payload}'")
                                responce = c.fetchall()
                                db.commit()
                                updateMessage(user_id, f"Вы выбрали «{payload}»\n\n{responce[0][0]}\n\nЦена от: {responce[0][1]}₽",
                                              attachment=responce[0][2], keyboard=startOrder())
                                try:
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                  {"event_id": event_id, "user_id": user_id,
                                                   "peer_id": peer_id,
                                                   "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Вы изучаете услугу {payload}'})}"})
                                except Exception:
                                    pass
                                c.execute(f"INSERT INTO orders VALUES ({user_id}, '{payload}', 'Просматривается', 0, '{datetime.datetime.now()}', 0, 0, 0, '', 0, 0, '', '')")
                                c.execute(f"UPDATE users SET flag = 'look_service' WHERE user_id = '{user_id}'")
                                if "скин" in payload.lower() or "скина" in payload.lower():
                                    c.execute(f"UPDATE orders SET it_skin = 1 WHERE user_id = '{user_id}'")
                                if "оформление профиля" in payload.lower():
                                    c.execute(f"UPDATE orders SET it_skin = 2 WHERE user_id = '{user_id}'")
                                db.commit()
                    elif payload['type'] == 'categoris':
                            if payload['categoris'] == 'all':
                                updateMessage(user_id,
                                              f"Выберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥 \n\nСтраница: 1",
                                              template=services_list(0))
                            else:
                                updateMessage(user_id,
                                          f"Выберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥 \n\nСтраница: 1",
                                          template=services_list(0, alias=payload['categoris']))
                elif flag == 'look_service':
                    if payload == 'continueSelection':
                        try:
                            vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Услуги»'})}"})
                        except Exception:
                            pass
                        updateMessage(user_id, message=order['main']['message'], keyboard=order['main']['keyboard'])
                        c.execute(f"UPDATE users SET flag = 'choice-service' where user_id = '{user_id}'")
                        c.execute(f"DELETE FROM orders WHERE user_id = '{user_id}'")
                        db.commit()
                    elif payload == 'startOrder':
                        c.execute(f"SELECT it_skin FROM orders WHERE user_id = '{user_id}'")
                        skin = c.fetchone()[0]
                        if skin == 1:
                            updateMessage(user_id, "Отличный выбор! ⚡ Выберите руки вашего скина", keyboard=arms())
                        elif skin == 2:
                            updateMessage(user_id, "Отличный выбор! ⚡ Выберите аватар профиля", keyboard=avatar())
                        else:
                            updateMessage(user_id,"Отличный выбор! ⚡ Теперь опишите ваш заказ. Вы можете прикреплять фотографии, файлы, ссылки, сообщения других пользователей и другие вложения. Постарайтесь описать заказ максимально подробно 😉", keyboard=cancelOrder())
                            c.execute(f"UPDATE users SET flag = 'describe-order' where user_id = '{user_id}'")
                        db.commit()
                    elif payload == 'Руки Alex':
                        c.execute(f"UPDATE orders SET arms = 'Руки Alex', it_skin = 0 WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'describe-order' where user_id = '{user_id}'")
                        db.commit()
                        updateMessage(user_id,
                                      "Отличный выбор! ⚡ Теперь опишите ваш заказ. Вы можете прикреплять фотографии, файлы, ссылки, сообщения других пользователей и другие вложения. Постарайтесь описать заказ максимально подробно 😉",
                                      keyboard=cancelOrder())
                    elif payload == 'Руки Steve':
                        c.execute(f"UPDATE orders SET arms = 'Руки Steve', it_skin = 0 WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'describe-order' where user_id = '{user_id}'")
                        updateMessage(user_id,
                                      "Отличный выбор! ⚡ Теперь опишите ваш заказ. Вы можете прикреплять фотографии, файлы, ссылки, сообщения других пользователей и другие вложения. Постарайтесь описать заказ максимально подробно 😉",
                                      keyboard=cancelOrder())
                    elif "Аватар" in payload:
                        payload = payload.split(' ')
                        c.execute(f"UPDATE orders SET arms = 'Аватар {payload[1]}', it_skin = 0 WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'describe-order' where user_id = '{user_id}'")
                        updateMessage(user_id,
                                      "Отличный выбор! ⚡ Теперь опишите ваш заказ. Вы можете прикреплять фотографии, файлы, ссылки, сообщения других пользователей и другие вложения. Постарайтесь описать заказ максимально подробно 😉",
                                      keyboard=cancelOrder())
                        db.commit()
                    elif payload == 'cancelOrder':
                        try:
                            vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Услуги»'})}"})
                        except Exception as e:
                            pass
                        updateMessage(user_id, message="Убираем клавиатуру...", keyboard=clearKeyboard())
                        updateMessage(user_id, message="Выберите нужную категорию услуги 🔥", keyboard=order['main']['keyboard'])
                        c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                        responce = c.fetchall()
                        db.commit()
                        try:
                            messageSendChat(responce[0][0], "Клиент отменил заказ")
                        except Exception:
                            pass
                        c.execute(f"UPDATE users SET flag = 'choice-service' where user_id = '{user_id}'")
                        c.execute(f"DELETE FROM orders WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id}'")
                        db.commit()
                elif flag == 'describe-order' or flag == 'describe-order-2' or flag == 'pay-order':
                    if payload == 'cancelOrder':
                        try:
                            vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Услуги»'})}"})
                        except Exception as e:
                            pass
                        updateMessage(user_id, message="Убираем клавиатуру...", keyboard=clearKeyboard())
                        updateMessage(user_id, message="Выберите нужную категорию услуги 🔥", keyboard=order['main']['keyboard'])
                        c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                        responce = c.fetchall()
                        db.commit()
                        try:
                            messageSendChat(responce[0][0], "Клиент отменил заказ")
                        except Exception:
                            pass
                        c.execute(f"UPDATE users SET flag = 'choice-service' where user_id = '{user_id}'")
                        c.execute(f"DELETE FROM orders WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id}'")
                        db.commit()
                if flag == 'describe-order-2':
                    if payload == 'further':
                        c.execute("SELECT designer FROM dialogs_count")
                        db.commit()
                        dialog_number = c.fetchone()[0] + 1
                        manager_id = getWorker("manager", "dialog")
                        updateMessage(user_id, "Убираем кнопки...", keyboard=clearKeyboard())
                        messageSendUser(user_id, f"Отлично! Ваш заказ #{dialog_number} отправлен на модерацию менеджеру {manager_id[1]} с рейтингом {getRaything(manager_id[0], 'manager')} ⚡ Обычно этот процесс занимает около 10 минут в рабочее время студии \n\nпн-пт: 07:00 — 22:00\nсб-вс: 12:00 — 22:00 \n\nВы можете задавать вопросы ниже, они будут перенаправлены менеджеру по вашему заказу 😉")
                        addStats(manager_id[0], "dialog")
                        c.execute(f"SELECT service, arms FROM orders WHERE user_id = '{user_id}'")
                        service = c.fetchall()
                        dialog_responce = createChat(vk_session,
                                                         f"Заказ #{dialog_number} | {service[0][0]} {service[0][1]}",
                                                         design_group_id)
                        c.execute(f"UPDATE orders SET status = 'Проверяется', manager_id = '{manager_id[0]}', chat_id = '{dialog_responce[0]}', number = '{dialog_number}' WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'wait-approvals' WHERe user_id = '{user_id}'")
                        c.execute(f"UPDATE dialogs_count SET designer = {dialog_number}")
                        db.commit()
                        c.execute("SELECT orders_chat FROM chats")
                        db.commit()
                        messageSendChat(c.fetchone()[0],
                                        f"@id{manager_id[0]}({manager_id[1]}), отправлен новый заказ на модерацию! \nВойти в чат → {dialog_responce[1]['link']}")
                elif flag == 'pay-order':
                    if payload == 'check_pay':
                        c.execute(f"SELECT id_form FROM pay_list WHERE user_id = '{user_id}'")
                        form_info = c.fetchall()
                        id_form = form_info[0][0]
                        if checkstatus(id_form):
                            c.execute(f"SELECT service, number, chat_id FROM orders WHERE user_id = '{user_id}'")
                            db.commit()
                            responce = c.fetchall()
                            designer = getDesigner(responce[0][0])
                            updateMessage(user_id, f"Отлично! Оплата вашего заказа подтверждена и он добавлен в очередь! \n\nЕсли у вас возникли вопросы, то пишите их ниже. Они будут отправлены вашему дизайнеру.\n\nСтатус вашего заказа - «Статус заказа»\nВаш заказ готов? - «Закрыть заказ»\n\nИсполнителем вашего заказа является {designer[1]} с рейтингом {designer[2]} ⭐", keyboard=waitOrder())
                            c.execute("SELECT designer_chat FROM chats")
                            messageSendChat(c.fetchone()[0], f"@id{designer[0]}({designer[1]}), вам пришел новый заказ #{responce[0][1]}. Вступите в чат по ссылке → {vk_session.method('messages.getInviteLink', {'peer_id': 2000000000 + responce[0][2], 'group_id': design_group_id})['link']}")
                            db.commit()
                            c.execute(f"UPDATE orders SET status = 'В очереди', designer_id = {designer[0]}, data = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id}'")
                            c.execute(f"UPDATE users SET flag = 'wait-orders' WHERE user_id = '{user_id}'")
                            c.execute(
                                f"SELECT bet FROM designer_service WHERE user_id = '{designer[0]}' AND service = '{responce[0][0]}'")
                            c.execute(f"UPDATE pay_list SET designer = '{designer[0]}', bet = '{c.fetchone()[0]}' WHERE id_form = '{id_form}'")
                            c.execute(f"INSERT INTO control_close_orders VALUES ({user_id}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}')")
                            c.execute(
                                f"UPDATE staff SET orders_all = orders_all + 1, orders_no_does = orders_no_does + 1 WHERE user_id = '{designer[0]}'")
                            db.commit()
                            c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                            chat_id = c.fetchall()
                            if chat_id != ((0,),):
                                messageSendChat(chat_id[0][0], "Клиент оплатил заказ")
                        else:
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы не оплатили заказ или он еще не обработан системой. Повторите попытку через 5 сек'})}"})
                    elif payload == 'promocode':
                        updateMessage(user_id, "Отправьте ваш промокод в чат. \nНет промокода? — Следите за новостями в нашей группе или ищите пасхалки...", keyboard=noPromocode())
                        c.execute(f"UPDATE users SET flag = 'activate_promocode' WHERE user_id = '{user_id}'")
                        db.commit()
                    elif payload == 'new_link':
                        c.execute(f"SELECT service, number FROM orders WHERE user_id = {user_id}")
                        db.commit()
                        order_info = c.fetchall()
                        c.execute(f"SELECT money FROM pay_list WHERE user_id = {user_id}")
                        db.commit()
                        order_price = c.fetchone()[0]
                        c.execute("SELECT nalog FROM nalog")
                        nalog = c.fetchone()[0]
                        order_price = order_price * nalog + order_price
                        payform = createpay(order_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                        updateMessage(user_id, f"Обновлено {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\nВаш заказ #{order_info[0][1]} успешно одобрен и дизайнеры почти готовы начать работу 🧛‍♀️\n\nСтоимость вашего заказа {order_price}₽ Выполнение заказа займет до 3-х рабочих дней студии. \n\nВо время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡ ",
                                                               keyboard=payKeyboard(payform['link'], True))
                        c.execute(f"UPDATE pay_list SET id_form = '{payform['id']}' WHERE user_id = '{user_id}'")
                        db.commit()
                    else:
                        try:
                            if "https://yoomoney.ru/checkout/payments/v2/contract?" in event.object.payload['link']:
                                vk_session.method("messages.sendMessageEventAnswer",
                                                  {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                                   "peer_id": event.object.peer_id,
                                                   "event_data": f"{json.dumps(event.object.payload)}"})
                        except Exception as e:
                            pass
                elif flag == 'dop-pay':
                        if payload == 'cancelDopPay':
                            updateMessage(user_id, "Доплата отменена")
                            c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                            messageSendChat(c.fetchone()[0], f"Клиент отказался от доплаты")
                            c.execute(f"UPDATE users SET flag = 'wait-orders' WHERE user_id = '{user_id}'")
                            db.commit()
                        else:
                            try:
                                if "https://yoomoney.ru/checkout/payments/v2/contract?" in event.object.payload['link']:
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                                       "peer_id": event.object.peer_id,
                                                       "event_data": f"{json.dumps(event.object.payload)}"})
                            except Exception as e:
                                pass
                        try:
                            if payload['payload'] == 'check_pay':
                                if checkstatus(payload['payform']):
                                    c.execute(f"SELECT service, number, chat_id FROM orders WHERE user_id = '{user_id}'")
                                    db.commit()
                                    responce = c.fetchall()
                                    designer = getDesigner(responce[0][0])
                                    updateMessage(user_id,
                                                  f"Отлично! Доплата подтверждена")
                                    c.execute(f"UPDATE users SET flag = 'wait-orders' WHERE user_id = '{user_id}'")
                                    c.execute(
                                        f"INSERT INTO pay_list VALUES ({user_id}, '{payload['money']}', '{payload['payform']}', '{payload['designer']}', '', '{payload['bet']}')")
                                    db.commit()
                                    c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                                    chat_id = c.fetchall()
                                    messageSendChat(chat_id[0][0], "Клиент доплатил за заказ")
                                else:
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event_id, "user_id": user_id,
                                                       "peer_id": peer_id,
                                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы не доплатили заказ или он еще не обработан системой. Повторите попытку через 5 сек'})}"})
                        except Exception:
                            pass
                        if payload == 'get_status':
                            c.execute(f"SELECT status FROM orders WHERE user_id = '{user_id}'")
                            db.commit()
                            messageSendUser(user_id, f"Статус вашего заказа: {c.fetchone()[0]}")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Статус заказа отправлен в чат'})}"})

                        elif payload == 'get_queue':
                            c.execute(f"SELECT designer_id FROM orders WHERE user_id = '{user_id}'")
                            response = c.fetchone()[0]
                            db.commit()
                            c.execute(
                                f"SELECT number, service, data, status FROM orders WHERE designer_id = '{response}' ORDER by data")
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
                            messageSendUser(user_id,
                                            f"Текущая очереди вашего исполнителя:\n\n{orders}\n\n————————————————\n\n{orders2}\n\nВсего заказов в очереди {count}", )
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Очередь отправлена в чат'})}"})

                        elif payload == 'close_order':
                            messageSendUser(user_id,
                                            "Хотите закрыть заказ? Нажмите на зеленую кнопку под сообщением, чтобы подтвердить это действие",
                                            closeOrder())
                        elif payload == 'close_order_confirm':
                            c.execute(
                                f"SELECT designer_id, manager_id, chat_id, number FROM orders WHERE user_id = '{user_id}'")
                            responce = c.fetchall()
                            db.commit()
                            message_id = messageSendUser(user_id, message="Убираем клавиатуру...",
                                                         keyboard=clearKeyboard())
                            c.execute(
                                f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id}'")
                            db.commit()
                            updateMessage(user_id,
                                          "Спасибо, что сделали заказ у нас! Оцените работу вашего дизайнера от 1 до 5",
                                          raything(responce[0][0], responce[0][2], responce[0][3]))
                            closeOrderAddBalance(user_id)
                            messageSendChat(responce[0][2], "Клиент закрыл заказ. Деньги зачислены на ваш баланс")
                            c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id}'")
                            c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id}'")
                            c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id}'")
                            c.execute(f"UPDATE orders SET status = 'Готов' WHERE user_id = '{user_id}'")
                            c.execute(
                                f"UPDATE staff SET designer_no_does = designer_no_does - 1, designer_did = designer_did + 1 WHERE user_id = '{responce[0][0]}'")
                            c.execute(
                                f"UPDATE staff SET dialog_no_does = dialog_no_does - 1, dialog_did = dialog_did + 1 WHERE user_id = '{responce[0][1]}'")
                            c.execute(
                                f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id}'")
                            db.commit()
                elif flag == 'activate_promocode':
                    if payload == "no_promocode":
                        c.execute(f"SELECT service, number FROM orders WHERE user_id = {user_id}")
                        db.commit()
                        order_info = c.fetchall()
                        c.execute(f"SELECT money FROM pay_list WHERE user_id = {user_id}")
                        db.commit()
                        order_price = c.fetchone()[0]
                        payform = createpay(order_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                        updateMessage(user_id,
                                      f"Ваш заказ #{order_info[0][1]} успешно одобрен и дизайнеры почти готовы начать работу 🧛‍♀️\n\nСтоимость вашего заказа {order_price}₽ Выполнение заказа займет до 3-х рабочих дней студии. \n\nВо время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡ ",
                                      keyboard=payKeyboard(payform['link'], True))
                        c.execute(f"UPDATE pay_list SET id_form = '{payform['id']}' WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'pay-order' WHERE user_id = '{user_id}'")
                        db.commit()
                elif flag == 'wait-orders':
                    if payload == 'get_status':
                        c.execute(f"SELECT status FROM orders WHERE user_id = '{user_id}'")
                        db.commit()
                        messageSendUser(user_id, f"Статус вашего заказа: {c.fetchone()[0]}")
                        vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Статус заказа отправлен в чат'})}"})

                    elif payload == 'get_queue':
                        c.execute(f"SELECT designer_id FROM orders WHERE user_id = '{user_id}'")
                        response = c.fetchone()[0]
                        db.commit()
                        c.execute(
                            f"SELECT number, service, data, status FROM orders WHERE designer_id = '{response}' ORDER by data")
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
                        messageSendUser(user_id,  f"Текущая очереди вашего исполнителя:\n\n{orders}\n\n————————————————\n\n{orders2}\n\nВсего заказов в очереди {count}", )
                        vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Очередь отправлена в чат'})}"})

                    elif payload == 'close_order':
                        messageSendUser(user_id, "Хотите закрыть заказ? Нажмите на зеленую кнопку под сообщением, чтобы подтвердить это действие", closeOrder())
                    elif payload == 'close_order_confirm':
                        c.execute(f"SELECT designer_id, manager_id, chat_id, number FROM orders WHERE user_id = '{user_id}'")
                        responce = c.fetchall()
                        db.commit()
                        message_id = messageSendUser(user_id, message="Убираем клавиатуру...", keyboard=clearKeyboard())
                        c.execute(
                            f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id}'")
                        db.commit()
                        updateMessage(user_id,
                                        "Спасибо, что сделали заказ у нас! Оцените работу вашего дизайнера от 1 до 5",
                                        raything(responce[0][0], responce[0][2], responce[0][3]))
                        closeOrderAddBalance(user_id)
                        messageSendChat(responce[0][2], "Клиент закрыл заказ. Деньги зачислены на ваш баланс")
                        c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id}'")
                        c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE orders SET status = 'Готов' WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id}'")
                        db.commit()
                elif flag == 'designer_raything':
                    addRaything(payload['manager_id'], payload['raything'], "designer", payload["number"])
                    messageSendChat(payload['chat_id'], f"Пользователь оценил вашу работу на {payload['raything']} ⭐")
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Оставьте отзыв о работе'})}"})
                    c.execute(f"SELECT reviews FROM design_settings")
                    if c.fetchone()[0] == 1:
                        updateMessage(user_id,
                                      f"Спасибо за вашу оценку! Она поможет улучшить наш сервис ❤️\n\nНапишите ниже отзыв о работе вашего дизайнера. Это поможет нам в продвижении ⭐")#, keyboard=noWouldRewievs())
                    else:
                        updateMessage(user_id,
                                      f"Спасибо за вашу оценку! Она поможет улучшить наш сервис ❤️\n\nНапишите ниже отзыв о работе вашего дизайнера. Это поможет нам в продвижении ⭐", keyboard=noWouldRewievs())
                    c.execute(f"UPDATE users SET flag = 'add-review' where user_id = '{user_id}'")
                    db.commit()
                elif flag == 'add-review':
                    if payload == 'no-would-rewievs':
                        c.execute(f"SELECT message_id FROM users WHERE user_id = '{user_id}'")
                        db.commit()
                        deleteMessage(c.fetchone()[0])
                        responce = messageSendUser(user_id,
                                                   f"Жаль, что не оставили отзыв :( Используйте кнопки, чтобы управлять ботом",
                                                   keyboard=menuKeyboard(user_id))
                        c.execute(f"DELETE FROM orders WHERE user_id = '{user_id}'")
                        c.execute(
                            f"UPDATE users SET flag = 'main', message_id = '{responce}' WHERE user_id = '{user_id}'")
                        db.commit()
            elif event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_user:
                    user_id = event.object.message['from_id']
                    message = event.object.message['text']
                    message_id = event.object.message['id']
                    arg = message.split(' ')
                    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
                    db.commit()
                    if c.fetchone() is not None:
                        c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
                        db.commit()
                        flag = c.fetchone()[0]
                    else:
                        flag = ""
                    if flag == 'describe-order':
                        c.execute(f"SELECT message_id FROM users WHERe user_id = '{user_id}'")
                        deleteMessage(c.fetchone()[0])
                        responce = messageSendUser(user_id, "Ваше сообщение добавлено к описанию заказа! Вы можете продолжить описывать заказ, а когда закончите, то нажмите на кнопку «Далее»", keyboard=cancelOrder(True, True))
                        c.execute(f"INSERT INTO order_messages VALUES ({user_id}, {message_id})")
                        c.execute(f"UPDATE users SET flag = 'describe-order-2', message_id = {responce} WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE orders SET status = 'Описывается' WHERE user_id = '{user_id}'")
                        db.commit()
                    elif flag == 'choice-service':
                        c.execute(f"SELECT message_id FROM users WHERe user_id = '{user_id}'")
                        deleteMessage(c.fetchone()[0])
                        responce = messageSendUser(user_id, "⛔ Используйте кнопки для работы с ботом!\n")
                        c.execute(
                            f"UPDATE users SET message_id = {responce} WHERE user_id = '{user_id}'")
                        time.sleep(2)
                        updateMessage(user_id, f"Возвращаю кнопки...")
                        updateMessage(user_id,
                                      f"Выберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥 \n\nСтраница: 1",
                                      template=services_list(0))
                    elif flag == 'look_service':
                        c.execute(f"SELECT message_id FROM users WHERe user_id = '{user_id}'")
                        deleteMessage(c.fetchone()[0])
                        responce = messageSendUser(user_id, "⛔ Используйте кнопки для работы с ботом!")
                        c.execute(
                            f"UPDATE users SET message_id = {responce} WHERE user_id = '{user_id}'")
                        time.sleep(2)
                        updateMessage(user_id, f"Возвращаю кнопки...")
                        c.execute(f"SELECT service FROM orders WHERe user_id = '{user_id}'")
                        db.commit()
                        service = c.fetchone()[0]
                        c.execute(f"SELECT about, price, attachment FROM services WHERE service = '{service}'")
                        responce = c.fetchall()
                        db.commit()
                        updateMessage(user_id,
                                      f"Вы выбрали «{service}»\n\n{responce[0][0]}\n\nЦена от: {responce[0][1]}₽",
                                      attachment=responce[0][2], keyboard=startOrder())
                    elif flag == 'describe-order-2':
                        responce = messageSendUser(user_id, "Ваше сообщение добавлено к описанию заказа! Вы можете продолжить описывать заказ, а когда закончите, то нажмите на кнопку «Далее»", keyboard=cancelOrder(True, True))
                        c.execute(f"INSERT INTO order_messages VALUES ({user_id}, {message_id})")
                        c.execute(f"UPDATE users SET message_id = {responce} WHERE user_id = '{user_id}'")
                        db.commit()
                        c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                        chat_id = c.fetchall()
                        if chat_id[0][0] > 0:
                            messageSendChat(chat_id[0][0], "Новое сообщение от клиента: ", forward_messages=message_id)
                        db.commit()
                    elif flag == 'wait-orders' or flag == 'pay-order' or flag == 'wait-approvals' or flag == 'dop-pay':
                        c.execute(f"INSERT INTO order_messages VALUES ({user_id}, {message_id})")
                        c.execute(f"UPDATE control_close_orders SET date_last_message = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id}'")
                        db.commit()
                        c.execute(f"SELECT chat_id FROM orders WHERE user_id = '{user_id}'")
                        messageSendChat(c.fetchone()[0], "Новое сообщение от клиента: ", forward_messages=message_id)
                        db.commit()
                    elif flag == 'activate_promocode':
                        c.execute(f"SELECT promocode FROM promocodes WHERE promocode = '{message}'")
                        db.commit()
                        if c.fetchall() != ():
                            c.execute(f"SELECT sale, used_count FROM promocodes WHERE promocode = '{message}'")
                            db.commit()
                            promo_info = c.fetchall()
                            c.execute(f"SELECT user_id FROM used_promocode WHERE promocode = '{message}'")
                            db.commit()
                            promo_used = c.fetchall()
                            if user_id in promo_used:
                                messageSendUser(user_id, "Вы уже использовали этот промокод ⛔")
                            else:
                                if promo_info[0][1] == -1:
                                    c.execute(f"SELECT money FROM pay_list WHERE user_id = '{user_id}'")
                                    db.commit()
                                    responce = c.fetchone()[0]
                                    c.execute(f"SELECT service, number FROM orders WHERE user_id = {user_id}")
                                    db.commit()
                                    order_info = c.fetchall()
                                    new_price = responce - (responce * promo_info[0][0] / 100)
                                    payform = createpay(new_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                                    updateMessage(user_id, f"Скидка {promo_info[0][0]}% по промокоду {message} применена!\n️Новая стоимость вашего заказа #{order_info[0][1]} {new_price}₽ \n\nВыполнение заказа займет до 3-х рабочих дней студии. Во время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡", payKeyboard(payform['link']))
                                    c.execute(f"UPDATE users SET flag = 'pay-order' WHERE user_id = '{user_id}'")
                                    c.execute(f"UPDATE pay_list SET id_form = '{payform['id']}' WHERE user_id = '{user_id}'")
                                    c.execute(f"INSERT INTO used_promocode VALUES ({user_id}, '{message}')")
                                    db.commit()
                                elif promo_info[0][1] == 0:
                                    messageSendUser(user_id, "Этот промокод уже нельзя использовать, так как исчерпан лимит его использований ⛔")
                                else:
                                    c.execute(f"SELECT money FROM pay_list WHERE user_id = '{user_id}'")
                                    db.commit()
                                    c.execute(f"SELECT service, number FROM orders WHERE user_id = {user_id}")
                                    db.commit()
                                    order_info = c.fetchall()
                                    responce = c.fetchone()[0]
                                    new_price = responce - (responce * promo_info[0][0] / 100)
                                    payform = createpay(new_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                                    updateMessage(user_id,
                                                  f"Скидка {promo_info[0][0]}% по промокоду {message} применена!\n️Новая стоимость вашего заказа #{order_info[0][1]} {new_price}₽ Выполнение заказа займет до 3-х рабочих дней студии. Во время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡",
                                                  payKeyboard(payform['link']))
                                    c.execute(f"UPDATE users SET flag = 'pay-order' WHERE user_id = '{user_id}'")
                                    c.execute(
                                        f"UPDATE pay_list SET id_from = '{payform['id']}' WHERE user_id = '{user_id}'")
                                    c.execute(f"UPDATE promocodes SET used_count = used_count - 1 WHERE promocode = '{message}'")
                                    db.commit()
                        else:
                            messageSendUser(user_id, "Такого промокода не существует ⛔")
                    elif flag == 'add-review':
                        c.execute(f"SELECT message_id FROM users WHERE user_id = '{user_id}'")
                        db.commit()
                        deleteMessage(c.fetchone()[0])
                        responce = messageSendUser(user_id,
                                      f"Спасибо за ваш отзыв! Используйте кнопки, чтобы управлять ботом",
                                      keyboard=menuKeyboard(user_id))
                        try:
                            addReview(user_id, message)
                        except Exception as e:
                            error("Невозможно оставить отзыв", e)
                        c.execute(f"SELECT number, service, data, status, attachment FROM orders WHERE user_id = '{user_id}' ORDER by data")
                        db.commit()
                        order_info = c.fetchall()
                        c.execute("SELECT review_chat FROM chats")
                        messageSendChat(c.fetchone()[0], f"Оставили новый отзыв  #{order_info[0][0]} | {order_info[0][1]} {order_info[0][3]} ({order_info[0][2]})\n\n » {message}\n\nПосмотреть — https://vk.com/topic-225244054_49626064", attachment=order_info[0][4])
                        c.execute(f"DELETE FROM orders WHERE user_id = '{user_id}'")
                        c.execute(f"UPDATE users SET flag = 'main', message_id = '{responce}' WHERE user_id = '{user_id}'")
                        db.commit()
    except Exception as e:
        error("order_longpoll.py", e)
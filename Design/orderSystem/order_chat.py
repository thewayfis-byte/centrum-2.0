import datetime
import json

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from Design.design_message import order
from Design.ЮKassa.payment import createpay, getMoney
from config.config import design_token, design_group_id, admins
from methods.design_message import messageSendUser, messageSendChat, error, deleteMessage, updateMessage, getPayList
from database.design_database import c, db
from keyboards.design_keyboard import orderDialog, payKeyboard, waitOrder, raything, clearKeyboard, dopPay
from methods.staff_methods import getDesigner, closeOrderAddBalance

vk_session = vk_api.VkApi(token=design_token)
longpoll = VkBotLongPoll(vk_session, design_group_id)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    chat_id = event.chat_id
                    manager_id = event.object.message['from_id']
                    message = event.object.message['text']
                    arg = message.split(' ')
                    c.execute(f"SELECT chat_id FROM orders WHERE chat_id = {chat_id}")
                    db.commit()
                    if arg[0] == "!айди":
                        messageSendChat(chat_id, f"⚡ | Айди чата: {chat_id}")
                    if c.fetchall() != ():
                        c.execute(f"SELECT user_id, manager_id, designer_id FROM orders WHERE chat_id = {chat_id}")
                        db.commit()
                        user_id = c.fetchall()
                        message_id = event.object.message['conversation_message_id']
                        c.execute(f"SELECT perms FROM staff_perms WHERE user_id = {manager_id}")
                        perms = c.fetchall()
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_order_chat" in perms or user_id[0][2] == manager_id:
                            if arg[0].lower() == '!написать':
                                messageSendChat(chat_id, "✅ | Сообщение отправлено")
                                if len(arg) > 1:
                                    message = message.replace(f"{arg[0]} ", '')
                                else:
                                    message = "-"
                                responce = vk_session.method("messages.getByConversationMessageId",
                                                             {"peer_id": 2000000000 + chat_id,
                                                              "conversation_message_ids": f"{message_id}",
                                                              "group_id": design_group_id})
                                length = len(responce['items'][0]['attachments']) - 1
                                b = 0
                                attachemts = ""
                                for i in range(len(responce['items'][0]['attachments'])):
                                    type = responce['items'][0]['attachments'][i]['type']
                                    owner_id = responce['items'][0]['attachments'][i][type]['owner_id']
                                    id = responce['items'][0]['attachments'][i][type]['id']
                                    access_key =responce['items'][0]['attachments'][i][type]['access_key']
                                    attachemts = attachemts + f"{type}{owner_id}_{id}_{access_key}"
                                    if b < length:
                                        attachemts = attachemts + ","
                                    b += 1
                                c.execute(
                                        f"UPDATE orders SET attachment = '{attachemts}' WHERE user_id = '{user_id[0][0]}'")
                                db.commit()
                                messageSendUser(user_id[0][0], f"⚡ Новое сообщение от дизайнера: {message}", attachment=attachemts)
                            elif message.lower() == '!клавиатура':
                                messageSendChat(chat_id, "✅ | Клавиатура выдана", keyboard=orderDialog())
                            elif message.lower() == '!завершить':
                                messageSendChat(chat_id, "Отлично! Работа отправлена клиенту, а статус заказ изменен на «Готов». \n\nЧтобы получить деньги на баланс, дождитесь, пока клиент не закроет заказ, а если прошло больше 24-х часов после последнего сообщения от клиента, то закройте его сами по кнопке «Закрыть заказ» ⭐")
                                responce = vk_session.method("messages.getByConversationMessageId",
                                                             {"peer_id": 2000000000 + chat_id,
                                                              "conversation_message_ids": f"{message_id}",
                                                              "group_id": design_group_id})
                                length = len(responce['items'][0]['attachments']) - 1
                                b = 0
                                attachemts = ""
                                attachemts_no_key = ""
                                for i in range(len(responce['items'][0]['attachments'])):
                                    type = responce['items'][0]['attachments'][i]['type']
                                    owner_id = responce['items'][0]['attachments'][i][type]['owner_id']
                                    id = responce['items'][0]['attachments'][i][type]['id']
                                    access_key = responce['items'][0]['attachments'][i][type]['access_key']
                                    attachemts = attachemts + f"{type}{owner_id}_{id}_{access_key}"
                                    attachemts_no_key = attachemts_no_key + f"{type}{owner_id}_{id}"
                                    if b < length:
                                        attachemts = attachemts + ","
                                        attachemts_no_key = attachemts_no_key + ','
                                    b += 1
                                messageSendUser(user_id[0][0],
                                            "Динь-Донь 🔔 Вам посылка!\n Если у вас не осталось правок, то закройте заказ, или он будет закрыт автоматически через 24 часа", attachment=attachemts)
                                c.execute(f"UPDATE orders SET attachment = '{attachemts}', status = 'Готов', attachment_no_key = '{attachemts_no_key}' WHERE user_id = '{user_id[0][0]}'")
                                c.execute(
                                    f"UPDATE control_close_orders SET date_last_message = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id[0][0]}'")
                                db.commit()
                            else:
                                try:
                                    if event.object.message['action']['type'] == 'chat_invite_user' or event.object.message['action']['type'] == 'chat_invite_user_by_link':
                                        messageSendChat(chat_id, "✅ | Клавиатура выдана", keyboard=orderDialog())
                                        c.execute(f"UPDATE orders SET have_manager = 1 WHERE user_id = '{user_id[0][0]}'")
                                        db.commit()
                                except Exception:
                                    pass
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "approve-order" in perms:
                            if arg[0] == '!одобрить': #!одобрить 30р
                                c.execute(f"SELECT status FROM orders WHERE user_id = '{user_id[0][0]}'")
                                responce = c.fetchone()[0]
                                if responce != 'В очереди' or responce != 'Выполняется' or responce != 'Готов':
                                    if len(arg) > 1:
                                        messageSendChat(chat_id, "✅ | Заказ одобрен")
                                        c.execute(f"SELECT service, number FROM orders WHERe user_id = '{user_id[0][0]}'")
                                        order_info = c.fetchall()
                                        db.commit()
                                        c.execute("SELECT nalog FROM nalog")
                                        nalog = c.fetchone()[0]
                                        db.commit()
                                        order_price = int(arg[1])
                                        order_price = order_price * nalog + order_price
                                        c.execute(f"SELECT message_id FROM users WHERE user_id = '{user_id[0][0]}'")
                                        deleteMessage(c.fetchone()[0])
                                        db.commit()
                                        payform = createpay(order_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                                        responce = messageSendUser(user_id[0][0],
                                                                   f"Ваш заказ #{order_info[0][1]} успешно одобрен и дизайнеры почти готовы начать работу 🧛‍♀️\nСтоимость вашего заказа {order_price}₽ Выполнение заказа займет до 3-х рабочих дней студии. Во время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡",
                                                                   keyboard=payKeyboard(payform['link'], True))
                                        c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                        c.execute(
                                            f"INSERT INTO pay_list VALUES ({user_id[0][0]}, {int(arg[1])}, '{payform['id']}', 0, '{order_info[0][0]}', 0)")
                                        c.execute(
                                            f"UPDATE users SET flag = 'pay-order', message_id = {responce} WHERE user_id = '{user_id[0][0]}'")
                                        c.execute(f"UPDATE orders SET status = 'Оплачивается' WHERE chat_id = '{chat_id}'")
                                        db.commit()
                                    else:
                                        messageSendChat(chat_id, "✅ | Заказ одобрен")
                                        c.execute(
                                            f"SELECT service, number FROM orders WHERE user_id = '{user_id[0][0]}'")
                                        order_info = c.fetchall()
                                        c.execute(f"SELECT price FROM services WHERE service = '{order_info[0][0]}'")
                                        order_price = c.fetchone()[0]
                                        old_price = order_price
                                        db.commit()
                                        if order_price > 0:
                                            c.execute("SELECT nalog FROM nalog")
                                            nalog = c.fetchone()[0]
                                            db.commit()
                                            order_price = order_price * nalog + order_price
                                            db.commit()
                                            c.execute(f"SELECT message_id FROM users WHERE user_id = '{user_id[0][0]}'")
                                            deleteMessage(c.fetchone()[0])
                                            payform = createpay(order_price, f'Заказ {order_info[0][1]} | {order_info[0][0]}')
                                            responce = messageSendUser(user_id[0][0], f"Ваш заказ #{order_info[0][1]} успешно одобрен и дизайнеры почти готовы начать работу 🧛‍♀️\nСтоимость вашего заказа {order_price}₽ Выполнение заказа займет до 3-х рабочих дней студии. Во время выполнения заказа с вами будут постоянно связываться и уточнять все детали разработки ⚡", keyboard=payKeyboard(payform['link'], True))
                                            c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                            c.execute(f"INSERT INTO pay_list VALUES ({user_id[0][0]}, {old_price}, '{payform['id']}', 0, '{order_info[0][0]}', 0)")
                                            c.execute(
                                                f"UPDATE users SET flag = 'pay-order', message_id = {responce} WHERE user_id = '{user_id[0][0]}'")
                                            c.execute(f"UPDATE orders SET status = 'Оплачивается' WHERE chat_id = '{chat_id}'")
                                            db.commit()
                                        else:
                                            c.execute(
                                                f"SELECT service, number, chat_id FROM orders WHERE user_id = '{user_id[0][0]}'")
                                            db.commit()
                                            responce = c.fetchall()
                                            designer = getDesigner(responce[0][0].replace(" FREE", ''))
                                            messageSendUser(user_id[0][0],
                                                          f"Отлично! Оплата вашего заказа подтверждена и он добавлен в очередь! \n\nЕсли у вас возникли вопросы, то пишите их ниже. Они будут отправлены вашему дизайнеру.\n\nСтатус вашего заказа - «Статус заказа»\nВаш заказ готов? - «Закрыть заказ»\n\nИсполнителем вашего заказа является {designer[1]} с рейтингом {designer[2]} ⭐",
                                                          keyboard=waitOrder())
                                            c.execute("SELECT designer_chat FROM chats")
                                            messageSendChat(c.fetchone()[0],
                                                            f"@id{designer[0]}({designer[1]}), вам пришел новый заказ #{responce[0][1]}. Вступите в чат по ссылке → {vk_session.method('messages.getInviteLink', {'peer_id': 2000000000 + responce[0][2], 'group_id': design_group_id})['link']}")
                                            c.execute(
                                                f"UPDATE orders SET status = 'В очереди', designer_id = {designer[0]}, data = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id[0][0]}'")
                                            c.execute(
                                                f"UPDATE users SET flag = 'wait-orders' WHERE user_id = '{user_id[0][0]}'")
                                            c.execute(
                                                f"INSERT INTO control_close_orders VALUES ({user_id[0][0]}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}')")
                                            c.execute(f"INSERT INTO check_free VALUES ({user_id[0][0]})")
                                            db.commit()
                                else:
                                    messageSendChat(chat_id, "Одобрить этот заказ нельзя, так как он оплачен")
                            elif arg[0] == '!доплата': #!доплата 100 1 10
                                if len(arg) > 3:
                                    messageSendChat(chat_id, "✅ | Доплата запрошена")
                                    c.execute("SELECT nalog FROM nalog")
                                    nalog = c.fetchone()[0]
                                    db.commit()
                                    order_price = int(arg[1])
                                    order_price = order_price * nalog + order_price
                                    c.execute(f"SELECT number FROM orders WHERE user_id = {user_id[0][0]}")
                                    db.commit()
                                    payform = createpay(order_price, f"Доплата за заказ #{c.fetchone()[0]}")
                                    c.execute(f"SELECT user_id FROM staff WHERE blokopad_id = '{arg[2]}'")
                                    responce = messageSendUser(user_id[0][0], f"Доплатите за ваш заказ {order_price}₽", keyboard=dopPay(payform['id'], int(arg[1]), payform['link'], c.fetchone()[0], float(arg[3])))
                                    c.execute(f"UPDATE users SET message_id = '{responce}', flag = 'dop-pay' WHERE user_id = '{user_id[0][0]}'")
                                    db.commit()
                            elif arg[0] == '!отказать':
                                if len(arg) > 2:
                                    responce = messageSendUser(user_id[0][0], message="Ваш заказ отказан. Убираем клавиатуру...", keyboard=clearKeyboard())
                                    c.execute(f"UPDATE users SET message_id = '{responce}' WHERE user_id = '{user_id[0][0]}'")
                                    db.commit()
                                    updateMessage(user_id[0][0], message=f"⛔ Ваш заказ отказан по причине: {message.replace(f'{arg[0]} ', '')}\n\nВыберите нужную категорию услуги 🔥",
                                                  keyboard=order['main']['keyboard'])
                                    messageSendChat(chat_id, "✅ | Заказ отказан")
                                    c.execute(f"UPDATE users SET flag = 'choice-service' where user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM orders WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id[0][0]}'")
                                    db.commit()
                                else:
                                    responce = messageSendUser(user_id[0][0],
                                                               message="Ваш заказ отказан. Убираем клавиатуру...",
                                                               keyboard=clearKeyboard())
                                    c.execute(
                                        f"UPDATE users SET message_id = '{responce}' WHERE user_id = '{user_id[0][0]}'")
                                    db.commit()
                                    updateMessage(user_id[0][0],
                                                  message=f"⛔ Ваш заказ отказан\n\nВыберите нужную услугу и нажмите на зеленую кнопку под ней, чтобы изучить ее более подробно 🔥",
                                                  keyboard=order['main']['keyboard'])
                                    messageSendChat(chat_id, "✅ | Заказ отказан")
                                    c.execute(
                                        f"UPDATE users SET flag = 'choice-service' where user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM orders WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id[0][0]}'")
                                    c.execute(f"DELETE FROM order_messages WHERE user_id = '{user_id[0][0]}'")
                                    db.commit()
                            elif arg[0] == '!проверка':
                                response = vk_session.method("groups.isMember",
                                                             {"group_id": design_group_id,
                                                              "user_id": user_id[0][0]})
                                if response == 1:
                                    messageSendChat(chat_id, "Пользователь подписан на сообщество")
                                else:
                                    messageSendChat(chat_id, "Пользователь не подписан на сообщество")
                            elif arg[0] == '!платеж': # добавить 100 1 0 удалить 100 1 получить
                                if len(arg) >3:
                                    if arg[1] == 'добавить':
                                        c.execute(f"SELECT user_id FROM staff WHERE blokopad_id = '{arg[3]}'")
                                        c.execute(f"INSERT INTO pay_list VALUES ({user_id[0][0]}, {float(arg[2])}, '', {c.fetchone()[0]}, '', 0)")
                                        db.commit()
                                        messageSendChat(chat_id, "Платеж добавлен к заказу. Деньги будут начислены после выполнения")
                                    elif arg[1] == 'удалить':
                                        c.execute(f"SELECT user_id FROM staff WHERE blokopad_id = '{arg[3]}'")
                                        c.execute(f"DELETE FROM pay_list WHERE user_id = {user_id[0][0]} AND designer = {c.fetchone()[0]} AND money = '{float(arg[2])}'")
                                        db.commit()
                                        messageSendChat(chat_id, "Платеж удален")
                                elif len(arg) > 1:
                                    if arg[1] == 'получить':
                                        messageSendChat(chat_id, getPayList(user_id[0][0]))
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "paid-order" in perms:
                            if message.lower() == '!оплатил':
                                c.execute(f"SELECT service, number, chat_id FROM orders WHERE user_id = '{user_id[0][0]}'")
                                db.commit()
                                responce = c.fetchall()
                                designer = getDesigner(responce[0][0])
                                updateMessage(user_id[0][0],
                                              f"Отлично! Оплата вашего заказа подтверждена и он добавлен в очередь! \n\nЕсли у вас возникли вопросы, то пишите их ниже. Они будут отправлены вашему дизайнеру.\n\nСтатус вашего заказа - «Статус заказа»\nВаш заказ готов? - «Закрыть заказ»\n\nИсполнителем вашего заказа является {designer[1]} с рейтингом {designer[2]} ⭐",
                                              keyboard=waitOrder())
                                c.execute("SELECT designer_chat FROM chats")
                                messageSendChat(c.fetchone()[0],
                                                f"@id{designer[0]}({designer[1]}), вам пришел новый заказ #{responce[0][1]}. Вступите в чат по ссылке → {vk_session.method('messages.getInviteLink', {'peer_id': 2000000000 + responce[0][2], 'group_id': design_group_id})['link']}")
                                c.execute(
                                    f"UPDATE orders SET status = 'В очереди', designer_id = {designer[0]}, data = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id[0][0]}'")
                                c.execute(f"UPDATE users SET flag = 'wait-orders' WHERE user_id = '{user_id[0][0]}'")
                                c.execute(
                                    f"SELECT bet FROM designer_service WHERE user_id = '{designer[0]}' AND service = '{responce[0][0]}'")
                                c.execute(
                                    f"UPDATE pay_list SET designer = '{designer[0]}', bet = '{c.fetchone()[0]}' WHERE user_id = '{user_id[0][0]}'")
                                c.execute(
                                    f"INSERT INTO control_close_orders VALUES ({user_id[0][0]}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}')")
                                c.execute(
                                    f"UPDATE staff SET orders_all = orders_all + 1, orders_no_does = orders_no_does + 1 WHERE user_id = '{designer[0]}'")
                                db.commit()
                                messageSendChat(chat_id, "Клиент оплатил заказ")
                                c.execute(f"SELECT id_form FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                db.commit()
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event_id = event.object.event_id
                manager_id = event.object.user_id
                peer_id = event.object.peer_id
                payload = event.object.payload
                chat_id = peer_id - 2000000000
                c.execute(f"SELECT chat_id FROM orders WHERE chat_id = {chat_id}")
                db.commit()
                if c.fetchall() != ():
                    c.execute(f"SELECT user_id, manager_id, designer_id FROM orders WHERE chat_id = {chat_id}")
                    db.commit()
                    user_id = c.fetchall()
                    c.execute(f"SELECT perms FROM staff_perms WHERE user_id = {manager_id}")
                    perms = c.fetchall()
                    if payload == "get_order_message":
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            c.execute(f"SELECT message_id FROM order_messages WHERE user_id = '{user_id[0][0]}'")
                            responce = c.fetchall()
                            length = len(responce) - 1
                            b = 0
                            message_ids = ""
                            for i in range(len(responce)):
                                message_ids = message_ids + f"{responce[i][0]}"
                                if b < length:
                                    message_ids = message_ids + ","
                                b += 1
                            messageSendChat(chat_id, f"Найдено {len(responce)} сообщений от пользователя: ", forward_messages=message_ids)
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Отправлено {len(responce)} сообщений'})}"})
                    elif payload == 'request-about':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            messageSendUser(user_id[0][0], "⚡ Новое сообщение от дизайнера: Опишите, пожалуйста, ваш заказ более подробно. Этот поможет нам сделать его более качественно 😉")
                            messageSendChat(chat_id, "✅ | Сообщение отправлено")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Сообщение отправлено'})}"})
                    elif payload == 'request-file':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            messageSendUser(user_id[0][0],
                                            "⚡ Новое сообщение от дизайнера: Отправьте ваш скин документом! Это сделает ваш заказ более качественным, а нам упростит задачу.\n\n⛔ Пока Вы не отправите ваш скин, я не смогу продолжить выполнять ваш заказ", attachment="photo-224824486_456239075")
                            messageSendChat(chat_id, "✅ | Сообщение отправлено")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Сообщение отправлено'})}"})
                    elif payload == 'ready':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            messageSendUser(user_id[0][0],
                                            "Статус вашего заказа изменен на «Готов» Если у вас не осталось правок, то закройте заказ или он будет закрыт автоматически через 24 часа")
                            messageSendChat(chat_id, "✅ | Статус заказа изменен на «Готов»")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Статус изменен'})}"})
                            c.execute(f"UPDATE orders SET status = 'Готов' WHERE chat_id = '{chat_id}'")
                            db.commit()

                    elif payload == 'waiting':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            messageSendUser(user_id[0][0],
                                            "Статус вашего заказа изменен на «В очереди»")
                            messageSendChat(chat_id, "✅ | Статус заказа изменен на «В очереди»")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Статус изменен'})}"})
                            c.execute(f"UPDATE orders SET status = 'В очереди' WHERE chat_id = '{chat_id}'")
                            c.execute(
                                f"UPDATE control_close_orders SET data_last_message = '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}' WHERE user_id = '{user_id[0][0]}'")
                            db.commit()
                    elif payload == 'progress':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            messageSendUser(user_id[0][0],
                                            "Статус вашего заказа изменен на «Выполняется»")
                            messageSendChat(chat_id, "✅ | Статус заказа изменен на «Выполняется»")
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": manager_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Статус изменен'})}"})
                            c.execute(f"UPDATE orders SET status = 'Выполняется' WHERE chat_id = '{chat_id}'")
                            db.commit()
                    elif payload == 'close_order_designer':
                        if manager_id in admins or user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms or user_id[0][2] == manager_id:
                            c.execute(f"SELECT date_last_message FROM control_close_orders WHERE user_id = {user_id[0][0]}")
                            date = c.fetchone()[0]
                            date = date.replace('.', ' ').replace(':', ' ').split(' ')
                            date = list(map(int, date))
                            date = datetime.datetime(day=date[0], month=date[1], year=date[2], hour=date[3],
                                                     minute=date[4], second=date[5])
                            date += datetime.timedelta(days=1)
                            if date < datetime.datetime.now():
                                print(date, datetime.datetime.now())
                                c.execute(f"SELECT status FROM orders WHERE user_id = '{user_id[0][0]}'")
                                if c.fetchone()[0] == 'Готов':
                                    c.execute(f"SELECT attachment FROM orders WHERE user_id = '{user_id[0][0]}'")
                                    if c.fetchall() != (('',),):
                                        c.execute(
                                            f"SELECT designer_id, manager_id, chat_id, number FROM orders WHERE user_id = '{user_id[0][0]}'")
                                        responce = c.fetchall()
                                        db.commit()
                                        message_id = messageSendUser(user_id[0][0], message="Убираем клавиатуру...",
                                                                     keyboard=clearKeyboard())
                                        c.execute(
                                            f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id[0][0]}'")
                                        db.commit()
                                        updateMessage(user_id[0][0],
                                                      "Спасибо, что сделали заказ у нас! Оцените работу вашего дизайнера от 1 до 5",
                                                      raything(responce[0][0], responce[0][2], responce[0][3]))
                                        closeOrderAddBalance(user_id[0][0])
                                        messageSendChat(responce[0][2],
                                                        "Клиент закрыл заказ. Деньги зачислены на ваш баланс")
                                        c.execute(f"DELETE FROM pay_list WHERE user_id = '{user_id[0][0]}'")
                                        c.execute(f"DELETE FROM control_close_orders WHERE user_id = '{user_id[0][0]}'")
                                        c.execute(
                                            f"UPDATE users SET flag = 'designer_raything', orders = orders + 1, message_id = {message_id} WHERE user_id = '{user_id[0][0]}'")
                                        db.commit()
                                    else:
                                        vk_session.method("messages.sendMessageEventAnswer",
                                                          {"event_id": event_id, "user_id": manager_id,
                                                           "peer_id": peer_id,
                                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Вы не можете закрыть этот заказ'})}"})

                                        messageSendChat(chat_id,
                                                        "⛔ | Вы не можете закрыть заказ, так как Вы не завершили выполнения заказа через команду !завершить. Отправьте работу клиенту при помощи команды !завершить")
                                else:
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event_id, "user_id": manager_id,
                                                       "peer_id": peer_id,
                                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Вы не можете закрыть этот заказ'})}"})

                                    messageSendChat(chat_id,
                                                    "⛔ | Вы не можете закрыть заказ, так как не поменяли его статус на «Готов»")

                            else:
                                vk_session.method("messages.sendMessageEventAnswer",
                                                  {"event_id": event_id, "user_id": manager_id,
                                                   "peer_id": peer_id,
                                                   "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Вы не можете закрыть этот заказ'})}"})

                                messageSendChat(chat_id, "⛔ | Вы не можете закрыть заказ, так как с момента последнего сообщения от клиента не прошло 24 часа")

    except Exception as e:
        error("order_chat.py", e)

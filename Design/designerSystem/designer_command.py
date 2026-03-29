import json
import  datetime

import vk_api
import subprocess
import sys
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from Centrum.accounting.methods import sendMessageChat
from Centrum.keyboard import checkPay
from config.config import centrum_group_id, centrum_token, admins
from database.design_database import c, db
from keyboards.design_keyboard import designChat, chapterAdmin
from methods.design_message import error
from methods.staff_methods import getOrders, getBalance, getRaythingAll, getOrdersNoManager, getOrdersNoClose, \
    getDialogNoManager, getStats, getStaff, getOrdersNeedDid, getOrdersBeLate
from Design.ЮKassa.payment import getInfo, createpay, checkstatus, getMoney

vk_session = vk_api.VkApi(token=centrum_token)
longpoll = VkBotLongPoll(vk_session, centrum_group_id)

while True:
    try:
        for event in longpoll.listen():
            print(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    user_id = event.object.message['from_id']
                    message = event.object.message['text']
                    message_id = event.object.message['id']
                    chat_id = event.chat_id
                    arg = message.split(' ')
                    if arg[0] == '.заказы':
                        if len(arg) > 2:
                            if arg[1] == 'без' and arg[2] == 'менеджера':
                                sendMessageChat(chat_id, getOrdersNoManager())
                        elif len(arg) > 1:
                            if arg[1] == 'незакрытые':
                                sendMessageChat(chat_id, getOrdersNoClose())
                        else:
                            sendMessageChat(chat_id, getOrders(user_id))
                    elif arg[0] == '.диалоги':
                        if len(arg) > 2:
                            if arg[1] == 'без' and arg[2] == 'менеджера':
                                sendMessageChat(chat_id, getDialogNoManager())
                        else:
                            sendMessageChat(chat_id, getOrders(user_id))
                    elif arg[0] == '.персонал':
                        sendMessageChat(chat_id, getStaff())
                    elif message.lower() == '.стата':
                        sendMessageChat(chat_id, getStats(user_id))
                    elif message.lower() == '.баланс':
                        sendMessageChat(chat_id, getBalance(user_id))
                    elif message.lower() == '.рейтинг':
                        sendMessageChat(chat_id, getRaythingAll(user_id))
                    elif arg[0] == '.клавиатура':
                        if len(arg) > 1:
                            if arg[1] == 'дизайнерская':
                                sendMessageChat(chat_id, "Клавиатура выдана", keyboard=designChat())
                            elif arg[1] == 'админская':
                                sendMessageChat(chat_id, "Клавиатура выдана", keyboard=designChat(True))
                    elif user_id in admins:
                        if arg[0] == '.рассылка':
                            subprocess.Popen(
                                                [sys.executable, 'Design/maillingSystem/mailling_start.py'])
                        elif arg[0] == '.платеж': #".платеж создать 100 Оплата заказ / .платеж найти айди"
                            if len(arg) > 2:
                                if arg[1] == 'найти':
                                    responce = getInfo(arg[2])
                                    if responce['status'] == 'succeeded':
                                        sendMessageChat(chat_id, f"Информация о платеже {responce['description']}:\n\nСтатус: Оплачен ✅\nМетод оплаты: {responce['payment_method']['type']}\nСумма: {responce['amount']['value']}₽ | {responce['income_amount']['value']}₽ ")
                                    else:
                                        sendMessageChat(chat_id,
                                                        f"Информация о платеже {responce['description']}:\n\nСтатус: Не оплачен 😐\nСумма: {responce['amount']['value']}₽")
                                elif arg[1] == 'создать':
                                    if len(arg) > 3:
                                        c.execute("SELECT nalog FROM nalog")
                                        db.commit()
                                        responce = createpay(float(arg[2]) + float(arg[2]) * c.fetchone()[0], message.replace(f"{arg[0]} {arg[1]} {arg[2]} ", ''))
                                        sendMessageChat(chat_id,
                                                        f"Платеж создан! Оплатите ваш заказ\n\nСсылка → {responce['link']}", keyboard=checkPay(responce['id'], message.replace(f"{arg[0]} {arg[1]} {arg[2]} ", '')))


            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event_id = event.object.event_id
                user_id = event.object.user_id
                peer_id = event.object.peer_id
                payload = event.object.payload
                chat_id = peer_id - 2000000000
                print(payload)
                if payload == 'get_orders_designer':
                    sendMessageChat(chat_id, getOrders(user_id))
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Список заказов отправлен'})}"})
                elif payload == 'get_balance_designer':
                    sendMessageChat(chat_id, getBalance(user_id))
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Баланс отправлен'})}"})
                elif payload == 'get_raything_designer':
                    sendMessageChat(chat_id, getRaythingAll(user_id))
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Рейтинги отправлены'})}"})
                elif payload == 'get_stats':
                    sendMessageChat(chat_id, getStats(user_id))
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Статистика отправлена'})}"})
                elif payload == 'admin_orders':
                    vk_session.method("messages.sendMessageEventAnswer",
                                     {"event_id": event_id, "user_id": user_id,
                                      "peer_id": peer_id,
                                      "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Раздел Заказы'})}"})
                    sendMessageChat(chat_id, "Раздел: Заказы", keyboard=chapterAdmin("orders"))
                elif payload == 'admin_settings':
                    vk_session.method("messages.sendMessageEventAnswer",
                                     {"event_id": event_id, "user_id": user_id,
                                      "peer_id": peer_id,
                                      "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Раздел Настройки'})}"})
                    sendMessageChat(chat_id, "Раздел: Настройки", keyboard=chapterAdmin("settings"))
                elif payload == 'no_have_manager':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Список отправлен'})}"})
                    sendMessageChat(chat_id, getOrdersNoManager())
                elif payload == 'no_close':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Список отправлен'})}"})
                    sendMessageChat(chat_id, getOrdersNoClose())
                elif payload == 'orders_need_did':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Список отправлен'})}"})
                    sendMessageChat(chat_id, getOrdersNeedDid())
                elif payload == 'orders_be_late':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Список отправлен'})}"})
                    sendMessageChat(chat_id, getOrdersBeLate())
                elif payload == 'free_avatar_on':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Включено'})}"})
                    c.execute(f"UPDATE design_settings SET on_free_avatar = 1")
                    db.commit()
                    sendMessageChat(chat_id, "Бесплатные Аватар включены", keyboard=chapterAdmin("settings"))
                elif payload == 'reviews_on':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Включено'})}"})
                    c.execute(f"UPDATE design_settings SET reviews = 1")
                    db.commit()
                    sendMessageChat(chat_id, "Обязательные отзывы включены", keyboard=chapterAdmin("settings"))
                elif payload == 'reviews_off':
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event_id, "user_id": user_id,
                                                       "peer_id": peer_id,
                                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Выключено'})}"})
                                    c.execute(f"UPDATE design_settings SET reviews = 0")
                                    db.commit()
                                    sendMessageChat(chat_id, "Обязательные отзывы выключены", keyboard=chapterAdmin("settings"))
                elif payload == 'free_avatar_off':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Выключено'})}"})
                    c.execute(f"UPDATE design_settings SET on_free_avatar = 0")
                    db.commit()
                    sendMessageChat(chat_id, "Бесплатные Аватар выключены", keyboard=chapterAdmin("settings"))
                elif payload == 'back_admin':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Главная клавиатура'})}"})
                    sendMessageChat(chat_id, "Бесплатные Аватар выключены", keyboard=designChat(True))
                try:
                    if payload['type'] == 'checkStatus':
                        if checkstatus(payload['id']):
                            vk_session.method("messages.sendMessageEventAnswer",
                                  {"event_id": event_id, "user_id": user_id,
                                   "peer_id": peer_id,
                                   "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Оплата подтверждена'})}"})

                        else:
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': f'Платеж не оплачен'})}"})
                except Exception:
                    pass


    except Exception as e:
        error("designer_command.py", e)
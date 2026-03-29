import datetime
import datetime
import json

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from methods.design_message import error, messageSendUser, deleteMessage, messageSendChat, updateMessage
from Design.design_message import help
from database.design_database import c, db
from methods.createChat import createChat
from methods.staff_methods import getWorker, addStats, getRaything, addBalance, addRaything
from keyboards.design_keyboard import raything, menuKeyboard

vk_session = vk_api.VkApi(token=design_token)
longpoll = VkBotLongPoll(vk_session, design_group_id)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
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
                    if flag == 'help':
                        c.execute(f"INSERT INTO help_messages VALUES ({user_id}, {message_id})")
                        c.execute(f"UPDATE users SET flag = 'dialog_to_manager' where user_id = '{user_id}'")
                        db.commit()

                        c.execute("SELECT manager FROM dialogs_count")
                        dialog_count = c.fetchone()[0] + 1
                        dialog_responce = createChat(vk_session, f"Тикет #{dialog_count}", design_group_id)
                        manager_id = getWorker("manager", "dialog")
                        c.execute(f"UPDATE dialogs_count SET manager = {dialog_count}")
                        c.execute(f"INSERT INTO manager_dialog VALUES ({user_id}, {manager_id[0]}, {dialog_count}, {dialog_responce[0]}, '{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}', 0)")
                        db.commit()

                        c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
                        db.commit()
                        deleteMessage(c.fetchone()[0])
                        messageSendUser(user_id,
                            f"Ваше сообщение отправлено менеджеру {manager_id[1]} с рейтингом {getRaything(manager_id[0], 'manager')} ⭐ Вам ответят в течении 10 минут рабочего времени студии:\n\nпн-пт: 07:00 — 22:00\nсб-вс: 12:00 — 22:00\n\n⛔ Не закрывайте тикет, пока Вы не получите ответ! Вы также можете продолжать отправлять сообщения, они будут доставлены",
                            keyboard=help[flag]['keyboard'])
                        c.execute("SELECT support_chat FROM chats")
                        db.commit()
                        messageSendChat(c.fetchone()[0], f"@id{manager_id[0]}({manager_id[1]}), поступило новое обращение в техническую поддержку! \nВойти в чат → {dialog_responce[1]['link']}")
                        addStats(manager_id[0], "dialog")
                    elif flag == 'dialog_to_manager':
                        c.execute(f"INSERT INTO help_messages VALUES ({user_id}, {message_id})")
                        c.execute(f"SELECT chat_id FROM manager_dialog WHERE user_id = '{user_id}'")
                        db.commit()
                        messageSendChat(c.fetchone()[0], "🚀 | Новое сообщение от пользователя: ", forward_messages=message_id)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event_id = event.object.event_id
                user_id = event.object.user_id
                peer_id = event.object.peer_id
                payload = event.object.payload
                c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
                db.commit()
                if c.fetchone() != ():
                    c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
                    db.commit()
                    flag = c.fetchone()[0]
                else:
                    flag = ""
                if flag == 'dialog_to_manager':
                    if payload == 'close_ticket':
                        c.execute(f"SELECT manager_id, chat_id, number_dialog FROM manager_dialog WHERE user_id = '{user_id}'")
                        responce = c.fetchall()
                        info_dialog = [responce[0][0], responce[0][1], responce[0][2]]
                        db.commit()
                        c.execute(f"SELECT name FROM staff WHERE user_id = '{info_dialog[0]}'")
                        db.commit()
                        info_dialog.append(c.fetchone()[0])
                        vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Оцените работу менеджера'})}"})
                        responce = messageSendUser(user_id, f"Разговор с менеджером завершен, надеемся вам удалось получить ответы на все вопросы 👑 \n\nОцените работу менеджера {info_dialog[3]} от 1 до 5 ⭐", keyboard=raything(info_dialog[0], info_dialog[1], info_dialog[2]))
                        c.execute("SELECT manager_bet FROM bet")
                        bet = c.fetchone()[0]
                        c.execute(f"UPDATE users SET message_id = {responce} WHERE user_id = {user_id}")
                        c.execute(f"UPDATE users SET flag = 'raything_manager' where user_id = '{user_id}'")
                        db.commit()
                        messageSendChat(info_dialog[1], f"Пользователь завершил диалог! Отличная работа 😉 На ваш баланс начислена сумма {bet}₽")
                        c.execute(
                            f"UPDATE staff SET dialog_no_does = dialog_no_does - 1, dialog_did = dialog_did + 1 WHERE user_id = '{user_id}'")
                        db.commit()
                        addBalance(info_dialog[0], bet, 'manager', info_dialog[2])
                elif flag == 'raything_manager':
                    addRaything(payload['manager_id'], payload['raything'], "manager", payload["number"])
                    messageSendChat(payload['chat_id'], f"Пользователь оценил вашу работу на {payload['raything']} ⭐")
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Главное меню»'})}"})
                    updateMessage(user_id,
                                               f"Спасибо за вашу оценку! Она поможет улучшить наш сервис ❤️\n\nИспользуйте кнопки, чтобы управлять ботом",
                                               keyboard=menuKeyboard(user_id))
                    c.execute(f"UPDATE users SET flag = 'main' where user_id = '{user_id}'")
                    c.execute(f"DELETE FROM manager_dialog WHERE user_id = '{user_id}'")
                    c.execute(f"DELETE FROM help_messages WHERE user_id = '{user_id}'")
                    db.commit()

    except Exception as e:
        error("help_longpoll.py", e)
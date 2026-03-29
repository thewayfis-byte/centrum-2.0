
import json

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from methods.design_message import messageSendUser, messageSendChat, error
from database.design_database import c, db
from keyboards.design_keyboard import managerDialog

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
                    c.execute(f"SELECT chat_id FROM manager_dialog WHERE chat_id = {chat_id}")
                    db.commit()
                    if c.fetchall() != ():
                        c.execute(f"SELECT user_id, manager_id FROM manager_dialog WHERE chat_id = {chat_id}")
                        db.commit()
                        user_id = c.fetchall()
                        message_id = event.object.message['conversation_message_id']
                        c.execute(f"SELECT perms FROM staff_perms WHERE user_id = {manager_id}")
                        perms = c.fetchall()
                        if user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms:
                            if arg[0].lower() == '!написать':
                                messageSendChat(chat_id, "✅ | Сообщение отправлено")
                                message = message.replace(f"{arg[0]} ", '')
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
                                messageSendUser(user_id[0][0], f"⚡ Новое сообщение от менеджера: {message}", attachment=attachemts)
                            elif message.lower() == '!клавиатура':
                                messageSendChat(chat_id, "✅ | Клавиатура выдана", keyboard=managerDialog())
                            else:
                                try:
                                    if event.object.message['action']['type'] == "chat_invite_user_by_link" or event.object.message['action']['type'] == "chat_invite_user":
                                        messageSendChat(chat_id, "✅ | Клавиатура выдана", keyboard=managerDialog())
                                        c.execute(f"UPDATE manager_dialog SET have_manager WHERE user_id = '{user_id[0][0]}'")
                                        db.commit()
                                except Exception:
                                    pass
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event_id = event.object.event_id
                manager_id = event.object.user_id
                peer_id = event.object.peer_id
                payload = event.object.payload
                chat_id = peer_id - 2000000000
                c.execute(f"SELECT chat_id FROM manager_dialog WHERE chat_id = {chat_id}")
                db.commit()
                if c.fetchall() is not None:
                    c.execute(f"SELECT user_id, manager_id FROM manager_dialog WHERE chat_id = {chat_id}")
                    db.commit()
                    user_id = c.fetchall()
                    c.execute(f"SELECT perms FROM staff_perms WHERE user_id = {manager_id}")
                    perms = c.fetchall()
                    if payload == "get_manager_message":
                        if user_id[0][1] == manager_id or "*" in perms or "send_manager_chat" in perms:
                            c.execute(f"SELECT message_id FROM help_messages WHERE user_id = '{user_id[0][0]}'")
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
    except Exception as e:
        error("manager_chat.py", e)

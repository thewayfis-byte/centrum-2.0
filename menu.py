import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from methods.design_message import error, startMessage, useKeyboard, deleteMessage, updateMessageID, messageSendChat
from keyboards.design_keyboard import menuKeyboard
from database.design_database import c, db

vk_session = vk_api.VkApi(token=design_token)
longpoll = VkBotLongPoll(vk_session, design_group_id)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_user:
                    user_id = event.object.message['from_id']
                    message = event.object.message['text']
                    arg = message.split(' ')
                    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
                    db.commit()
                    if c.fetchone() is None:
                        c.execute(f"INSERT INTO users VALUES ({user_id}, 'main', 0, -1, 1)")
                        db.commit()
                    c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
                    db.commit()
                    flag = c.fetchone()[0]
                    if flag == 'main':
                        if message.lower() == "начать":
                            c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
                            db.commit()
                            if c.fetchone()[0] != -1:
                                c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
                                db.commit()
                                deleteMessage(c.fetchone()[0])
                            responce = startMessage(user_id)
                            c.execute(f"UPDATE users SET message_id = {responce} WHERE user_id = {user_id}")
                            db.commit()
                        else:
                            c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
                            db.commit()
                            if c.fetchone()[0] != -1:
                                c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
                                db.commit()
                                deleteMessage(c.fetchone()[0])
                            responce = useKeyboard(user_id, menuKeyboard(user_id))
                            c.execute(f"UPDATE users SET message_id = {responce} WHERE user_id = {user_id}")
                            db.commit()
                    elif flag == "choice-service" or flag == "look_service" or flag == "main":
                        if message.lower() != "начать":
                            messageSendChat(340, f"У пользователя возможно проблема: \n→ {message}\n\nСсылка на чат: https://vk.com/gim{design_group_id}?sel={user_id}")
    except Exception as e:
        error("menu.py", e)
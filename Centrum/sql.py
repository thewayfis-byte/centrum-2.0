import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll, VkBotEvent

from methods.centrum_message import error
from config.config import centrum_token, centrum_group_id, admins
from database.design_database import c, db
from methods.staff_methods import getPerms
from methods.centrum_message import messageSendChat

vk_session = vk_api.VkApi(token=centrum_token)
longpoll = VkBotLongPoll(vk_session, centrum_group_id)

while True:
    #try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    user_id = event.object.message['from_id']
                    chat_id = event.chat_id
                    message = event.object.message['text']
                    arg = message.split(' ')
                    if "*" in getPerms(user_id) or "sql_system" or user_id in admins:
                        if arg[0] == '!sql':
                            if len(arg) > 1:
                                try:
                                    c.execute(message.replace(f"{arg[0]} ", ''))
                                    db.commit()
                                    messageSendChat(chat_id, f"🚀 | Ответ от MYSQL: {c.fetchall()}")
                                except Exception as e:
                                    messageSendChat(chat_id, f"🚀 | Ответ от MYSQL: {e}")
                            else:
                                messageSendChat(chat_id, "⛔ | Вы забыли указать SQL-синтаксис")
    #except Exception as e:
        #error("sql.py", e)
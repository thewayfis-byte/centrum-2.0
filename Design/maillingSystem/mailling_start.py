import json
import time

import vk_api

from keyboards.design_keyboard import cancelMailling
from methods.design_message import messageSendChat, messageSendUser
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from database.design_database import c, db
vk_session = vk_api.VkApi(token=design_token)
longpoll = VkBotLongPoll(vk_session, design_group_id)

user_id = 501285409
def updateMessage(message, keyboard=None, attachment=None, template=None):
    vk_session.method("messages.edit", {"peer_id": user_id, "message_id": id, "message": message, "keyboard": keyboard, "attachment": attachment, "template": template})


id = messageSendUser(user_id, "📤 » Запускаю рассылку...\n\nПолучение пользователей")
c.execute("SELECT user_id FROM users WHERE flag = 'main' OR flag = 'choice-service' OR flag = 'look_service'")
db.commit()
responce = c.fetchall()
time.sleep(3)
updateMessage(f"📤 » Получено {len(responce)} пользователей\n\nНачинаю сортировку...")
users = []
a = 0
for i in range(len(responce)):
    api = vk_session.method("messages.isMessagesFromGroupAllowed", {"user_id": responce[i][0], "group_id": design_group_id})
    if api['is_allowed'] == 1:
        users.append(responce[i][0])
    if a == 20:
        a = 0
        updateMessage(
            f"📤 » Сортировка\n\nОтсортировано {i}/{len(responce)} пользователей\nПолучат рассылку {len(users)}")
    a+=1
updateMessage(
            f"📤 » Рассылка\n\n\nПолучат рассылку {len(users)} пользователей")
peers = ""
a = 0
for i in range(len(users)):
    a+=1
    peers = peers + f",{users[i]}"
    if a == 99:
        response = vk_session.method("messages.send", {"peer_ids": peers, "message": "Привет! 👋 У вас возникли проблемы по работе с ботом? \n\n🎬 Посмотрите наше новое видео, оно вам поможет с оформлением заказа!", "keyboard": cancelMailling(),
                                                       "attachment": "video-224824486_456239017",  "random_id": 0})
        peers = ""
response = vk_session.method("messages.send", {"peer_ids": peers, "message": "Привет! 👋 У вас возникли проблемы по работе с ботом? \n\n🎬 Посмотрите наше новое видео, оно вам поможет с оформлением заказа!", "keyboard": cancelMailling(),
                                                       "attachment": "video-224824486_456239017",  "random_id": 0})
updateMessage(f"📤 » Рассылка завершена! {len(users)} пользователей получили ее.")




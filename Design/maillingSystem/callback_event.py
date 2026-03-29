import vk_api
import json
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from methods.design_message import error, updateMessage, startMessage
from database.design_database import c, db

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
                if payload == 'cancelMailling':
                    c.execute(f"UPDATE users SET mailling = 0 WHERE user_id = '{user_id}'")
                    db.commit()
                    vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы больше не будете получать рассылки!'})}"})
                elif payload == 'enableMailling':
                    c.execute(f"UPDATE users SET mailling = 1 WHERE user_id = '{user_id}'")
                    db.commit()
                    vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы включили получение рассылок!'})}"}) 
                    
    except Exception as e:
        error("maillingSystem/callback.py", e)
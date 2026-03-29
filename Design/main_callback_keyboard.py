import vk_api
import json
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import design_token, design_group_id
from keyboards.design_keyboard import menuKeyboard, services_list, categoris
from methods.design_message import error, updateMessage, startMessage
from design_message import help, order
from methods.usersSetting import getFullName, getFlag, updateFlag
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
                flag = getFlag(user_id)
                if payload == 'faq':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event_id, "user_id": user_id,
                                       "peer_id": peer_id,
                                       "event_data": f"{json.dumps({'type': 'open_link', 'link': 'https://vk.com/@blokopad-faq-chasto-zadavaemye-voprosy'})}"})
                elif payload == 'reviews':
                    vk_session.method("messages.sendMessageEventAnswer",
                                      {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                       "peer_id": event.object.peer_id,
                                       "event_data": f"{json.dumps({'type': 'open_link', 'link': 'https://vk.com/topic-225244054_49626064'})}"})
                if flag == 'main':
                    if payload == 'help':
                        vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Помощь»'})}"})
                        updateMessage(user_id, message=help[flag]['message'], keyboard=help[flag]['keyboard'])
                        updateFlag(user_id, 'help')
                    elif payload == 'new_order':
                        try:
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Услуги»'})}"})
                        except Exception:
                            pass
                        updateMessage(user_id, message=order[flag]['message'], keyboard=categoris())
                        updateFlag(user_id, 'choice-service')
                    elif payload == 'cancelMailling' or payload == 'enableMailling':
                        updateMessage(user_id,
                                      f"Привет, {getFullName(user_id)['first_name']} 👋 Я умный робот-помощник студии NowkeArt\n\nИспользуй кнопки, чтобы управлять мною, а если у вас возникли, то Вы всегда можете обратиться к менеджеру в разделе «Помощь»\n\n🎬 Видеоинструкция — https://vk.com/video-224824486_456239017",
                                      keyboard=menuKeyboard(user_id))

                    elif payload == 'new_order_free':
                        c.execute("SELECT on_free_avatar FROM design_settings")
                        db.commit()
                        if c.fetchone()[0] == 1:
                            response = vk_session.method("groups.isMember",
                                                         {"group_id": design_group_id, "user_id": event.object.user_id})
                            if response == 1:
                                c.execute(f"SELECT user_id FROM check_free WHERE user_id = '{user_id}'")
                                db.commit()
                                if c.fetchall() == ():
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                                       "peer_id": event.object.peer_id,
                                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Выберите бесплатный аватар'})}"})
                                    updateMessage(user_id, message=order[flag]['message'], template=services_list(0, 0))
                                    updateFlag(user_id, 'choice-service')
                                else:
                                    vk_session.method("messages.sendMessageEventAnswer",
                                                      {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                                       "peer_id": event.object.peer_id,
                                                       "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы уже получали бесплатный аватар'})}"})
                            else:
                                vk_session.method("messages.sendMessageEventAnswer",
                                                  {"event_id": event.object.event_id, "user_id": event.object.user_id,
                                                   "peer_id": event.object.peer_id,
                                                   "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы не подписались на сообщество'})}"})
                                vk_session.method("messages.sendMessageEventAnswer",
                                                  {"event_id": event_id, "user_id": user_id,
                                                   "peer_id": peer_id,
                                                   "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Услуги»'})}"})
                                updateMessage(user_id, message=order[flag]['message'], template=order[flag]['keyboard'])
                                updateFlag(user_id, 'choice-service')
                        else:
                            updateMessage(user_id, f"Привет, {getFullName(user_id)['first_name']} 👋 Я умный робот-помощник студии NowkeArt\n\nИспользуй кнопки, чтобы управлять мною, а если у вас возникли, то Вы всегда можете обратиться к менеджеру в разделе «Помощь»\n\n🎬 Видеоинструкция — https://vk.com/video-224824486_456239017", keyboard=menuKeyboard(user_id))
                            vk_session.method("messages.sendMessageEventAnswer",
                                              {"event_id": event_id, "user_id": user_id,
                                               "peer_id": peer_id,
                                               "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Акция недоступна'})}"})

                elif flag == 'help' or flag == 'choice-service':
                    if payload == 'back_to_menu':
                        vk_session.method("messages.sendMessageEventAnswer",
                                          {"event_id": event_id, "user_id": user_id,
                                           "peer_id": peer_id,
                                           "event_data": f"{json.dumps({'type': 'show_snackbar', 'text': 'Вы в разделе «Главное меню»'})}"})
                        updateMessage(user_id, message=f"Привет, {getFullName(user_id)['first_name']} 👋 Я умный робот-помощник студии NowkeArt\n\nИспользуй кнопки, чтобы управлять мною, а если у вас возникли, то Вы всегда можете обратиться к менеджеру в разделе «Помощь\n\n🎬 Видеоинструкция — https://vk.com/video-224824486_456239017", keyboard=menuKeyboard(user_id))
                        updateFlag(user_id, 'main')
    except Exception as e:
        error("main_callback_keyboard.py", e)
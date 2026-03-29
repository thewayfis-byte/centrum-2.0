import subprocess
import sys
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config.config import centrum_token, centrum_group_id, admins
from methods.staff_methods import getPerms
from methods.centrum_message import noPerms, messageSendChat, error

vk_session = vk_api.VkApi(token=centrum_token)
longpoll = VkBotLongPoll(vk_session, centrum_group_id)

#-=-=-=-=-=-=- АвтоСтарт -=-=-=-=-=-=-
#Design

design_menu = subprocess.Popen([sys.executable, 'Design/menu.py'])
design_main_callback_keyboard = subprocess.Popen([sys.executable, 'Design/main_callback_keyboard.py'])
design_help_longpoll = subprocess.Popen([sys.executable, 'Design/helpSystem/help_longpoll.py'])
design_manager_chat = subprocess.Popen([sys.executable, 'Design/helpSystem/manager_chat.py'])
design_order_longpoll = subprocess.Popen([sys.executable, 'Design/orderSystem/order_longpoll.py'])
design_order_chat = subprocess.Popen([sys.executable, 'Design/orderSystem/order_chat.py'])
design_designer_command = subprocess.Popen([sys.executable, 'Design/designerSystem/designer_command.py'])
design_mailling_callback = subprocess.Popen([sys.executable, 'Design/maillingSystem/callback_event.py'])

#Centrum

sql = subprocess.Popen([sys.executable, 'Centrum/sql.py'])

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    user_id = event.object.message['from_id']
                    chat_id = event.chat_id
                    message = event.object.message['text']
                    arg = message.split(' ')
                    if "*" in getPerms(user_id) or "manage_system" or user_id in admins:
                        if arg[0] == ".продукт":
                            if len(arg) > 1:
                                if arg[1] == "старт":
                                    if len(arg) > 2:
                                        if arg[2] == "design":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно запущен")
                                            design_menu = subprocess.Popen([sys.executable, 'Design/menu.py'])
                                            design_main_callback_keyboard = subprocess.Popen(
                                                [sys.executable, 'Design/main_callback_keyboard.py'])
                                            design_help_longpoll = subprocess.Popen(
                                                [sys.executable, 'Design/helpSystem/help_longpoll.py'])
                                            design_manager_chat = subprocess.Popen(
                                                [sys.executable, 'Design/helpSystem/manager_chat.py'])
                                            design_order_longpoll = subprocess.Popen(
                                                [sys.executable, 'Design/orderSystem/order_longpoll.py'])
                                            design_order_chat = subprocess.Popen(
                                                [sys.executable, 'Design/orderSystem/order_chat.py'])
                                            design_designer_command = subprocess.Popen(
                                                [sys.executable, 'Design/designerSystem/designer_command.py'])
                                            design_mailling_callback = subprocess.Popen(
                                                [sys.executable, 'Design/maillingSystem/callback_event.py'])
                                        elif arg[2] == "centrum":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно запущен")
                                        else:
                                            messageSendChat(chat_id, f"⛔ | Не существует проекта {arg[2]} \n" + "Использование → .продукт {действие} {проект}")
                                    else:
                                        messageSendChat(chat_id, f"⛔ | Вы не указали проект \nИспользование → .продукт {arg[1]} " + "{проект}")
                                elif arg[1] == 'стоп':
                                    if len(arg) > 2:
                                        if arg[2] == "design":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно выключен")
                                            design_menu.kill()
                                            design_main_callback_keyboard.kill()
                                            design_help_longpoll.kill()
                                            design_manager_chat.kill()
                                            design_order_longpoll.kill()
                                            design_order_chat.kill()
                                            design_designer_command.kill()
                                            design_mailling_callback.kill()
                                        elif arg[2] == "centrum":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно запущен")
                                        else:
                                            messageSendChat(chat_id, f"⛔ | Не существует проекта {arg[2]} \n" + "Использование → .продукт {действие} {проект}")
                                    else:
                                        messageSendChat(chat_id, f"⛔ | Вы не указали проект \nИспользование → .продукт {arg[1]} " + "{проект}")
                                elif arg[1] == 'рестарт':
                                    if len(arg) > 2:
                                        if arg[2] == "design":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно перезапущен")
                                            design_menu.kill()
                                            design_main_callback_keyboard.kill()
                                            design_help_longpoll.kill()
                                            design_manager_chat.kill()
                                            design_order_longpoll.kill()
                                            design_order_chat.kill()
                                            design_designer_command.kill()
                                            design_menu = subprocess.Popen([sys.executable, 'Design/menu.py'])
                                            design_main_callback_keyboard = subprocess.Popen(
                                                [sys.executable, 'Design/main_callback_keyboard.py'])
                                            design_help_longpoll = subprocess.Popen(
                                                [sys.executable, 'Design/helpSystem/help_longpoll.py'])
                                            design_manager_chat = subprocess.Popen(
                                                [sys.executable, 'Design/helpSystem/manager_chat.py'])
                                            design_order_longpoll = subprocess.Popen(
                                                [sys.executable, 'Design/orderSystem/order_longpoll.py'])
                                            design_order_chat = subprocess.Popen(
                                                [sys.executable, 'Design/orderSystem/order_chat.py'])
                                            design_designer_command = subprocess.Popen(
                                                [sys.executable, 'Design/designerSystem/designer_command.py'])
                                            design_mailling_callback = subprocess.Popen(
                                                [sys.executable, 'Design/maillingSystem/callback_event.py'])
                                        elif arg[2] == "centrum":
                                            messageSendChat(chat_id, "🚀 | Продукт успешно запущен")
                                        else:
                                            messageSendChat(chat_id, f"⛔ | Не существует проекта {arg[2]} \n" + "Использование → .продукт {действие} {проект}")
                                    else:
                                        messageSendChat(chat_id, f"⛔ | Вы не указали проект \nИспользование → .продукт {arg[1]} " + "{проект}")
                                else:
                                    messageSendChat(chat_id, f"⛔ | Не существует действия {arg[1]} \n" + "Использование → .продукт {действие} {проект}")
                            else:
                                messageSendChat(chat_id, "⛔ | Вы не указали аргументы команды .продукт \nИспользование → .продукт {действие} {проект}")
                    else:
                        noPerms(chat_id)
    except Exception as e:
        error("start.py", e)

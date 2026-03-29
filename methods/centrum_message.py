import vk_api
from config.config import centrum_token, admins

vk_session = vk_api.VkApi(token=centrum_token)

def messageSendChat(chat_id, message, keyboard=None, attachment=None):
    response = vk_session.method("messages.send", {"chat_id": chat_id, "message": message, "keyboards": keyboard, "attachment": attachment, "random_id": 0})
    return response

def noPerms(user_id):
    response = messageSendChat(user_id, "⛔ | У вас нет прав на использование этой команды O_o")
    return response

def messageSendUser(user_id, message, keyboard=None, attachment=None):
    response = vk_session.method("messages.send", {"user_id": user_id, "message": message, "keyboards": keyboard, "attachment": attachment, "random_id": 0})
    return response

def error(file, error):
    for i in range(len(admins)):
        messageSendUser(admins[i], f"😰 | Ошибка в {file} \n → {error}")
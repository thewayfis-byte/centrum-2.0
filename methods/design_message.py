import vk_api
from config.config import design_token, admins, design_group_id, user_token
from keyboards.design_keyboard import menuKeyboard
from methods.staff_methods import getRaything
from methods.usersSetting import getFullName
from database.design_database import c, db


vk_session = vk_api.VkApi(token=design_token)
user_session = vk_api.VkApi(token=user_token)

def messageSendChat(chat_id, message, keyboard=None, attachment=None, forward_messages=None):
    response = vk_session.method("messages.send", {"chat_id": chat_id, "message": message, "keyboard": keyboard, "attachment": attachment, "forward_messages": forward_messages, "random_id": 0})
    return response

def noPerms(user_id):
    response = messageSendChat(user_id, "⛔ | У вас нет прав на использование этой команды O_o")
    return response

def messageSendUser(user_id, message, keyboard=None, attachment=None, template=None):
    response = vk_session.method("messages.send", {"user_id": user_id, "message": message, "keyboard": keyboard, "attachment": attachment, "template": template,"random_id": 0})
    return response

def startMessage(user_id):
    response = messageSendUser(user_id, f"Привет, {getFullName(user_id)['first_name']} 👋 Я умный робот-помощник студии NowkeArt\n\nИспользуй кнопки, чтобы управлять мною, а если у вас возникли, то Вы всегда можете обратиться к менеджеру в разделе «Помощь»\n\n🎬 Видеоинструкция — https://vk.com/video-224824486_456239017", keyboard=menuKeyboard(user_id))
    return response

def useKeyboard(user_id, keyboard):
    response = messageSendUser(user_id,
                               f"Это сообщение никто не увидит 😭 Используйте кнопки, чтобы сделать заказ, а если у вас возникли, то Вы всегда можете обратиться к менеджеру в разделе «Помощь» ",
                               keyboard=keyboard)
    return response

def error(file, error):
    try:
        for i in range(len(admins)):
            messageSendUser(admins[i], f"😰 | Ошибка в {file} \n → {error}")
    except Exception as e:
        pass

def deleteMessage(message_id):
    try:
        vk_session.method("messages.delete", {"message_ids": f"{message_id}", "delete_for_all": 1})
    except Exception:
        pass

def updateMessage(user_id, message, keyboard=None, attachment=None, template=None):
    c.execute(f"SELECT message_id FROM users WHERE user_id = {user_id}")
    db.commit()
    vk_session.method("messages.edit", {"peer_id": user_id, "message_id": c.fetchone()[0], "message": message, "keyboard": keyboard, "attachment": attachment, "template": template})

def updateMessageID(responce, user_id):
    c.execute(f"UPDATE users SET message_id = {responce} WHERE user_id = {user_id}")
    db.commit()

def getPayList(user_id):
    c.execute(f"SELECT designer, money, bet FROM pay_list WHERE user_id = '{user_id}'")
    responce = c.fetchall()
    db.commit()
    answer = "Платежи этого заказа"
    for i in range(len(responce)):
        c.execute(f"SELECT name FROM staff WHERe user_id = {responce[i][0]}")
        answer = answer + f"\n@id{responce[i][0]}({c.fetchone()[0]}) {responce[i][1]}₽ {responce[i][2]}%"
    return answer
def addReview(user_id, message):
    c.execute(f"SELECT number, service, designer_id, attachment_no_key FROM orders WHERE user_id = '{user_id}'")
    db.commit()
    responce = c.fetchall()
    c.execute(f"SELECT name FROM staff WHERE user_id = '{responce[0][2]}'")
    designer = c.fetchone()[0]
    user_session.method("board.createComment", {"group_id": design_group_id, "topic_id": 49551847, "message": f"Отзыв от @id{user_id}({getFullName(user_id)['first_name']} {getFullName(user_id)['last_name']})\n\n» {message} \n\nЗаказ #{responce[0][0]} | {responce[0][1]}. Выполнил дизайнер {designer} с рейтингом {getRaything(responce[0][2], 'designer')} ⭐", "from_group": 1, "attachments": f"{responce[0][3]}"})


import vk_api
import json
from config.config import design_token, admins
from database.design_database import c, db

vk_session = vk_api.VkApi(token=design_token)

def getFullName(user_id):
    response = vk_session.method("users.get", {"user_ids": user_id, "fields": "screen_name,last_name"})
    answer = {"first_name": response[0]['first_name'],
            "last_name": response[0]["last_name"],
            "domen": response[0]["screen_name"]
            }
    answer = json.dumps(answer, ensure_ascii=False)
    answer = json.loads(answer)
    return answer

def newUser(user_id):
    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    db.commit()
    if c.fetchone() is None:
        c.execute(f"INSERT INTO users VALUES ({user_id}, 'main', 0, -1)")
        db.commit()
    c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
    db.commit()
    return c.fetchone()[0]

def getFlag(user_id):
    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    db.commit()
    if c.fetchone() != ():
        c.execute(f"SELECT flag FROM users WHERE user_id = '{user_id}'")
        db.commit()
        flag = c.fetchone()[0]
    else:
        flag = ""
    return flag

def updateFlag(user_id, flag):
    c.execute(f"UPDATE users SET flag = '{flag}' WHERE user_id = '{user_id}'")
    db.commit()
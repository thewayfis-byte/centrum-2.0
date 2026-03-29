import json
from datetime import datetime

import vk_api
from yookassa import Configuration, Payment
from config.config import centrum_token
from database.design_database import c, db

vk_session = vk_api.VkApi(token=centrum_token)

Configuration.account_id = 0
Configuration.secret_key = ''

def getPayments(date):
    get = Payment.list({
        "created_at.gte": f"{date}",
        "status": "succeeded",
        "limit": 100
    }
    )
    return json.loads(get.json())
def addPayments(values, updater):
    c.execute("SELECT columns_table FROM date_payment_check")
    columns = c.fetchone()[0]
    db.commit()
    c.execute(f"UPDATE date_payment_check SET columns_table = '{columns + 1}'")
    db.commit()
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"A{columns}:D{columns}",
                 "majorDimension": "ROWS",
                 "values": values
                 }
            ]
        }
    ).execute()
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"A12:D12",
                 "majorDimension": "ROWS",
                 "values": [[f"Обновил {updater} в {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"]]
                 }
            ]
        }
    ).execute()




def sendMessageChat(chat_id, message, keyboard=None):
    if keyboard == None:
        response = vk_session.method('messages.send', {"chat_id": chat_id, "message": message, "random_id": 0})
    else:
        response = vk_session.method('messages.send', {"chat_id": chat_id, "message": message, "keyboard": keyboard, "random_id": 0})
    return response


def getFullName(user_id):
    response = vk_session.method("users.get", {"user_ids": user_id, "fields": "screen_name,last_name"})
    answer = {"first_name": response[0]['first_name'],
            "last_name": response[0]["last_name"],
            "domen": response[0]["screen_name"]
            }
    answer = json.dumps(answer, ensure_ascii=False)
    answer = json.loads(answer)
    return answer

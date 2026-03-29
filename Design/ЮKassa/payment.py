import uuid
import json
from yookassa import Configuration, Payment


Configuration.account_id = 439664
Configuration.secret_key = 'live_3SkRY2FUqwhfcDTX0JpQ_5-wY9R_KgTr961qKgo9QJE'


def createpay(money, about):
    payment = Payment.create({
        "amount": {
            "value": f"{money}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://vk.com/morozov_dsgn"
        },
        "receipt": {
            "customer": {
                "email": "kassa@morozov-ilezzov.ru"
            },
            "items": [
                {
                    "description": f"{about}",
                    "quantity": "1",
                    "amount": {
                        "value": f"{money}",
                        "currency": "RUB"
                    },
                    "vat_code": "1"
                }]},
        "capture": True,
        "description": f"{about}"
    }, uuid.uuid4())
    form = json.loads(payment.json())
    answer = {
        "id": form['id'],
        "status": form['status'],
        "link": form['confirmation']['confirmation_url']
    }
    answer = json.dumps(answer, ensure_ascii=False)
    answer = json.loads(answer)
    return answer


def checkstatus(id):
    find = json.loads(Payment.find_one(id).json())
    status = find['status']
    if status == 'succeeded':
        return True
    else:
        return False

def getMoney(id):
    payment = json.loads(Payment.find_one(id).json())
    return payment["income_amount"]["value"]

def getInfo(id):
    payment = json.loads(Payment.find_one(id).json())
    return payment



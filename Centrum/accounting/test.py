import hashlib
import json

import requests

api_id = '9A4F0DB84FB651450C'
project_id = '14679'
pay_id = 104
amount = 1000
currency = 'RUB'
desc = 'Testf'
method = 'advcash'
email = 'r@mail.ru'
api_key = ''

sign = hashlib.sha256(f'create-payment{api_id}{project_id}{pay_id}{amount}{currency}{desc}{method}{api_key}'.encode())

response = requests.get(f'https://anypay.io/api/create-payment/{api_id}',
                        params={'project_id': project_id,
                                'pay_id': pay_id,
                                'amount': amount,
                                'currency': currency,
                                'desc': desc,
                                'method': method,
                                'email': email,
                                'sign': sign.hexdigest()})

print(response.url)

response_json = json.loads(response.text)
print(response_json)
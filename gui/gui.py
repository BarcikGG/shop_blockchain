import requests
from flask import Flask, jsonify, render_template, request
import time
import json

app = Flask(__name__)

BASE_URL = 'http://localhost:'
ASSETID = 'C6FrUQWhBWiBHTvwytSDQjUoMZtm22pTWZjarfzChkyi'
CONTRACTID = 'AKdJi5iNT1Ztp9ik2er77hJC1mD458CCFowShA6ZHK9S'
VERSION = 1

ports = {"3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp": "6862", 
         "3NoXmP2bv4xVajPGPZdzkKXy37dyUro7g7V": "6872",
         "3NforeFPihoReVSCc18kriTbwdUamFbifLn": "6892"}

SandB = '/transactions/signAndBroadcast/'
Status = 'http://localhost:6862/contracts/status/'
GetByKey = 'http://localhost:6862/contracts/'
Balance = 'http://localhost:6862/assets/balance/'
BalanceOfContract = f'http://localhost:6862/contracts/asset-balance/{CONTRACTID}/{ASSETID}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('reg.html')

@app.route('/profile')
def about():
    return render_template('profile.html')

@app.route('/confirm_user', methods=['POST'])
def confirm_user():
    data = request.json
    acc_type = data['acc_type']
    acc_add = data['acc_add']
    result = confirmUser(acc_type, acc_add)
    return jsonify(result)

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    acc_type = data['acc_type']
    name = data['name']
    description = data['description']
    adr = data['adr']
    password = data['password']
    region = data['region']
    phone = data['phone']
    fio = data['fio']

    result = registerUser(acc_type, adr, password, name, description, region, phone, fio)

    return jsonify(result)

@app.route('/contract_balance', methods=['GET'])
def contract_balance():
    result = getContractBalance()
    return result

@app.route('/get_waitlist', methods=['GET'])
def get_waitlist():
    waitlist_dict = printList("waitList")
    
    keys = list(waitlist_dict.keys())
    fio = list()

    for value in waitlist_dict.values():
        fio.append(json.loads(value)['fio'])
    
    return jsonify({'keys': keys, 'names': fio})

def getContractBalance():
    response = requests.get(BalanceOfContract)
    return response.json()['balance']

def checkStatus(transaction_id):
    print(transaction_id)
    time.sleep(5)
    iteration = 0
    response = requests.get(Status+transaction_id)

    while True:
        iteration+= 1
        if isinstance(response.json(), list) and 'status' in response.json()[-1]:
            if response.json()[-1]['status'] == 'Success':
                return response.json()[-1]['status']
            elif response.json()[-1]['status'] == 'Error':
                return response.json()[-1]['message']
        time.sleep(2)
        response = requests.get(Status+transaction_id)
        if iteration == 5:
            break

    return 'cant send request'


def confirmUser(acc_type, acc_add):
    tx = {
    "contractId": CONTRACTID,
    "fee": 0,
    "sender": "3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp",
    "password": "DC3_0U7cCGhGQstieg8kHg",
    "type": 104,
    "params":
    [
        {
           "type": "string",
           "key": "action",
           "value": "accept_register"
        },
        {
           "type": "string",
           "key": "type",
           "value": acc_type
        },
        {
           "type": "string",
           "key": "account",
           "value": acc_add
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
    response = requests.post(BASE_URL+ports["3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def createProduct(title, desc, price, region):
    tx = {
    "contractId": CONTRACTID,
    "fee": 0,
    "sender": "3NoXmP2bv4xVajPGPZdzkKXy37dyUro7g7V",
    "password": "TSFu-6QrpWsIIApnDJdmXg",
    "type": 104,
    "params":
    [
        {
           "type": "string",
           "key": "action",
           "value": "create_product"
        },
        {
           "type": "string",
           "key": "title",
           "value": title
        },
        {
           "type": "string",
           "key": "description",
           "value": desc
        },
        {
           "type": "string",
           "key": "regions",
           "value": region
        },
        {
           "type": "integer",
           "key": "price",
           "value": price
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
    response = requests.post(BASE_URL+ports["3NoXmP2bv4xVajPGPZdzkKXy37dyUro7g7V"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def printList(list_name):
    response = requests.get(GetByKey+CONTRACTID+'/'+list_name)
    try:
        return json.loads(response.json()['value'])
    except: 
        return response.json()['value']
    
def confirmProduct(prod_id, title, min, max, sellers):
    tx = {
    "contractId": CONTRACTID,
    "fee": 0,
    "sender": "3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp",
    "password": "DC3_0U7cCGhGQstieg8kHg",
    "type": 104,
    "params":
    [
        {
           "type": "string",
           "key": "action",
           "value": "accept_product"
        },
        {
           "type": "integer",
           "key": "max",
           "value": max
        },
        {
           "type": "integer",
           "key": "min",
           "value": min
        },
        {
           "type": "string",
           "key": "title",
           "value": title
        },
        {
         "type": "string",
           "key": "id",
           "value": prod_id
        },
        {
           "type": "string",
           "key": "sellers",
           "value": sellers
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
    response = requests.post(BASE_URL+ports["3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def registerUser(type, adr, password, name, description, region, phone, fio):
    tx = {
    "contractId": CONTRACTID,
    "fee": 0,
    "sender": adr,
    "password": password,
    "type": 104,
    "params":
    [
        {
           "type": "string",
           "key": "action",
           "value": "register"
        },
        {
           "type": "string",
           "key": "type",
           "value": type
        },
        {
           "type": "string",
           "key": "name",
           "value": name
        },
        {
           "type": "string",
           "key": "description",
           "value": description
        },
        {
           "type": "string",
           "key": "region",
           "value": region
        },
        {
           "type": "string",
           "key": "phone",
           "value": phone

        },
        {
           "type": "string",
           "key": "fio",
           "value": fio

        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def getProductPrice(prod_id):
    return json.loads(printList("products")[prod_id])["price"]

def buyProduct(prod_id, amount):
    money = getProductPrice(prod_id=prod_id) * amount

    tx = {
    "contractId": CONTRACTID,
    "fee": 0,
    "sender": "3NforeFPihoReVSCc18kriTbwdUamFbifLn",
    "password": "777",
    "type": 104,
    "params":
    [
        {
           "type": "string",
           "key": "action",
           "value": "buy"
        },
        {
           "type": "integer",
           "key": "amount",
           "value": amount
        },
        {
           "type": "string",
           "key": "id",
           "value": prod_id
        }
    ],
    "payments": [
      {
        "assetId": ASSETID,
        "amount": money
      }
    ],
    "version": 5,
    "contractVersion": VERSION
    }
    response = requests.post(BASE_URL+ports["3NforeFPihoReVSCc18kriTbwdUamFbifLn"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

# print(confirmUser('dist', '3NtW4TTNN8Cvq9WkSHGgrRHfA314vuzrY5z'))
# print(createProduct("tea", "best price", 100, "Moscow"))
# print(printOrders("productWait"))
# confirmProduct("74169", "tea", 2, 200, "3NtW4TTNN8Cvq9WkSHGgrRHfA314vuzrY5z")

# getProductPrice("74169")

# registerUser("3NforeFPihoReVSCc18kriTbwdUamFbifLn", "777", "Moscow", "839849303", "SPS")
# confirmUser("client", "3NforeFPihoReVSCc18kriTbwdUamFbifLn")
# buyProduct("74169", 5)

if __name__ == '__main__':
    app.run(debug=True)
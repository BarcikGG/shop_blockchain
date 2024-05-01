import requests
from transactions.tx import *
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
    tx = confirm_account_tx(acc_type, acc_add)
    response = requests.post(BASE_URL+ports["3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def createProduct(adr, password, title, desc, price, region):
    tx = create_product_tx(adr, password, title, desc, region, price)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
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
    tx = confirm_product_tx(max, min, title, prod_id, sellers)
    response = requests.post(BASE_URL+ports["3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp"]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def registerUser(type, adr, password, name, description, region, phone, fio):
    tx = register_user_tx(adr, password, type, name, description, region, phone, fio)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    print(response.status_code)
    print('sending...')
    return checkStatus(response.json()['id'])

def getProductPrice(prod_id):
    return json.loads(printList("products")[prod_id])["price"]

def buyProduct(adr, password, prod_id, amount):
    money = getProductPrice(prod_id=prod_id) * amount
    tx = buy_product_tx(adr, password, amount, prod_id, money)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
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
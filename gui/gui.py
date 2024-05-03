import requests
from transactions.tx import *
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import time
import json

app = Flask(__name__)
app.secret_key = 'secret_key'

BASE_URL = 'http://localhost:'

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
def profile():
    adr = session.get('adr')
    fio = session.get('fio')
    
    return render_template('profile.html', adr=adr, fio=fio)

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/confirm_user', methods=['POST'])
def confirm_user():
    data = request.json
    acc_type = data['acc_type']
    acc_add = data['acc_add']
    result = confirmUser(acc_type, acc_add)
    return jsonify(result)

@app.route('/confirm_product', methods=['POST'])
def confirm_product():
    data = request.json
    prod = data['prod']
    min = int(data['min'])
    max = int(data['max'])
    seller = data['seller']

    adr = session.get('adr')
    password = session.get('password')

    result = confirmProduct(adr, password, prod, min, max, seller)
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

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.json
    adr = data['adr']
    password = data['password']
    type = data['type']

    session['adr'] = adr
    session['password'] = password
    session['type'] = type

    result = json.loads(printList(type+"s")[adr])["fio"]
    session['fio'] = str(result)

    return jsonify(result)

@app.route('/get_values', methods=['POST'])
def get_values():
    data = request.json
    list_name = data['list']

    list_dict = printList(list_name)
    keys = list(list_dict.keys())
    values = list()

    for value in list_dict.values():
        values.append(value)
    
    return jsonify({'keys': keys, 'values': values})

@app.route('/user_logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    name = data['name']
    description = data['description']
    adr = session.get('adr')
    password = session.get('password')
    region = data['region']
    price = int(data['price'])

    result = createProduct(adr, password, name, description, price, region)
    return jsonify(result)

@app.route('/delete_value', methods=['POST'])
def delete_value():
    data = request.json
    type = data['type']
    value = data['value']
    adr = session.get('adr')
    password = session.get('password')

    result = deleteValue(adr, password, type, value)
    return jsonify(result)

@app.route('/buy_product', methods=['POST'])
def buy_product():
    data = request.json
    adr = session.get('adr')
    password = session.get('password')
    product_id = data['product_id']
    amount = int(data['amount'])
    
    result = buyProduct(adr, password, product_id, amount)
    return jsonify(result)

@app.route('/contract_balance', methods=['GET'])
def contract_balance():
    result = getContractBalance()
    return result

@app.route('/user_balance', methods=['GET'])
def user_balance():
    result = getUserBalance()
    return result

@app.route('/get_waitlist', methods=['GET'])
def get_waitlist():
    waitlist_dict = printList("waitList")
    
    keys = list(waitlist_dict.keys())
    fio = list()

    for value in waitlist_dict.values():
        fio.append(json.loads(value)['fio'])
    
    return jsonify({'keys': keys, 'names': fio})

@app.route('/get_wait_products', methods=['GET'])
def get_waitproducts():
    products_dict = printList("productWait")
    
    keys = list(products_dict.keys())
    titles = list()
    prices = list()

    for value in products_dict.values():
        titles.append(json.loads(value)['title'])
        prices.append(json.loads(value)['price'])
    
    return jsonify({'keys': keys, 'names': titles, 'prices': prices})

@app.route('/get_products', methods=['GET'])
def get_products():
    products_dict = printList("products")
    
    keys = list(products_dict.keys())
    titles = list()
    prices = list()
    min = list()
    max = list()

    for value in products_dict.values():
        titles.append(json.loads(value)['title'])
        prices.append(json.loads(value)['price'])
        min.append(json.loads(value)['min'])
        max.append(json.loads(value)['max'])
    
    return jsonify({'keys': keys, 'names': titles, 'prices': prices, 'min': min, 'max': max})

def getContractBalance():
    response = requests.get(BalanceOfContract)
    return response.json()['balance']

def getUserBalance():
    adr = session.get('adr')
    response = requests.get(Balance + adr + "/" + ASSETID)
    return str(response.json()['balance'])

def checkStatus(transaction_id):
    print(transaction_id)
    time.sleep(5)
    iteration = 0
    response = requests.get(Status+transaction_id)
    print(transaction_id)

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
    return checkStatus(response.json()['id'])

def createProduct(adr, password, title, desc, price, region):
    tx = create_product_tx(adr, password, title, desc, region, price)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    return checkStatus(response.json()['id'])

def printList(list_name):
    response = requests.get(GetByKey+CONTRACTID+'/'+list_name)
    try:
        return json.loads(response.json()['value'])
    except: 
        return response.json()['value']
    
def confirmProduct(adr, password, prod_id, min, max, sellers):
    tx = confirm_product_tx(adr, password, max, min, prod_id, sellers)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    return checkStatus(response.json()['id'])

def registerUser(type, adr, password, name, description, region, phone, fio):
    tx = register_user_tx(adr, password, type, name, description, region, phone, fio)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    return checkStatus(response.json()['id'])

def getProductPrice(prod_id):
    return json.loads(printList("products")[prod_id])["price"]

def buyProduct(adr, password, prod_id, amount):
    money = getProductPrice(prod_id) * amount
    tx = buy_product_tx(adr, password, amount, prod_id, money)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    print(response.json())
    return checkStatus(response.json()['id'])

def deleteValue(adr, password, type, value):
    tx = delete_tx(adr, password, type, value)
    response = requests.post(BASE_URL+ports[adr]+SandB, json=tx)
    print(response.json())
    return checkStatus(response.json()['id'])

if __name__ == '__main__':
    app.run(debug=True)
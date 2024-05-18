from flask import Flask, jsonify, redirect, render_template, json, request, session
import time
import requests

from transactions_tx.tx import *


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

BASE_URL = 'http://localhost:'

ports = {"3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp": "6862", 
         "3NoXmP2bv4xVajPGPZdzkKXy37dyUro7g7V": "6872",
         "3NtW4TTNN8Cvq9WkSHGgrRHfA314vuzrY5z": "6882",
         "3NforeFPihoReVSCc18kriTbwdUamFbifLn": "6892"}

SandB = '/transactions/signAndBroadcast/'
Status = 'http://localhost:6862/contracts/status/'
GetByKey = 'http://localhost:6862/contracts/'
Balance = 'http://localhost:6862/assets/balance/'
BalanceOfContract = f'http://localhost:6862/contracts/asset-balance/{CONTRACT_ID}/{ASSET_ID}'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login_page():
    return render_template('login.html')

@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route("/register")
def register_user():
    return render_template('register.html')

@app.route("/user_login", methods=['POST'])
def login_user():
    data = request.json
    adr = data['adr']
    password = data['password']
    result = login(adr, password)
    print(result)
    if result == 'Error: Can\'t find action. Available: register, send mail, send money ...':
        session['adr'] = adr
        session['password'] = password
        return "Success"
    return jsonify(result)

@app.route("/user_reg", methods=['POST'])
def user_reg():
    data = request.json
    adr = data['adr']
    password = data['password']
    fio = data['fio']
    home = data['home']
    result = registration(adr, password, fio, home)
    # print(result)
    return jsonify(result)

def login(adr, password):
    tx = login_tx(adr, password)
    response = requests.post(f'{BASE_URL}{ports[adr]}{SandB}', json=tx)
    if 'error' in response.json():
        return response.json()['message']
    return check_status(response.json()['id'])

def registration(adr, password, fio, home):
    tx = register(adr, password, fio, home)
    response = requests.post(f'{BASE_URL}{ports[adr]}{SandB}', json=tx)
    # print(response.json())
    if 'error' in response.json():
        return response.json()['message']
    return check_status(response.json()['id'])

def check_status(id):
    time.sleep(5)
    iterations = 0
    while True:
        response = requests.get(Status+id)
        if isinstance(response.json(), list) and 'status' in response.json()[-1]:
            if response.json()[-1]['status'] == 'Error': return response.json()[-1]['message']
            return response.json()[-1]['status']
        iterations += 1
        time.sleep(2)
        if iterations == 5:
            break
    return 'cant send request'

if __name__ == '__main__':
    app.run(debug=True, port=8080)
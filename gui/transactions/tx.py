from gui import CONTRACTID, VERSION, ASSETID

def confirm_account_tx(acc_type, acc_add):
    tx = {
        "contractId": CONTRACTID,
        "fee": 0,
        "sender": "3NvCmTJEsJqZy8rseRJXJFaLdqX5XeiEsqp",
        "password": "DC3_0U7cCGhGQstieg8kHg",
        "type": 104,
        "params": [
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
    return tx

def create_product_tx(adr, password, title, desc, region, price):
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
    return tx

def register_user_tx(adr, password, type, name, description, region, phone, fio):
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
    return tx

def buy_product_tx(adr, password, amount, prod_id, money):
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
    return tx

def confirm_product_tx(max, min, title, prod_id, sellers):
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
    return tx



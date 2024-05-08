ASSETID = 'C6FrUQWhBWiBHTvwytSDQjUoMZtm22pTWZjarfzChkyi'
CONTRACTID = 'AKdJi5iNT1Ztp9ik2er77hJC1mD458CCFowShA6ZHK9S'
VERSION = 6

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

def delete_tx(adr, password, type, value):
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
           "value": "delete"
        },
        {
           "type": "string",
           "key": "type",
           "value": type
        },
        {
           "type": "string",
           "key": "key",
           "value": value
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
    return tx

def confirm_product_tx(adr, password, max, min, prod_id, sellers):
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

def send_money_tx(adr, password, to, amount):
   tx = {
   "type": 4,
   "version": 2,
   "sender": adr,
   "password": password,
   "recipient": to,
   "amount": amount,
   "assetId": ASSETID,
   "fee": 0
   }

   return tx

def withdraw_tx(adr, password, id):
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
           "value": "withdraw"
        },
        {
           "type": "string",
           "key": "order_id",
           "value": id
        },
        {
           "type": "string",
           "key": "asset",
           "value": ASSETID
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
   
   return tx

def approve_tx(adr, password, id):
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
           "value": "approve"
        },
        {
           "type": "string",
           "key": "order_id",
           "value": id
        }
    ],
    "version": 2,
    "contractVersion": VERSION
    }
   
   return tx
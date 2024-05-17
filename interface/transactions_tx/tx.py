CONTRACT_ID = '45YSVkQKR9FKHTRg6ij7NANA9TZe6sP4kyRutx2vA1T8'
ASSET_ID = 'CkUnhCezFthA4kkHXiewhQV4CmX6W8C5UwPCc6foSv7B'
VERSION = 1

def register(adr, password, fio, home):
    tx = {
        "contractId": CONTRACT_ID,
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
            "key": "name",
            "value": fio

            },
            {
            "type": "string",
            "key": "home_address",
            "value": home

            }
        ],
        "version": 2,
        "contractVersion": VERSION
    }

    return tx

def login_tx(adr, password):
    tx = {
        "contractId": CONTRACT_ID,
        "fee": 0,
        "sender": adr,
        "password": password,
        "type": 104,
        "params":
        [],
        "version": 2,
        "contractVersion": VERSION
    }

    return tx
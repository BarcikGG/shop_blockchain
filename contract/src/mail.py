import random
import datetime
import grpc
import json
import os
import sys
from google.protobuf.json_format import MessageToJson, MessageToDict
from google.protobuf import descriptor_pool as _descriptor_pool

from protobuf import data_entry_pb2
from protobuf.contract import contract_contract_service_pb2, contract_contract_service_pb2_grpc
from protobuf.contract_asset_operation import contract_transfer_out_pb2
from protobuf import contract_asset_operation_pb2


CreateContractTransactionType = 103
CallContractTransactionType = 104
AUTH_METADATA_KEY = "authorization"

def find_string(params, key):
    for param in params:
        if param.key == key:
            return param.string_value

def find_int(params, key):
    for param in params:
        if param.key == key:
            return param.int_value
        
indexes = {
    344000: "Rostov",
    347900: "Taganrog",
    347901: "Taganrog 1",
    347902: "Taganrog 2",
    347903: "Taganrog 3",
    346780: "Azov",
    346781: "Azov 1",
    346782: "Azov 2",
    346783: "Azov 3",
}

mail_classes = {
    1: {'days': 5, 'price': 0.5},
    2: {'days': 10, 'price': 0.3},
    3: {'days': 15, 'price': 0.1}
}

class ContractHandler:
    def __init__(self, stub, connection_id):
        self.client = stub
        self.connection_id = connection_id
        

        self.users = {}
        self.workers = {}
        self.mails = {}
        self.money_mails = {}
        self.history = {}
        self.days = 0
        self.last_sent = 1
        return

    def start(self, connection_token):
        self.__connect(connection_token)

    def __connect(self, connection_token):
        request = contract_contract_service_pb2.ConnectionRequest(
            connection_id=self.connection_id
        )
        metadata = [(AUTH_METADATA_KEY, connection_token)]
        for contract_transaction_response in self.client.Connect(request=request, metadata=metadata):
            self.__process_connect_response(contract_transaction_response)

    def __process_connect_response(self, contract_transaction_response):
        print("receive: {}".format(contract_transaction_response))
        contract_transaction = contract_transaction_response.transaction
        if contract_transaction.type == CreateContractTransactionType:
            self.__handle_create_transaction(contract_transaction_response)
        elif contract_transaction.type == CallContractTransactionType:
            self.__handle_call_transaction(contract_transaction_response)
        else:
            print("Error: unknown transaction type '{}'".format(contract_transaction.type), file=sys.stderr)

    def __handle_create_transaction(self, contract_transaction_response):
        create_transaction = contract_transaction_response.transaction
        metadata = [(AUTH_METADATA_KEY, contract_transaction_response.auth_token)]

        try:
            self.workers = {}
            self.users = {}

            new_worker2 = Worker({"name": 'Антонов Антон Антонович', "home_address": 'Doroznya 11 kv 17', 
                                "role": 'worker', 'ident': 'RR347900'})
            self.workers["3NoXmP2bv4xVajPGPZdzkKXy37dyUro7g7V"] = new_worker2.objToStr()

            new_admin = User({"name": 'Семенов Семен Семенович',
                    "home_address": 'Pushkina 8 kv 15', "role": 'admin'})
            self.users[create_transaction.sender] = new_admin.objToStr()

            new_client = User({"name": 'Юрьев Юрий Юрьевич',
                            "home_address": 'Doroznya 10 kv 16', "role": 'client'})
            self.users['3NforeFPihoReVSCc18kriTbwdUamFbifLn'] = new_client.objToStr()

            new_worker = Worker({"name": 'Петров Петр Петрович', "home_address": 'Doroznya 20 kv 14', 
                                "role": 'worker', 'ident': 'RR344000'})
            self.workers["3NtW4TTNN8Cvq9WkSHGgrRHfA314vuzrY5z"] = new_worker.objToStr()
        except BaseException as err:
            self.__set_error(str(err))

        data = [
            data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
            data_entry_pb2.DataEntry(key="mails", string_value=json.dumps(self.mails)),
            data_entry_pb2.DataEntry(key="history", string_value=json.dumps(self.history)),
            data_entry_pb2.DataEntry(key="money_mails", string_value=json.dumps(self.money_mails)),
            data_entry_pb2.DataEntry(key="workers", string_value=json.dumps(self.workers)),
            data_entry_pb2.DataEntry(key="days", int_value=create_transaction.timestamp),
            data_entry_pb2.DataEntry(key="last_sent", int_value=1),
            data_entry_pb2.DataEntry(key="owner", string_value=create_transaction.sender)
        ]
        request = contract_contract_service_pb2.ExecutionSuccessRequest(
            tx_id=create_transaction.id, results=data)
        response = self.client.CommitExecutionSuccess(request=request, metadata=metadata)
        print("in create tx response '{}'".format(response))

    def __handle_call_transaction(self, contract_transaction_response):
        self.__call_transaction = contract_transaction_response.transaction
        self.__metadata = [(AUTH_METADATA_KEY, contract_transaction_response.auth_token)]

        try:
            action = find_string(self.__call_transaction.params, "action")
            if action == "register": self.__register()
            elif action == "send mail": self.__send_mail()
            elif action == "send money": self.__send_money()
            elif action == "approve mail": self.__approve_mail()
            elif action == "edit profile": self.__edit_profile()
            elif action == "revoke": self.__revoke()
            elif action == "reject money": self.__reject_money()
            elif action == "receive": self.__receive_money()
            elif action == "reject mail": self.__reject_mail()
            elif action == "edit workers": self.__edit_workers()
            else: self.__set_error("Can't find action. Available: register, send mail, send money ...")
        except BaseException as error:
            self.__set_error(error)
    
    def __register(self):
        try:
            self.users = self.__read_key("users")
            name = find_string(self.__call_transaction.params, "name")
            home_adr = find_string(self.__call_transaction.params, "home_address")
            
            if self.__call_transaction.sender in self.users:
                self.__set_error("User is already registered")
            if name is None: self.__set_error("Name is required")
            if home_adr is None: self.__set_error("Home address is required")

            new_user = User({"name": name, "home_address": home_adr, "role": 'client'})
            self.users[self.__call_transaction.sender] = new_user.objToStr()

            self.__write_data([
                data_entry_pb2.DataEntry(key="users",string_value=json.dumps(self.users))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __edit_workers(self):
        try:
            self.workers = self.__read_key("workers")
            self.users = self.__read_key("users")
            type = find_string(self.__call_transaction.params, "type")
            index = find_int(self.__call_transaction.params, "index")
            adr = find_string(self.__call_transaction.params, "adr")

            sender = json.loads(self.users[self.__call_transaction.sender])
            if type not in ['add', 'delete']: self.__set_error('Wrong type: choose: add, delete, edit')
            if sender['role'] != 'admin': self.__set_error('You are not admin')

            if type == 'add':
                if adr not in self.users: self.__set_error('Cant find this user')
                if adr in self.workers: self.__set_error('Worker is registered')
                user_info = json.loads(self.users[adr])

                new_worker = Worker({"name": user_info['name'], "home_address": user_info['home_address'], 
                             "role": 'worker', 'ident': f'RR{index}'})
                self.workers[adr] = new_worker.objToStr()
            if type == 'edit':
                if adr not in self.workers: self.__set_error('Worker is not registered')
                worker_info = json.loads(self.workers[adr])
                worker_info['ident'] = f'RR{index}'
                self.workers[adr] = json.dumps(worker_info)
            if type == 'delete':
                self.workers.pop(adr)

            self.__write_data([
                data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
                data_entry_pb2.DataEntry(key="workers", string_value=json.dumps(self.workers))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __edit_profile(self):
        try:
            self.users = self.__read_key("users")
            name = find_string(self.__call_transaction.params, "name")
            home_adr = find_string(self.__call_transaction.params, "home_address")
            sender = self.__call_transaction.sender
            
            if sender not in self.users:
                self.__set_error("Cant find user")

            user = json.loads(self.users[sender])

            if name is None: name = user['name']
            if home_adr is None: home_adr = user['home_address']

            user['name'] = name
            user['home_address'] = home_adr

            self.users[sender] = json.dumps(user)

            self.__write_data([
                data_entry_pb2.DataEntry(key="users",string_value=json.dumps(self.users))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __send_mail(self):
        try:
            self.users = self.__read_key("users")
            self.mails = self.__read_key("mails")
            old_last_sent = self.__read_int("last_sent")

            start_time = self.__read_int("days")
            end_time = int(self.__call_transaction.timestamp)

            type = find_string(self.__call_transaction.params, "type")
            mail_class = find_int(self.__call_transaction.params, "class")
            weight = find_string(self.__call_transaction.params, "weight")
            index_from = find_int(self.__call_transaction.params, "from")
            index_to = find_int(self.__call_transaction.params, "to")
            sender = self.__call_transaction.sender
            address_from = json.loads(self.users[sender])['home_address']
            recipient = find_string(self.__call_transaction.params, "recipient")
            cost = find_int(self.__call_transaction.params, "cost")

            if recipient not in self.users: self.__set_error('Cant find recipient!')
            if sender not in self.users: self.__set_error('You must be registered!')
            
            address_to = json.loads(self.users[recipient])['home_address']
            if type is None: self.__set_error('Type is required!')
            if address_from is None or address_to is None: self.__set_error('Addresses is reqired!')
            if type not in ['mail', 'banderol', 'package']: self.__set_error('Wrong type! Choose: mail, banderol, package')
            if mail_class is None: self.__set_error('Mail class is required!')
            if index_from is None or index_to is None: self.__set_error('Indexes is required!')
            if float(weight) > 10 or weight is None: self.__set_error('Wrong weight, max 10kg')

            need_days = mail_classes[mail_class]['days']
            delivery_price = mail_classes[mail_class]['price'] * float(weight)

            if cost is None: cost = 0
            total_price = delivery_price + (cost * 0.1)

            payments = self.__call_transaction.payments
            if len(payments) != 1: self.__set_error('Wrong payments')
            if float(payments[0].amount) < total_price: self.__set_error('Not enough money in payments')

            track_num = generate_number(start_time, end_time, old_last_sent, index_from, index_to)

            mail = Mail({"track_number": track_num, "sender": sender, "recipient": recipient, "type": type, "time": end_time//1000,
                         "weight": weight, "class": mail_class, "date_to": need_days, "delivery_price": delivery_price, 
                         "price_of": cost, "total_cost": total_price, 
                         "address_to": {"index": index_to, "address": address_to}, 
                         "address_from": {"index": index_from, "address": address_from}})

            self.mails[track_num] = mail.objToStr()
            self.__write_data([
                data_entry_pb2.DataEntry(key="mails",string_value=json.dumps(self.mails)),
                data_entry_pb2.DataEntry(key="users",string_value=json.dumps(self.users)),
                data_entry_pb2.DataEntry(key="last_sent",int_value=old_last_sent + 1)
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __reject_mail(self):
        try:
            self.workers = self.__read_key("workers")
            self.mails = self.__read_key("mails")
            self.history = self.__read_key("history")
            sender = self.__call_transaction.sender
            track = find_string(self.__call_transaction.params, "track")
            now_time = int(self.__call_transaction.timestamp)//1000
            
            if track not in self.mails: self.__set_error('Wrong track number')
            if track not in self.history: self.__set_error('Mail didnt sent')
            mail = json.loads(self.mails[track])
            mail_history = json.loads(self.history[track])
            if mail['recipient'] != sender: self.__set_error('Its not your mail')
            if int(mail_history[-1]['worker'])[2:] != mail['address_to']['index'] : self.__set_error('Mail in delivery')
            if now_time <  int(mail['time']) + (int(mail['date_to']) * 24*60*60): self.__set_error('Wait time for delivery')

            self.mails.pop(track)
            self.__write_data([
                data_entry_pb2.DataEntry(key="mails", string_value=json.dumps(self.mails))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __approve_mail(self):
        try:
            self.workers = self.__read_key("workers")
            self.mails = self.__read_key("mails")
            self.history = self.__read_key("history")
            track_num = find_string(self.__call_transaction.params, "track_number")
            weight = find_string(self.__call_transaction.params, "weight")
            worker = self.__call_transaction.sender

            if self.__call_transaction.sender not in self.workers: self.__set_error('You are not a worker!')
            if track_num not in self.mails: self.__set_error('Cant find this mail!')
            mail_info = json.loads(self.mails[track_num])
            worker_info = json.loads(self.workers[worker])
                                     # RR374701
            worker_ident = worker_info['ident']
                                        #374701

            if track_num not in self.history:
                if mail_info['address_from']['index'] != int(worker_ident[2:]): self.__set_error('Mail not in this place')
                
                new_transit = [{"worker": worker_ident, "track": track_num, "weight": weight}] # Error: list indices must be integers or slices, not str
                self.history[track_num] = json.dumps(new_transit)
            else:
                items = json.loads(self.history[track_num])
                last_index = int(items[len(items) - 1]['worker'][2:]) # получили индекс почты которая была последней
                map = create_map(mail_info['address_from']['index'], mail_info['address_to']['index'])

                # тут проверяем что прошлый пункт назначения посылки был верным 
                # и проверяем, что ее следующая точка это наш текущий пункт
                if int(map[len(items) - 1]) == last_index and int(map[len(items)]) == int(worker_ident[2:]):
                    items.append({"worker": worker_ident, "track": track_num, "weight": weight})
                    self.history[track_num] = json.dumps(items)
                else: self.__set_error('Mail to far!')

            self.__write_data([
                data_entry_pb2.DataEntry(key="history", string_value=json.dumps(self.history))
            ])
        except BaseException as error:
            self.__set_error(str(error))
    
    def __send_money(self):
        try:
            old_last_sent = self.__read_int("last_sent")
            self.workers = self.__read_key("workers")
            self.users = self.__read_key("users")
            self.money_mails = self.__read_key("money_mails")
            sender = self.__call_transaction.sender
            send_time = int(self.__call_transaction.timestamp)
            
            recipient = find_string(self.__call_transaction.params, "recipient")
            lifetime = find_int(self.__call_transaction.params, "lifetime")

            if sender not in self.users: self.__set_error('You must be registered!')
            if recipient not in self.users: self.__set_error('Wrong recipient!')
            if lifetime is None or lifetime <= 0: self.__set_error('Lifetime must be int and > 0')

            payments = self.__call_transaction.payments
            if len(payments) != 1: self.__set_error("Wrong payments")

            time = send_time//1000
            new_moneyMail = MoneyMail({"sender": sender, "recipient": recipient, "amount": payments[0].amount, "lifetime": lifetime, "time": time})
            
            self.money_mails[old_last_sent] = new_moneyMail.objToStr()

            self.__write_data([
                data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
                data_entry_pb2.DataEntry(key="money_mails", string_value=json.dumps(self.money_mails)),
                data_entry_pb2.DataEntry(key="last_sent",int_value=old_last_sent + 1)
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __reject_money(self):
        try:
            self.workers = self.__read_key("workers")
            self.users = self.__read_key('users')
            self.money_mails = self.__read_key("money_mails")
            sender = self.__call_transaction.sender
            id = find_string(self.__call_transaction.params, "transact_number")
            
            if sender not in self.users: self.__set_error('You must be registered!')
            if id not in self.money_mails: self.__set_error('Wrong money transaction id')
            money_info = json.loads(self.money_mails[id])

            if sender != money_info['recipient']: self.__set_error('Its not for you!')

            self.money_mails.pop(id)
            self.__write_data([
                data_entry_pb2.DataEntry(key="money_mails", string_value=json.dumps(self.money_mails))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __revoke(self):
        try:
            self.workers = self.__read_key("workers")
            self.users = self.__read_key('users')
            self.money_mails = self.__read_key("money_mails")
            sender = self.__call_transaction.sender
            assetID = find_string(self.__call_transaction.params, "asset")
            id = find_string(self.__call_transaction.params, "transact_number")
            
            if sender not in self.users: self.__set_error('You must be registered!')
            if id not in self.money_mails: self.__set_error('Wrong money transaction id')
            money_info = json.loads(self.money_mails[id])

            if sender != money_info['sender']: self.__set_error('Its not your sent!')

            amount = money_info["amount"]

            transfer = contract_transfer_out_pb2.ContractTransferOut()
            
            transfer.recipient = sender
            transfer.asset_id.value = assetID

            self.money_mails.pop(id)

            transfer.amount = amount
            request = contract_contract_service_pb2.ExecutionSuccessRequest(tx_id = self.__call_transaction.id, 
                                                                            results = [data_entry_pb2.DataEntry(key="ok", string_value="success"),
                                                                                       data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
                                                                                       data_entry_pb2.DataEntry(key="money_mails", string_value=json.dumps(self.money_mails))], 
                                                                            asset_operations=[contract_asset_operation_pb2.ContractAssetOperation(contract_transfer_out = transfer)])

            self.client.CommitExecutionSuccess(request, metadata=self.__metadata)
        except BaseException as error:
            self.__set_error(str(error))
    
    def __receive_money(self):
        try:
            self.workers = self.__read_key("workers")
            self.users = self.__read_key('users')
            self.money_mails = self.__read_key("money_mails")
            sender = self.__call_transaction.sender
            assetID = find_string(self.__call_transaction.params, "asset")
            id = find_string(self.__call_transaction.params, "transact_number")

            now_time = int(self.__call_transaction.timestamp)
            
            if sender not in self.users: self.__set_error('You must be registered!')
            if id not in self.money_mails: self.__set_error('Wrong money transaction id')
            money_info = json.loads(self.money_mails[id])

            if sender != money_info['recipient']: self.__set_error('Its not for you!')

            days = money_info['lifetime']
            sended_time = money_info['time']
            life_to = sended_time + (days * 24 * 60 * 60)

            if life_to < now_time : self.__set_error('Lifetime is end!')

            amount = money_info["amount"]

            transfer = contract_transfer_out_pb2.ContractTransferOut()
            
            transfer.recipient = sender
            transfer.asset_id.value = assetID

            self.money_mails.pop(id)

            transfer.amount = amount
            request = contract_contract_service_pb2.ExecutionSuccessRequest(tx_id = self.__call_transaction.id, 
                                                                            results = [data_entry_pb2.DataEntry(key="ok", string_value="success"),
                                                                                       data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
                                                                                       data_entry_pb2.DataEntry(key="money_mails", string_value=json.dumps(self.money_mails))], 
                                                                            asset_operations=[contract_asset_operation_pb2.ContractAssetOperation(contract_transfer_out = transfer)])

            self.client.CommitExecutionSuccess(request, metadata=self.__metadata)
        except BaseException as error:
            self.__set_error(str(error))
    
    def __read_string(self, key):
        contract_key_request = contract_contract_service_pb2.ContractKeyRequest(
            contract_id=self.__call_transaction.contract_id, 
            key=key)
        contract_key = self.client.GetContractKey(request=contract_key_request, metadata=self.__metadata)
        return contract_key.entry.string_value
    
    def __read_int(self, key):
        contract_key_request = contract_contract_service_pb2.ContractKeyRequest(
            contract_id=self.__call_transaction.contract_id, 
            key=key)
        contract_key = self.client.GetContractKey(request=contract_key_request, metadata=self.__metadata)
        return int(contract_key.entry.int_value)
    
    def __read_key(self, key) -> dict:
        contract_key_request = contract_contract_service_pb2.ContractKeyRequest(
                contract_id=self.__call_transaction.contract_id, 
                key=key)
        contract_key = self.client.GetContractKey(request=contract_key_request, metadata=self.__metadata)
        return json.loads(contract_key.entry.string_value)

    def __set_error(self, message):
        request = contract_contract_service_pb2.ExecutionErrorRequest(
                tx_id=self.__call_transaction.id,
                message=f"Error: {message}",
                code=0
            )
        self.client.CommitExecutionError(request=request, metadata=self.__metadata)

    def __write_data(self, data):
        request = contract_contract_service_pb2.ExecutionSuccessRequest(
            tx_id=self.__call_transaction.id,
            results=data
        )
        self.client.CommitExecutionSuccess(request=request, metadata=self.__metadata)

class User:
    def __init__(self, dictionary) -> None:
        self.name = dictionary["name"]
        self.home_address = dictionary["home_address"]
        self.role = dictionary["role"]
    def objToStr(self): return json.dumps(self.__dict__)

class Worker:
    def __init__(self, dictionary) -> None:
        self.name = dictionary["name"]
        self.home_address = dictionary["home_address"]
        self.role = dictionary["role"]
        self.ident = dictionary["ident"]
    def objToStr(self): return json.dumps(self.__dict__)

class Mail:
    def __init__(self, dictionary) -> None:
        self.track_number = dictionary["track_number"]
        self.sender = dictionary["sender"]
        self.recipient = dictionary["recipient"]
        self.type = dictionary["type"]
        self.weight = dictionary["weight"]
        self.type_of_class = dictionary["class"]
        self.date_to = dictionary["date_to"]
        self.delivery_price = dictionary["delivery_price"]
        self.price_of = dictionary["price_of"]
        self.total_cost = dictionary["total_cost"]
        self.address_to = dictionary["address_to"]
        self.address_from = dictionary["address_from"]
        self.time = dictionary["time"]
    def objToStr(self): return json.dumps(self.__dict__)

class MoneyMail:
    def __init__(self, dictionary) -> None:
        self.sender = dictionary["sender"]
        self.recipient = dictionary["recipient"]
        self.amount = dictionary["amount"]
        self.lifetime = dictionary["lifetime"]
        self.time = dictionary["time"]
    def objToStr(self): return json.dumps(self.__dict__)

class HistoryItem:
    def __init__(self, dictionary) -> None:
        self.info = dictionary["info"]
    def objToStr(self): return json.dumps(self.__dict__)

class Transit:
    def __init__(self, dictionary) -> None:
        self.worker = dictionary["worker"]
        self.track = dictionary["track"]
        self.weight = dictionary["weight"]
    def objToStr(self): return json.dumps(self.__dict__)

def getDate(start_time, end_time):
    dt = datetime.datetime(2024, 5, 17)
    days = (end_time//1000 - start_time//1000) // 5
    dt += datetime.timedelta(days=days)
    return dt.strftime("%d%m%Y")

def generate_number(start_time, end_time, number, index_from, index_to):
    days = getDate(start_time, end_time)
    return str(f"RR{days}{number}{index_from}{index_to}")

def create_map(index_from, index_to):
    from_num_last = str(index_from)[5]
    from_num = str(index_from)[2]
    to_num = str(index_to)[2]
    to_num_last = str(index_to)[5]

    map = [str(index_from)]

    if(from_num == '4'):
        if(to_num == '4'):
            map.append(str(index_to))
        elif(to_num_last == '0'):
            map.append(str(index_to))
        else:
            map.append(str(index_to)[:-1]+ '0')
            map.append(str(index_to))
    else:
        if(from_num_last != '0'):
            map.append(str(index_from)[:-1]+ '0')
        map.append('344000')
        if(to_num != '4'):
            if(to_num_last != '0'):
                map.append(str(index_to)[:-1]+ '0')
            map.append(str(index_to))

    return map

def run(connection_id, node_host, node_port, connection_token):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('{}:{}'.format(node_host, node_port)) as channel:
        stub = contract_contract_service_pb2_grpc.ContractServiceStub(channel)
        handler = ContractHandler(stub, connection_id)
        handler.start(connection_token)

CONNECTION_ID_KEY = 'CONNECTION_ID'
CONNECTION_TOKEN_KEY = 'CONNECTION_TOKEN'
NODE_KEY = 'NODE'
NODE_PORT_KEY = 'NODE_PORT'

if __name__ == '__main__':
    if CONNECTION_ID_KEY not in os.environ:
        sys.exit("Connection id is not set")
    if CONNECTION_TOKEN_KEY not in os.environ:
        sys.exit("Connection token is not set")
    if NODE_KEY not in os.environ:
        sys.exit("Node host is not set")
    if NODE_PORT_KEY not in os.environ:
        sys.exit("Node port is not set")

    connection_id = os.environ['CONNECTION_ID']
    connection_token = os.environ['CONNECTION_TOKEN']
    node_host = os.environ['NODE']
    node_port = os.environ['NODE_PORT']

    run(connection_id, node_host, node_port, connection_token)
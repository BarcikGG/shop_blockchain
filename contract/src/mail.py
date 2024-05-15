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
        self.mails = {}
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
        data = [
            data_entry_pb2.DataEntry(key="users", string_value=json.dumps(self.users)),
            data_entry_pb2.DataEntry(key="mails", string_value=json.dumps(self.mails)),
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
            else: self.__set_error("Can't find action. Available: register, create_product, delete, buy, withdraw")
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
            address_from = find_string(self.__call_transaction.params, "address_from")
            address_to = find_string(self.__call_transaction.params, "address_to")
            cost = find_int(self.__call_transaction.params, "cost")
            recipient = find_string(self.__call_transaction.params, "recipient")

            if type is None: self.__set_error('Type is required!')
            if address_from is None or address_to is None: self.__set_error('Addresses is reqired!')
            if type != 'mail' or type != 'banderol' or type != 'package': self.__set_error('Wrong type: Choose: mail, banderol, package')
            if mail_class is None: self.__set_error('Mail class is required!')
            if index_from is None or index_to is None: self.__set_error('Indexes class is required!')
            if recipient is None: self.__set_error('Recipient is required!')
            if float(weight) > 10 or weight is None: self.__set_error('Wrong weight, max 10kg')

            need_days = mail_classes[mail_class]['days']
            delivery_price = mail_classes[mail_class]['price'] * float(weight)

            if cost is None: cost = 0
            total_price = delivery_price + (cost * 0.1)

            track_num = generate_number(start_time, end_time, old_last_sent, index_from, index_to)

            mail = Mail({"track_number": track_num, "sender": sender, "recipient": recipient, "type": type, 
                         "weight": weight, "class": mail_class, "date_to": need_days, "delivery_price": delivery_price, 
                         "price_of": cost, "total_cost": total_price, 
                         "address_to": {"index": index_to, "address": address_to}, 
                         "address_from": {"index": index_from, "address": address_from}})
            
            self.mails[track_num] = mail.objToStr()
            self.__write_data([
                data_entry_pb2.DataEntry(key="mails",string_value=json.dumps(self.mails)),
                data_entry_pb2.DataEntry(key="last_sent",int_value=old_last_sent + 1)
            ])

        except BaseException as error:
            self.__set_error(str(error))

    def __approve(self):
        try:
            self.orders = self.__read_key("orders")
            self.operators = self.__read_key("operators")
            id = find_string(self.__call_transaction.params, "order_id")
            
            if self.__call_transaction.sender not in self.operators:
                self.__set_error("You are not operator!")

            if id not in self.orders: self.__set_error('Cant find this order')

            order_data = json.loads(self.orders[id])
            order_data['status'] = 'approved'

            self.orders[id] = json.dumps(order_data)
            self.__write_data([
                data_entry_pb2.DataEntry(key="orders", string_value=json.dumps(self.orders))
            ])
        except BaseException as error:
                self.__set_error(str(error))
    
    def __withdraw(self):
        try:
            self.orders = self.__read_key("orders")
            id = find_string(self.__call_transaction.params, "order_id")
            assetID = find_string(self.__call_transaction.params, "asset")
            
            if id not in self.orders: self.__set_error('cant find order')

            order_data = json.loads(self.orders[id])
            if self.__call_transaction.sender_public_key != order_data["seller"]:
                self.__set_error("You are not a seller")

            if order_data["status"] != 'approved':
                self.__set_error("Order wasn't approve")

            recipient = self.__call_transaction.sender
            amount = order_data["total_price"]

            transfer = contract_transfer_out_pb2.ContractTransferOut()
            
            transfer.recipient = recipient
            transfer.asset_id.value = assetID

            transfer.amount = amount
            request = contract_contract_service_pb2.ExecutionSuccessRequest(tx_id = self.__call_transaction.id, 
                                                                            results = [data_entry_pb2.DataEntry(key="ok", string_value="success")], 
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
    def objToStr(self): return json.dumps(self.__dict__)

class MoneyMail:
    def __init__(self, dictionary) -> None:
        self.sender = dictionary["sender"]
        self.recipient = dictionary["recipient"]
        self.amount = dictionary["amount"]
        self.lifetime = dictionary["lifetime"]
    def objToStr(self): return json.dumps(self.__dict__)

def getDate(start_time, end_time):
    dt = datetime.datetime(2024, 5, 14)
    days = (end_time - start_time) // 5
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

    map = [index_from]

    if(from_num == '4'):
        if(to_num == '4'):
            map.append(index_to)
        elif(to_num_last == '0'):
            map.append(index_to)
        else:
            map.append(index_to.slice(0, 5)+ '0')
            map.append(index_to)
    else:
        if(from_num_last != '0'):
            map.append(index_from.slice(0, 5)+ '0')
        map.append('344000')
        if(to_num != 4):
            if(to_num_last != 0):
                map.append(index_to.slice(0, 5)+ '0')
            map.append(index_to)

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
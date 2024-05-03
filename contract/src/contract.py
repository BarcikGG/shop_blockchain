import random
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

class ContractHandler:
    def __init__(self, stub, connection_id):
        self.client = stub
        self.connection_id = connection_id
        
        self.products = {}
        self.organizations = {}
        self.orders = {}
        self.waitList = {}
        self.productWait = {}

        self.operators = {}
        self.clients = {}
        self.dists = {}
        self.sellers = {}
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
            data_entry_pb2.DataEntry(key="operators",string_value=json.dumps(self.operators)),
            data_entry_pb2.DataEntry(key="clients",string_value=json.dumps(self.clients)),
            data_entry_pb2.DataEntry(key="dists",string_value=json.dumps(self.dists)),
            data_entry_pb2.DataEntry(key="sellers",string_value=json.dumps(self.sellers)),
            data_entry_pb2.DataEntry(key="waitList",string_value=json.dumps(self.waitList)),
            data_entry_pb2.DataEntry(key="productWait",string_value=json.dumps(self.productWait)),
            data_entry_pb2.DataEntry(key="products",string_value=json.dumps(self.products)),
            data_entry_pb2.DataEntry(key="orders",string_value=json.dumps(self.orders)),
            data_entry_pb2.DataEntry(key="organizations",string_value=json.dumps(self.organizations)),
            data_entry_pb2.DataEntry(key="owner",string_value=create_transaction.sender)
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
            elif action == "register_operator": self.__register_operator()
            elif action == "accept_register": self.__confirm_registration()
            elif action == "create_product": self.__create_product()
            elif action == "accept_product": self.__accept_product()
            elif action == "delete": self.__delete()
            elif action == "buy": self.__buy_product()
            elif action == "withdraw": self.__withdraw()
            else: self.__set_error("Can't find action. Available: register, create_product, delete, buy, withdraw")
        except BaseException as error:
            self.__set_error(error)

    def __delete(self):
        try:
            self.waitList = self.__read_key("waitList")
            self.organizations = self.__read_key("organizations")
            self.productWait = self.__read_key("productWait")
            self.products = self.__read_key("products")
            self.operators = self.__read_key("operators")
            self.clients = self.__read_key("clients")
            self.sellers = self.__read_key("sellers")
            self.dists = self.__read_key("dists")

            account_key = find_string(self.__call_transaction.params, "key")
            type = find_string(self.__call_transaction.params, "type")
            
            if self.__call_transaction.sender not in self.operators:
                self.__set_error("You are not operator!")
            if account_key is None: self.__set_error("Key is required")

            if type == "dist":
                self.dists.pop(account_key)
            elif type == "seller":
                self.sellers.pop(account_key)
            elif type == "client":
                self.clients.pop(account_key)
            elif type == "waitList":
                self.waitList.pop(account_key)
            elif type == "productWait":
                self.productWait.pop(account_key)
            elif type == "products":
                self.products.pop(account_key)
            elif type == "organizations":
                self.organizations.pop(account_key)
            else:
                self.__set_error("Wrong type")
            
            self.__write_data([
                data_entry_pb2.DataEntry(key="dists", string_value=json.dumps(self.dists)),
                data_entry_pb2.DataEntry(key="sellers", string_value=json.dumps(self.sellers)),
                data_entry_pb2.DataEntry(key="clients", string_value=json.dumps(self.clients)),
                data_entry_pb2.DataEntry(key="waitList", string_value=json.dumps(self.waitList)),
                data_entry_pb2.DataEntry(key="productWait", string_value=json.dumps(self.productWait)),
                data_entry_pb2.DataEntry(key="products", string_value=json.dumps(self.products)),
                data_entry_pb2.DataEntry(key="organizations", string_value=json.dumps(self.organizations))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __confirm_registration(self):
        try:
            self.waitList = self.__read_key("waitList")
            self.operators = self.__read_key("operators")
            self.clients = self.__read_key("clients")
            self.sellers = self.__read_key("sellers")
            self.dists = self.__read_key("dists")
            account_key = find_string(self.__call_transaction.params, "account")
            account_type = find_string(self.__call_transaction.params, "type")
            
            if self.__call_transaction.sender not in self.operators:
                self.__set_error("You are not operator!")
            if account_key is None: self.__set_error("Accepted account is required")
            if account_key not in self.waitList: self.__set_error('Cant find this account')

            if account_type == "dist":
                self.dists[account_key] = self.waitList.pop(account_key)
            elif account_type == "seller":
                self.sellers[account_key] = self.waitList.pop(account_key)
            elif account_type == "client":
                self.clients[account_key] = self.waitList.pop(account_key)
            else:
                self.__set_error("Wrong type. Choose: dist, seller, client")
            
            self.__write_data([
                data_entry_pb2.DataEntry(key="dists", string_value=json.dumps(self.dists)),
                data_entry_pb2.DataEntry(key="sellers", string_value=json.dumps(self.sellers)),
                data_entry_pb2.DataEntry(key="clients", string_value=json.dumps(self.clients)),
                data_entry_pb2.DataEntry(key="waitList", string_value=json.dumps(self.waitList))
            ])
        except BaseException as error:
            self.__set_error(str(error))
    
    def __register(self):
        try:
            self.waitList = self.__read_key("waitList")
            self.organizations = self.__read_key("organizations")
            type = find_string(self.__call_transaction.params, "type")
            name = find_string(self.__call_transaction.params, "name")
            description = find_string(self.__call_transaction.params, "description")
            region = find_string(self.__call_transaction.params, "region")
            pbk = self.__call_transaction.sender_public_key
            phone = find_string(self.__call_transaction.params, "phone")
            fio = find_string(self.__call_transaction.params, "fio")
            
            if self.__call_transaction.sender in self.waitList:
                self.__set_error("User is already in wait list")
            
            if type is None: self.__set_error("Type is required: dist, seller, client")
            if region is None: self.__set_error("Region is required")

            if type == "dist":
                if name is None: self.__set_error("Organization name is required")
                user = Dist({"organization_name": name, "region": 
                            region, "phone": phone, "fio": fio, "public_key": pbk})
                self.__push_waitList(user, self.__call_transaction.sender)
                self.__reg_organization(organization_name=name, pbk=pbk, type=type)
            elif type == "client":
                user = Client({"region": 
                            region, "phone": phone, "fio": fio, "public_key": pbk})
                self.__push_waitList(user, self.__call_transaction.sender)
            elif type == "seller":
                if name is None: self.__set_error("Seller name is required")
                if description is None: self.__set_error("Description name is required")
                user = Seller({"seller_name": name, "description": description, "region": 
                            region, "phone": phone, "fio": fio, "public_key": pbk})
                self.__push_waitList(user, self.__call_transaction.sender)
                self.__reg_organization(organization_name=name, pbk=pbk, type=type)
            else: self.__set_error('Wrong type, select: dist, seller, client')

            self.__write_data([
                data_entry_pb2.DataEntry(key="waitList",string_value=json.dumps(self.waitList)),
                data_entry_pb2.DataEntry(key="organizations", string_value=json.dumps(self.organizations))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __read_string(self, key):
        contract_key_request = contract_contract_service_pb2.ContractKeyRequest(
            contract_id=self.__call_transaction.contract_id, key=key)
        contract_key = self.client.GetContractKey(request=contract_key_request, metadata=self.__metadata)
        return contract_key.entry.string_value

    def __register_operator(self):
        try:
            self.operators = self.__read_key("operators")
            
            owner = self.__read_string("owner")
            pbk = self.__call_transaction.sender_public_key
            phone = find_string(self.__call_transaction.params, "phone")
            fio = find_string(self.__call_transaction.params, "fio")
            
            if self.__call_transaction.sender != owner:
                self.__set_error("Only owner can register operator")

            if self.__call_transaction.sender in self.operators:
                self.__set_error("User already registered")
            
            if phone is None: self.__set_error("Phone is required")
            if fio is None: self.__set_error("FIO is required")

            user = Operator({"phone": phone, "fio": fio, "public_key": pbk})
        
            self.operators[self.__call_transaction.sender] = user.objToStr()
            self.__write_data([
                data_entry_pb2.DataEntry(key="operators",string_value=json.dumps(self.operators))
            ])
        except BaseException as error:
            self.__set_error(str(error))

    def __reg_organization(self, organization_name, pbk, type):
        self.organizations = self.__read_key("organizations")

        if organization_name not in self.organizations:
            new_organization = Organization({"name": organization_name, "type": type, "workers": [pbk]})
            self.__push_organizations(new_organization, organization_name)
        else:
            for org_name, org_data in self.organizations.items():
                if org_name == organization_name:
                    org_info = json.loads(org_data)
                    if pbk not in org_info["workers"]:
                        org_info["workers"].append(pbk)
                        self.organizations[org_name] = json.dumps(org_info)
                    else:
                        self.__set_error("Worker already exists in organization")
                    break
    
    def __create_product(self):
        try:
            id_generator = IDGenerator()
            self.productWait = self.__read_key("productWait")
            self.organizations = self.__read_key("organizations")
            self.sellers = self.__read_key("sellers")
        
            title = find_string(self.__call_transaction.params, "title")
            description = find_string(self.__call_transaction.params, "description")
            regions = find_string(self.__call_transaction.params, "regions")
            pk = self.__call_transaction.sender_public_key
            price = find_int(self.__call_transaction.params, "price")

            if title is None:
                self.__set_error("Name can't be empty")
            if price is None:
                self.__set_error("price key can't be empty")
            
            worker_found = False

            if self.__call_transaction.sender not in self.sellers:
                self.__set_error("You are not a seller")
            
            for org_name, org_data_json in self.organizations.items():
                org_data = json.loads(org_data_json)
                if "workers" in org_data and pk in org_data["workers"]:
                    worker_found = True
                    break

            if not worker_found:
                self.__set_error("Can't find worker for this pk")

            product_id = id_generator.generate_id()
            product = ProductWait({"title": title, "description": description, 
                                "regions": [regions], "added": pk, "price": price})
            self.__push_productWait(product, product_id)
            self.__write_data([data_entry_pb2.DataEntry(key="productWait", string_value=json.dumps(self.productWait))])
        except BaseException as error:
                self.__set_error(str(error))

    def __approve(self):
        try:
            self.orders = self.__read_key("orders")
            id = find_string(self.__call_transaction.params, "order_id")
            
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

    def __buy_product(self):
        try:
            sender = self.__call_transaction.sender
            self.products = self.__read_key("products")
            self.orders = self.__read_key("orders")
            self.clients = self.__read_key("clients")
            amount = find_int(self.__call_transaction.params, "amount")
            id = find_string(self.__call_transaction.params, "id")
            
            generator = IDGenerator()
            order_id = generator.generate_id()
            
            client_data = json.loads(self.clients[sender])
            region = client_data["region"]
            
            if amount is None:
                self.__set_error("Amount can't be empty")

            if id not in self.products:
                self.__set_error("Can't find product with this id")

            prod_data = json.loads(self.products[id])
            if  region not in prod_data["regions"]:
                self.__set_error("You can't buy this product in this region")
            if amount > prod_data["max"]:
                self.__set_error("You can't buy this amount (need less)")
            if amount < prod_data["min"]:
                self.__set_error("You can't buy this amount (need more)")
            
            total = prod_data["price"] * amount
            seller = prod_data["added"]
            
            payments = self.__call_transaction.payments
            if len(payments) != 1:
                self.__set_error("Wrong payments") 

            payments_amount = payments[0].amount
            if payments_amount >= total:
                order = Order({"client": sender, "product": id, 
                               "total_price": total, "status": 'created', "seller": seller})
                
                prod_data["max"] = prod_data["max"] - amount

                self.orders[order_id] = order.objToStr()
                self.products[id] = json.dumps(prod_data)
                self.__write_data([
                    data_entry_pb2.DataEntry(key="orders", string_value=json.dumps(self.orders)),
                    data_entry_pb2.DataEntry(key="products", string_value=json.dumps(self.products))
                ])
            else: self.__set_error("Not enough money")
        except BaseException as error:
            self.__set_error(str(error))
    
    def __accept_product(self):
        try:
            self.productWait = self.__read_key("productWait")
            self.products = self.__read_key("products")
            self.operators = self.__read_key("operators")
            
            max = find_int(self.__call_transaction.params, "max")
            min = find_int(self.__call_transaction.params, "min")
            sellers = find_string(self.__call_transaction.params, "sellers")
            id = find_string(self.__call_transaction.params, "id")

            if self.__call_transaction.sender not in self.operators:
                self.__set_error("You are not operator!")

            if id not in self.productWait:
                self.__set_error("Can't find product with this id")

            if max is None: self.__set_error("Max amount can't be empty")
            if min is None: self.__set_error("Min amount key can't be empty")
            if sellers is None: self.__set_error("Sellers key can't be empty")

            current_product = json.loads(self.productWait[id])

            description = current_product["description"]
            regions = current_product["regions"]
            added = current_product["added"]
            title = current_product["title"]
            price = current_product["price"]

            product = Product({"title": title, "description": description, "regions": regions,
                            "max": max, "min": min, "sellers": [sellers], "added": added, "price": price})
            
            self.productWait.pop(id)
            self.__push_products(product, id)
            self.__write_data([
                data_entry_pb2.DataEntry(key="products",string_value=json.dumps(self.products)),
                data_entry_pb2.DataEntry(key="productWait",string_value=json.dumps(self.productWait))])
        except BaseException as error:
            self.__set_error(str(error))
    
    def __read_key(self, key) -> dict:
        contract_key_request = contract_contract_service_pb2.ContractKeyRequest(
                contract_id=self.__call_transaction.contract_id, key=key)
        contract_key = self.client.GetContractKey(request=contract_key_request, metadata=self.__metadata)
        return json.loads(contract_key.entry.string_value)

    def __set_error(self, message):
        request = contract_contract_service_pb2.ExecutionErrorRequest(
                tx_id=self.__call_transaction.id,
                message=f"Error: {message}",
                code=0
            )
        self.client.CommitExecutionError(request=request, metadata=self.__metadata)

    def __push_waitList(self, user, account):
        self.waitList[account] = user.objToStr()

    def __push_organizations(self, organization, org_name):
        self.organizations[org_name] = organization.objToStr()

    def __push_products(self, product, id):
        self.products[id] = product.objToStr()

    def __push_productWait(self, product, id):
        self.productWait[id] = product.objToStr()

    def __write_data(self, data):
        request = contract_contract_service_pb2.ExecutionSuccessRequest(
            tx_id=self.__call_transaction.id,
            results=data
        )
        self.client.CommitExecutionSuccess(request=request, metadata=self.__metadata)

class Dist:
    def __init__(self, dictionary) -> None:
        self.organization_name = dictionary["organization_name"]
        self.region = dictionary["region"]
        self.phone = dictionary["phone"]
        self.fio = dictionary["fio"]
        self.public_key = dictionary["public_key"]
    def objToStr(self): return json.dumps(self.__dict__)

class Seller:
    def __init__(self, dictionary) -> None:
        self.seller_name = dictionary["seller_name"]
        self.description = dictionary["description"]
        self.region = dictionary["region"]
        self.phone = dictionary["phone"]
        self.fio = dictionary["fio"]
        self.public_key = dictionary["public_key"]
    def objToStr(self): return json.dumps(self.__dict__)

class Client:
    def __init__(self, dictionary) -> None:
        self.region = dictionary["region"]
        self.phone = dictionary["phone"]
        self.fio = dictionary["fio"]
        self.public_key = dictionary["public_key"]
    def objToStr(self): return json.dumps(self.__dict__)

class Operator:
    def __init__(self, dictionary) -> None:
        self.phone = dictionary["phone"]
        self.fio = dictionary["fio"]
        self.public_key = dictionary["public_key"]
    def objToStr(self): return json.dumps(self.__dict__)

class Order:
    def __init__(self, dictionary) -> None:
        self.client = dictionary["client"]
        self.product = dictionary["product"]
        self.total_price = dictionary["total_price"]
        self.status = dictionary["status"]
        self.seller = dictionary["seller"]
    def objToStr(self): return json.dumps(self.__dict__)

class Organization:
    def __init__(self, dictionary) -> None:
        self.name = dictionary["name"]
        self.type = dictionary["type"]
        self.workers = dictionary["workers"]
    def objToStr(self): return json.dumps(self.__dict__)

class ProductWait:
    def __init__(self, dictionary) -> None:
        self.title = dictionary["title"]
        self.description = dictionary["description"]
        self.regions = dictionary["regions"]
        self.added = dictionary["added"]
        self.price = dictionary["price"]
    def objToStr(self): return json.dumps(self.__dict__)

class Product:
    def __init__(self, dictionary) -> None:
        self.title = dictionary["title"]
        self.description = dictionary["description"]
        self.regions = dictionary["regions"]
        self.max = dictionary["max"]
        self.min = dictionary["min"]
        self.sellers = dictionary["sellers"]
        self.added = dictionary["added"]
        self.price = dictionary["price"]
    def objToStr(self): return json.dumps(self.__dict__)

class IDGenerator:
    def generate_id(self):
        return random.randint(10000, 99999)

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
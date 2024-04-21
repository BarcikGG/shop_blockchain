#!/bin/bash

cd protobuf

# Компиляция файлов contract
python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. contract/contract_contract_service.proto

# cp contract/contract_contract_service.proto ./contract_contract_service.proto
# python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. contract_contract_service.proto

python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. data_entry.proto
python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. contract_transfer_in.proto
python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. contract_asset_operation.proto

cd contract_asset_operation

# Компиляция всех файлов .proto в текущей директории
for file in *.proto; do
    python3 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. "$file"
done
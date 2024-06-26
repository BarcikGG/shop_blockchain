# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: contract_asset_operation.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protobuf.contract_asset_operation import contract_issue_pb2 as contract__asset__operation_dot_contract__issue__pb2
from protobuf.contract_asset_operation import contract_reissue_pb2 as contract__asset__operation_dot_contract__reissue__pb2
from protobuf.contract_asset_operation import contract_burn_pb2 as contract__asset__operation_dot_contract__burn__pb2
from protobuf.contract_asset_operation import contract_transfer_out_pb2 as contract__asset__operation_dot_contract__transfer__out__pb2
from protobuf.contract_asset_operation import contract_lease_pb2 as contract__asset__operation_dot_contract__lease__pb2
from protobuf.contract_asset_operation import contract_cancel_lease_pb2 as contract__asset__operation_dot_contract__cancel__lease__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x63ontract_asset_operation.proto\x12\x0fwavesenterprise\x1a-contract_asset_operation/contract_issue.proto\x1a/contract_asset_operation/contract_reissue.proto\x1a,contract_asset_operation/contract_burn.proto\x1a\x34\x63ontract_asset_operation/contract_transfer_out.proto\x1a-contract_asset_operation/contract_lease.proto\x1a\x34\x63ontract_asset_operation/contract_cancel_lease.proto\"\x9d\x03\n\x16\x43ontractAssetOperation\x12\x38\n\x0e\x63ontract_issue\x18\x01 \x01(\x0b\x32\x1e.wavesenterprise.ContractIssueH\x00\x12<\n\x10\x63ontract_reissue\x18\x02 \x01(\x0b\x32 .wavesenterprise.ContractReissueH\x00\x12\x36\n\rcontract_burn\x18\x03 \x01(\x0b\x32\x1d.wavesenterprise.ContractBurnH\x00\x12\x45\n\x15\x63ontract_transfer_out\x18\x04 \x01(\x0b\x32$.wavesenterprise.ContractTransferOutH\x00\x12\x38\n\x0e\x63ontract_lease\x18\x05 \x01(\x0b\x32\x1e.wavesenterprise.ContractLeaseH\x00\x12\x45\n\x15\x63ontract_cancel_lease\x18\x06 \x01(\x0b\x32$.wavesenterprise.ContractCancelLeaseH\x00\x42\x0b\n\toperation\"Y\n\x1a\x43ontractAssetOperationList\x12;\n\noperations\x18\x01 \x03(\x0b\x32\'.wavesenterprise.ContractAssetOperation\"\xd4\x01\n\x19\x43ontractAssetOperationMap\x12T\n\roperationList\x18\x01 \x03(\x0b\x32=.wavesenterprise.ContractAssetOperationMap.OperationListEntry\x1a\x61\n\x12OperationListEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12:\n\x05value\x18\x02 \x01(\x0b\x32+.wavesenterprise.ContractAssetOperationList:\x02\x38\x01\x42[\n(com.wavesenterprise.transaction.protobufP\x01Z\x1bwavesenterprise.com/weproto\xaa\x02\x0fWavesEnterpriseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'contract_asset_operation_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n(com.wavesenterprise.transaction.protobufP\001Z\033wavesenterprise.com/weproto\252\002\017WavesEnterprise'
  _globals['_CONTRACTASSETOPERATIONMAP_OPERATIONLISTENTRY']._options = None
  _globals['_CONTRACTASSETOPERATIONMAP_OPERATIONLISTENTRY']._serialized_options = b'8\001'
  _globals['_CONTRACTASSETOPERATION']._serialized_start=349
  _globals['_CONTRACTASSETOPERATION']._serialized_end=762
  _globals['_CONTRACTASSETOPERATIONLIST']._serialized_start=764
  _globals['_CONTRACTASSETOPERATIONLIST']._serialized_end=853
  _globals['_CONTRACTASSETOPERATIONMAP']._serialized_start=856
  _globals['_CONTRACTASSETOPERATIONMAP']._serialized_end=1068
  _globals['_CONTRACTASSETOPERATIONMAP_OPERATIONLISTENTRY']._serialized_start=971
  _globals['_CONTRACTASSETOPERATIONMAP_OPERATIONLISTENTRY']._serialized_end=1068
# @@protoc_insertion_point(module_scope)

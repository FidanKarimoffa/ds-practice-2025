# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: transaction_verification.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'transaction_verification.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1etransaction_verification.proto\x12\"bookstore.transaction_verification\"0\n\x0fTransactionUser\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\"L\n\x15TransactionCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x16\n\x0e\x65xpirationDate\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\"1\n\x0fTransactionItem\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"J\n\x19TransactionBillingAddress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x03 \x01(\t\"\xa7\x03\n\tOrderData\x12\x41\n\x04user\x18\x01 \x01(\x0b\x32\x33.bookstore.transaction_verification.TransactionUser\x12M\n\ncreditCard\x18\x02 \x01(\x0b\x32\x39.bookstore.transaction_verification.TransactionCreditCard\x12\x42\n\x05items\x18\x03 \x03(\x0b\x32\x33.bookstore.transaction_verification.TransactionItem\x12U\n\x0e\x62illingAddress\x18\x04 \x01(\x0b\x32=.bookstore.transaction_verification.TransactionBillingAddress\x12V\n\x0fshippingAddress\x18\x05 \x01(\x0b\x32=.bookstore.transaction_verification.TransactionBillingAddress\x12\x15\n\rtermsAccepted\x18\x06 \x01(\x08\"{\n\x11\x43\x61\x63heOrderRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x13\n\x0bvectorClock\x18\x02 \x03(\x05\x12@\n\torderData\x18\x03 \x01(\x0b\x32-.bookstore.transaction_verification.OrderData\"0\n\x12\x43\x61\x63heOrderResponse\x12\x1a\n\x12updatedVectorClock\x18\x01 \x03(\x05\"4\n\x0c\x45ventRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x13\n\x0bvectorClock\x18\x02 \x03(\x05\"\\\n\x1fTransactionVerificationResponse\x12\x14\n\x0cverification\x18\x01 \x01(\x08\x12\x0e\n\x06\x65rrors\x18\x02 \x01(\t\x12\x13\n\x0bvectorClock\x18\x03 \x03(\x05\"\xf1\x02\n\x1eTransactionVerificationRequest\x12\x41\n\x04user\x18\x01 \x01(\x0b\x32\x33.bookstore.transaction_verification.TransactionUser\x12M\n\ncreditCard\x18\x02 \x01(\x0b\x32\x39.bookstore.transaction_verification.TransactionCreditCard\x12\x42\n\x05items\x18\x03 \x03(\x0b\x32\x33.bookstore.transaction_verification.TransactionItem\x12U\n\x0e\x62illingAddress\x18\x04 \x01(\x0b\x32=.bookstore.transaction_verification.TransactionBillingAddress\x12\"\n\x1atermsAndConditionsAccepted\x18\x05 \x01(\x08\x32\xeb\x05\n\x1eTransactionVerificationService\x12{\n\nCacheOrder\x12\x35.bookstore.transaction_verification.CacheOrderRequest\x1a\x36.bookstore.transaction_verification.CacheOrderResponse\x12\x8b\x01\n\x12\x43heckItemsNonEmpty\x12\x30.bookstore.transaction_verification.EventRequest\x1a\x43.bookstore.transaction_verification.TransactionVerificationResponse\x12\x8d\x01\n\x14\x43heckMandatoryFields\x12\x30.bookstore.transaction_verification.EventRequest\x1a\x43.bookstore.transaction_verification.TransactionVerificationResponse\x12\x8e\x01\n\x15\x43heckCreditCardFormat\x12\x30.bookstore.transaction_verification.EventRequest\x1a\x43.bookstore.transaction_verification.TransactionVerificationResponse\x12\x9c\x01\n\x11VerifyTransaction\x12\x42.bookstore.transaction_verification.TransactionVerificationRequest\x1a\x43.bookstore.transaction_verification.TransactionVerificationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'transaction_verification_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TRANSACTIONUSER']._serialized_start=70
  _globals['_TRANSACTIONUSER']._serialized_end=118
  _globals['_TRANSACTIONCREDITCARD']._serialized_start=120
  _globals['_TRANSACTIONCREDITCARD']._serialized_end=196
  _globals['_TRANSACTIONITEM']._serialized_start=198
  _globals['_TRANSACTIONITEM']._serialized_end=247
  _globals['_TRANSACTIONBILLINGADDRESS']._serialized_start=249
  _globals['_TRANSACTIONBILLINGADDRESS']._serialized_end=323
  _globals['_ORDERDATA']._serialized_start=326
  _globals['_ORDERDATA']._serialized_end=749
  _globals['_CACHEORDERREQUEST']._serialized_start=751
  _globals['_CACHEORDERREQUEST']._serialized_end=874
  _globals['_CACHEORDERRESPONSE']._serialized_start=876
  _globals['_CACHEORDERRESPONSE']._serialized_end=924
  _globals['_EVENTREQUEST']._serialized_start=926
  _globals['_EVENTREQUEST']._serialized_end=978
  _globals['_TRANSACTIONVERIFICATIONRESPONSE']._serialized_start=980
  _globals['_TRANSACTIONVERIFICATIONRESPONSE']._serialized_end=1072
  _globals['_TRANSACTIONVERIFICATIONREQUEST']._serialized_start=1075
  _globals['_TRANSACTIONVERIFICATIONREQUEST']._serialized_end=1444
  _globals['_TRANSACTIONVERIFICATIONSERVICE']._serialized_start=1447
  _globals['_TRANSACTIONVERIFICATIONSERVICE']._serialized_end=2194
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: bookstore/order_queue/order_queue.proto
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
    'bookstore/order_queue/order_queue.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'bookstore/order_queue/order_queue.proto\x12\x15\x62ookstore.order_queue\"H\n\nQueueOrder\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x17\n\x0fshippingCountry\x18\x02 \x01(\t\x12\x10\n\x08jsonData\x18\x03 \x01(\t\"B\n\x0e\x45nqueueRequest\x12\x30\n\x05order\x18\x01 \x01(\x0b\x32!.bookstore.order_queue.QueueOrder\"3\n\x0f\x45nqueueResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x10\n\x0e\x44\x65queueRequest\"e\n\x0f\x44\x65queueResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x30\n\x05order\x18\x03 \x01(\x0b\x32!.bookstore.order_queue.QueueOrder2\xc7\x01\n\x11OrderQueueService\x12X\n\x07\x45nqueue\x12%.bookstore.order_queue.EnqueueRequest\x1a&.bookstore.order_queue.EnqueueResponse\x12X\n\x07\x44\x65queue\x12%.bookstore.order_queue.DequeueRequest\x1a&.bookstore.order_queue.DequeueResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'bookstore.order_queue.order_queue_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_QUEUEORDER']._serialized_start=66
  _globals['_QUEUEORDER']._serialized_end=138
  _globals['_ENQUEUEREQUEST']._serialized_start=140
  _globals['_ENQUEUEREQUEST']._serialized_end=206
  _globals['_ENQUEUERESPONSE']._serialized_start=208
  _globals['_ENQUEUERESPONSE']._serialized_end=259
  _globals['_DEQUEUEREQUEST']._serialized_start=261
  _globals['_DEQUEUEREQUEST']._serialized_end=277
  _globals['_DEQUEUERESPONSE']._serialized_start=279
  _globals['_DEQUEUERESPONSE']._serialized_end=380
  _globals['_ORDERQUEUESERVICE']._serialized_start=383
  _globals['_ORDERQUEUESERVICE']._serialized_end=582
# @@protoc_insertion_point(module_scope)

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import transaction_verification_pb2 as transaction__verification__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in transaction_verification_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactionVerificationServiceStub(object):
    """-------- SERVICE --------

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CacheOrder = channel.unary_unary(
                '/bookstore.transaction_verification.TransactionVerificationService/CacheOrder',
                request_serializer=transaction__verification__pb2.CacheOrderRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.CacheOrderResponse.FromString,
                _registered_method=True)
        self.CheckItemsNonEmpty = channel.unary_unary(
                '/bookstore.transaction_verification.TransactionVerificationService/CheckItemsNonEmpty',
                request_serializer=transaction__verification__pb2.EventRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.TransactionVerificationResponse.FromString,
                _registered_method=True)
        self.CheckMandatoryFields = channel.unary_unary(
                '/bookstore.transaction_verification.TransactionVerificationService/CheckMandatoryFields',
                request_serializer=transaction__verification__pb2.EventRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.TransactionVerificationResponse.FromString,
                _registered_method=True)
        self.CheckCreditCardFormat = channel.unary_unary(
                '/bookstore.transaction_verification.TransactionVerificationService/CheckCreditCardFormat',
                request_serializer=transaction__verification__pb2.EventRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.TransactionVerificationResponse.FromString,
                _registered_method=True)
        self.VerifyTransaction = channel.unary_unary(
                '/bookstore.transaction_verification.TransactionVerificationService/VerifyTransaction',
                request_serializer=transaction__verification__pb2.TransactionVerificationRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.TransactionVerificationResponse.FromString,
                _registered_method=True)


class TransactionVerificationServiceServicer(object):
    """-------- SERVICE --------

    """

    def CacheOrder(self, request, context):
        """new caching call
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckItemsNonEmpty(self, request, context):
        """(a) check items
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckMandatoryFields(self, request, context):
        """(b) check mandatory fields
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckCreditCardFormat(self, request, context):
        """(c) credit card format
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VerifyTransaction(self, request, context):
        """optional older single-shot method
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionVerificationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CacheOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CacheOrder,
                    request_deserializer=transaction__verification__pb2.CacheOrderRequest.FromString,
                    response_serializer=transaction__verification__pb2.CacheOrderResponse.SerializeToString,
            ),
            'CheckItemsNonEmpty': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckItemsNonEmpty,
                    request_deserializer=transaction__verification__pb2.EventRequest.FromString,
                    response_serializer=transaction__verification__pb2.TransactionVerificationResponse.SerializeToString,
            ),
            'CheckMandatoryFields': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckMandatoryFields,
                    request_deserializer=transaction__verification__pb2.EventRequest.FromString,
                    response_serializer=transaction__verification__pb2.TransactionVerificationResponse.SerializeToString,
            ),
            'CheckCreditCardFormat': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckCreditCardFormat,
                    request_deserializer=transaction__verification__pb2.EventRequest.FromString,
                    response_serializer=transaction__verification__pb2.TransactionVerificationResponse.SerializeToString,
            ),
            'VerifyTransaction': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyTransaction,
                    request_deserializer=transaction__verification__pb2.TransactionVerificationRequest.FromString,
                    response_serializer=transaction__verification__pb2.TransactionVerificationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'bookstore.transaction_verification.TransactionVerificationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('bookstore.transaction_verification.TransactionVerificationService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactionVerificationService(object):
    """-------- SERVICE --------

    """

    @staticmethod
    def CacheOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/bookstore.transaction_verification.TransactionVerificationService/CacheOrder',
            transaction__verification__pb2.CacheOrderRequest.SerializeToString,
            transaction__verification__pb2.CacheOrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CheckItemsNonEmpty(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/bookstore.transaction_verification.TransactionVerificationService/CheckItemsNonEmpty',
            transaction__verification__pb2.EventRequest.SerializeToString,
            transaction__verification__pb2.TransactionVerificationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CheckMandatoryFields(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/bookstore.transaction_verification.TransactionVerificationService/CheckMandatoryFields',
            transaction__verification__pb2.EventRequest.SerializeToString,
            transaction__verification__pb2.TransactionVerificationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CheckCreditCardFormat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/bookstore.transaction_verification.TransactionVerificationService/CheckCreditCardFormat',
            transaction__verification__pb2.EventRequest.SerializeToString,
            transaction__verification__pb2.TransactionVerificationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def VerifyTransaction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/bookstore.transaction_verification.TransactionVerificationService/VerifyTransaction',
            transaction__verification__pb2.TransactionVerificationRequest.SerializeToString,
            transaction__verification__pb2.TransactionVerificationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

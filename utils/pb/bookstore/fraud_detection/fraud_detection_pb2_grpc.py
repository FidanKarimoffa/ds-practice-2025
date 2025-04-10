# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import fraud_detection_pb2 as fraud__detection__pb2

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
        + f' but the generated code in fraud_detection_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class FraudDetectionServiceStub(object):
    """-------- SERVICE --------

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CacheOrder = channel.unary_unary(
                '/bookstore.fraud_detection.FraudDetectionService/CacheOrder',
                request_serializer=fraud__detection__pb2.CacheOrderRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.CacheOrderResponse.FromString,
                _registered_method=True)
        self.CheckUserDataFraud = channel.unary_unary(
                '/bookstore.fraud_detection.FraudDetectionService/CheckUserDataFraud',
                request_serializer=fraud__detection__pb2.EventRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.FraudDetectionResponse.FromString,
                _registered_method=True)
        self.CheckCreditCardFraud = channel.unary_unary(
                '/bookstore.fraud_detection.FraudDetectionService/CheckCreditCardFraud',
                request_serializer=fraud__detection__pb2.EventRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.FraudDetectionResponse.FromString,
                _registered_method=True)
        self.DetectUserFraud = channel.unary_unary(
                '/bookstore.fraud_detection.FraudDetectionService/DetectUserFraud',
                request_serializer=fraud__detection__pb2.OrderInfo.SerializeToString,
                response_deserializer=fraud__detection__pb2.FraudDetectionResponse.FromString,
                _registered_method=True)


class FraudDetectionServiceServicer(object):
    """-------- SERVICE --------

    """

    def CacheOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckUserDataFraud(self, request, context):
        """(d) user data check
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckCreditCardFraud(self, request, context):
        """(e) advanced cc fraud check
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DetectUserFraud(self, request, context):
        """single-shot older approach
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FraudDetectionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CacheOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CacheOrder,
                    request_deserializer=fraud__detection__pb2.CacheOrderRequest.FromString,
                    response_serializer=fraud__detection__pb2.CacheOrderResponse.SerializeToString,
            ),
            'CheckUserDataFraud': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckUserDataFraud,
                    request_deserializer=fraud__detection__pb2.EventRequest.FromString,
                    response_serializer=fraud__detection__pb2.FraudDetectionResponse.SerializeToString,
            ),
            'CheckCreditCardFraud': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckCreditCardFraud,
                    request_deserializer=fraud__detection__pb2.EventRequest.FromString,
                    response_serializer=fraud__detection__pb2.FraudDetectionResponse.SerializeToString,
            ),
            'DetectUserFraud': grpc.unary_unary_rpc_method_handler(
                    servicer.DetectUserFraud,
                    request_deserializer=fraud__detection__pb2.OrderInfo.FromString,
                    response_serializer=fraud__detection__pb2.FraudDetectionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'bookstore.fraud_detection.FraudDetectionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('bookstore.fraud_detection.FraudDetectionService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class FraudDetectionService(object):
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
            '/bookstore.fraud_detection.FraudDetectionService/CacheOrder',
            fraud__detection__pb2.CacheOrderRequest.SerializeToString,
            fraud__detection__pb2.CacheOrderResponse.FromString,
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
    def CheckUserDataFraud(request,
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
            '/bookstore.fraud_detection.FraudDetectionService/CheckUserDataFraud',
            fraud__detection__pb2.EventRequest.SerializeToString,
            fraud__detection__pb2.FraudDetectionResponse.FromString,
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
    def CheckCreditCardFraud(request,
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
            '/bookstore.fraud_detection.FraudDetectionService/CheckCreditCardFraud',
            fraud__detection__pb2.EventRequest.SerializeToString,
            fraud__detection__pb2.FraudDetectionResponse.FromString,
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
    def DetectUserFraud(request,
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
            '/bookstore.fraud_detection.FraudDetectionService/DetectUserFraud',
            fraud__detection__pb2.OrderInfo.SerializeToString,
            fraud__detection__pb2.FraudDetectionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

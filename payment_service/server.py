import grpc
from concurrent import futures

import payment_pb2
import payment_pb2_grpc

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s"
)
logger = logging.getLogger("PaymentService")


class PaymentService(payment_pb2_grpc.PaymentServiceServicer):
    def __init__(self):
        self.prepared = False

    def Prepare(self, request, context):
        self.prepared = True
        logger.info(f"Prepared for order {request.order_id}")
        return payment_pb2.PrepareResponse(ready=True)

    def Commit(self, request, context):
        if self.prepared:
            logger.info(f"Committed for order {request.order_id}")
            self.prepared = False
            return payment_pb2.CommitResponse(success=True)
        return payment_pb2.CommitResponse(success=False)

    def Abort(self, request, context):
        self.prepared = False
        logger.info(f"Aborted for order {request.order_id}")
        return payment_pb2.AbortResponse(aborted=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    payment_pb2_grpc.add_PaymentServiceServicer_to_server(PaymentService(), server)
    server.add_insecure_port("[::]:50056")
    logger.info("Payment Service started on port 50056")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

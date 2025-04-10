# order_queue/src/app.py

import sys
import os
import heapq  # for priority queue
import threading
import json
from concurrent import futures

import grpc

# Add the path if needed (but in Docker, we do ENV PYTHONPATH=/app/utils/pb)
FILE = __file__ if "__file__" in globals() else os.getenv("PYTHONFILE", "")
sys.path.insert(0, os.path.abspath("/app/utils/pb"))  # optional if Docker sets ENV

# Because .proto => package bookstore.order_queue
from bookstore.order_queue import order_queue_pb2, order_queue_pb2_grpc

def get_country_priority(country: str) -> int:
    """
    Return an integer so that lower => higher priority:
     - 0 => USA
     - 1 => CANADA
     - 2 => MEXICO
     - 3 => anything else
    """
    c = country.upper()
    if c == "USA":
        return 0
    elif c == "CANADA":
        return 1
    elif c == "MEXICO":
        return 2
    else:
        return 3

class OrderQueueService(order_queue_pb2_grpc.OrderQueueServiceServicer):
    """Implements the gRPC service for enqueue/dequeue with a priority queue."""

    def __init__(self):
        self.heap = []
        self.counter = 0
        self.lock = threading.Lock()
        print("[OrderQueue] Service initialized.")

    def Enqueue(self, request, context):
        order = request.order
        prio = get_country_priority(order.shippingCountry)
        with self.lock:
            self.counter += 1
            heapq.heappush(self.heap, (prio, self.counter, order))
        print(f"[OrderQueue] Enqueued OrderID={order.orderId}, shipping={order.shippingCountry}, priority={prio}")
        return order_queue_pb2.EnqueueResponse(
            success=True,
            message=f"Order {order.orderId} enqueued with priority={prio}"
        )

    def Dequeue(self, request, context):
        with self.lock:
            if not self.heap:
                return order_queue_pb2.DequeueResponse(
                    success=False,
                    message="Queue is empty"
                )
            prio, idx, order = heapq.heappop(self.heap)
        print(f"[OrderQueue] Dequeued OrderID={order.orderId}, shipping={order.shippingCountry}, priority={prio}")
        return order_queue_pb2.DequeueResponse(
            success=True,
            message="OK",
            order=order
        )

def serve():
    """Start the gRPC server on port 50054."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_queue_pb2_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)

    port = "50054"
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[OrderQueue] Priority Queue Server started on port {port}.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

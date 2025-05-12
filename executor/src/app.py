import os
import sys
import time
import grpc
from concurrent import futures
import threading
import logging
from utils.pb import books_db_pb2 as db_pb
from utils.pb import books_db_pb2_grpc as db_grpc
from utils.pb.books_db_pb2_grpc import BooksDatabaseStub
sys.path.insert(0, "/app/payment_service")  # ✅ Add this near the top

import payment_pb2
import payment_pb2_grpc



from bookstore.executor import executor_pb2, executor_pb2_grpc
from bookstore.order_queue import order_queue_pb2, order_queue_pb2_grpc


# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

last_heartbeat = None
heartbeat_lock = threading.Lock()
leader_id = None
leader_lock = threading.Lock()

HEARTBEAT_INTERVAL = 5
HEARTBEAT_TIMEOUT = 30

try:
    EXECUTOR_ID = int(os.getenv("EXECUTOR_ID"))
except (TypeError, ValueError):
    print("Error: EXECUTOR_ID environment variable is not set or invalid.")
    sys.exit(1)

peer_ids_env = os.getenv("PEER_IDS", str(EXECUTOR_ID))
PEER_IDS = sorted([int(x.strip()) for x in peer_ids_env.split(",")])
print(f"[Executor {EXECUTOR_ID}] Peers in system: {PEER_IDS}")

DB_PRIMARY = os.getenv("DB_PRIMARY_HOST", "books-db-primary:6000")
db_stub = BooksDatabaseStub(grpc.insecure_channel(DB_PRIMARY))

def send_heartbeat():
    global last_heartbeat
    while True:
        if is_leader():
            with heartbeat_lock:
                last_heartbeat = time.time()
            print(f"[Executor {EXECUTOR_ID} - LEADER] Sent heartbeat at {last_heartbeat:.2f}")
        time.sleep(HEARTBEAT_INTERVAL)

def monitor_heartbeat():
    while True:
        if not is_leader():
            with heartbeat_lock:
                current_hb = last_heartbeat
            if current_hb is None or (time.time() - current_hb > HEARTBEAT_TIMEOUT):
                print(f"[Executor {EXECUTOR_ID} - FOLLOWER] Heartbeat timeout ({time.time()-current_hb if current_hb else 'None'} sec), triggering election.")
                trigger_election()
        time.sleep(HEARTBEAT_INTERVAL)

def is_leader():
    with leader_lock:
        return leader_id == EXECUTOR_ID

def trigger_election():
    global leader_id
    higher_peers = [pid for pid in PEER_IDS if pid > EXECUTOR_ID]
    if not higher_peers:
        with leader_lock:
            leader_id = EXECUTOR_ID
        print(f"[Executor {EXECUTOR_ID}] Elected as leader (no higher peers).")
    else:
        print(f"[Executor {EXECUTOR_ID}] Initiating election; sending election messages to higher peers: {higher_peers}.")
        time.sleep(3)
        new_leader = max(PEER_IDS)
        with leader_lock:
            leader_id = new_leader
        if leader_id == EXECUTOR_ID:
            print(f"[Executor {EXECUTOR_ID}] Elected as leader after election round.")
        else:
            print(f"[Executor {EXECUTOR_ID}] Remains a follower; new leader is Executor {leader_id}.")

def leader_order_execution_loop():
    print(f"[Executor {EXECUTOR_ID} - LEADER] Starting order execution loop.")
    while True:
        try:
            with grpc.insecure_channel("order_queue:50054") as q_channel:
                oq_stub = order_queue_pb2_grpc.OrderQueueServiceStub(q_channel)
                dq_response = oq_stub.Dequeue(order_queue_pb2.DequeueRequest())
                if dq_response.success:
                    order = dq_response.order
                    print(f"[Executor {EXECUTOR_ID} - LEADER] Dequeued order: {order.orderId}")
                    process_order(order)
                else:
                    print(f"[Executor {EXECUTOR_ID} - LEADER] Queue empty; waiting...")
                    time.sleep(5)
        except Exception as e:
            print(f"[Executor {EXECUTOR_ID} - LEADER] Error in Dequeue RPC: {e}")
            time.sleep(5)

import json  
def process_order(order):
    order_data = json.loads(order.jsonData)
    items = order_data.get("items", [])
    order_id = order.orderId

    db_stub = db_grpc.BooksDatabaseStub(grpc.insecure_channel(DB_PRIMARY))
    pay_stub = payment_pb2_grpc.PaymentServiceStub(grpc.insecure_channel("payment-service:50056"))

    logging.info(f"[Executor {EXECUTOR_ID}] Starting 2PC for order: {order_id}")

    # Phase 1: Check stock
    for item in items:
        read_resp = db_stub.Read(db_pb.ReadRequest(title=item["name"]))
        if read_resp.stock < item["quantity"]:
            logging.warning(f"[Executor {EXECUTOR_ID}] OUT-OF-STOCK {item['name']}")
            return False

    ready_votes = []
    for item in items:
        try:
            prepare_req = db_pb.PrepareRequest(order_id=order_id, title=item["name"], new_stock=read_resp.stock - item["quantity"])
            db_ready = db_stub.Prepare(prepare_req)
            ready_votes.append(db_ready.ready)
            logging.info(f"[Executor {EXECUTOR_ID}] DB ready vote for {item['name']}: {db_ready.ready}")
        except Exception as e:
            logging.error(f"[Executor {EXECUTOR_ID}] DB prepare failed for {item['name']}: {e}")
            ready_votes.append(False)

    try:
        pay_ready = pay_stub.Prepare(payment_pb2.PrepareRequest(order_id=order_id))
        ready_votes.append(pay_ready.ready)
        logging.info(f"[Executor {EXECUTOR_ID}] Payment ready vote: {pay_ready.ready}")
    except Exception as e:
        logging.error(f"[Executor {EXECUTOR_ID}] Payment prepare failed: {e}")
        ready_votes.append(False)

    # Phase 2: Commit or Abort
    if all(ready_votes):
        for item in items:
            try:
                db_stub.Commit(db_pb.CommitRequest(order_id=order_id))
                logging.info(f"[Executor {EXECUTOR_ID}] DB commit successful for {item['name']}")
            except Exception as e:
                logging.error(f"[Executor {EXECUTOR_ID}] DB commit failed for {item['name']}: {e}")
        try:
            pay_stub.Commit(payment_pb2.CommitRequest(order_id=order_id))
            logging.info(f"[Executor {EXECUTOR_ID}] Payment commit successful")
        except Exception as e:
            logging.error(f"[Executor {EXECUTOR_ID}] Payment commit failed: {e}")

        logging.info(f"[Executor {EXECUTOR_ID}] Order {order_id} committed successfully")
        return True
    else:
        for item in items:
            try:
                db_stub.Abort(db_pb.AbortRequest(order_id=order_id))
                logging.info(f"[Executor {EXECUTOR_ID}] DB abort completed for {item['name']}")
            except Exception as e:
                logging.warning(f"[Executor {EXECUTOR_ID}] DB abort failed for {item['name']}: {e}")
        try:
            pay_stub.Abort(payment_pb2.AbortRequest(order_id=order_id))
            logging.info(f"[Executor {EXECUTOR_ID}] Payment abort completed")
        except Exception as e:
            logging.warning(f"[Executor {EXECUTOR_ID}] Payment abort failed: {e}")

        logging.info(f"[Executor {EXECUTOR_ID}] Order {order_id} aborted")
        return False


# def process_order(order):
#     order_data = json.loads(order.jsonData)
#     items = order_data.get("items", [])
#     order_id = order.orderId

#     # gRPC stubs
#     db_stub = db_grpc.BooksDatabaseStub(grpc.insecure_channel(DB_PRIMARY))
#     pay_stub = payment_pb2_grpc.PaymentServiceStub(grpc.insecure_channel("payment-service:50056"))

#     ready_votes = []
#     updated_stocks = {}

#     # 🟡 Phase 1: Check stock & send Prepare to DB
#     for item in items:
#         try:
#             read_resp = db_stub.Read(db_pb.ReadRequest(title=item["name"]))
#             if read_resp.stock < item["quantity"]:
#                 print(f"[Executor {EXECUTOR_ID}] OUT-OF-STOCK {item['name']}")
#                 return False

#             new_stock = read_resp.stock - item["quantity"]
#             updated_stocks[item["name"]] = new_stock

#             prep_resp = db_stub.Prepare(db_pb.PrepareRequest(
#                 order_id=order_id,
#                 title=item["name"],
#                 new_stock=new_stock
#             ))
#             ready_votes.append(prep_resp.ready)

#         except Exception as e:
#             print(f"[Executor {EXECUTOR_ID}] DB Prepare failed for {item['name']}: {e}")
#             ready_votes.append(False)

#     # 🔵 Phase 1: Send Prepare to Payment
#     try:
#         pay_ready = pay_stub.Prepare(payment_pb2.PrepareRequest(order_id=order_id))
#         ready_votes.append(pay_ready.ready)
#     except Exception as e:
#         print(f"[Executor {EXECUTOR_ID}] Payment Prepare failed: {e}")
#         ready_votes.append(False)

#     # 🟢 Phase 2: Commit or Abort
#     if all(ready_votes):
#         # COMMIT
#         for item in items:
#             db_stub.Commit(db_pb.CommitRequest(order_id=order_id))
#         pay_stub.Commit(payment_pb2.CommitRequest(order_id=order_id))
#         print(f"[Executor {EXECUTOR_ID}] Order {order_id} committed")
#         return True
#     else:
#         # ABORT
#         for item in items:
#             db_stub.Abort(db_pb.AbortRequest(order_id=order_id))
#         pay_stub.Abort(payment_pb2.AbortRequest(order_id=order_id))
#         print(f"[Executor {EXECUTOR_ID}] Order {order_id} aborted")
#         return False


class ExecutorServicer(executor_pb2_grpc.ExecutorServiceServicer):
    def ExecuteOrder(self, request, context):
        return executor_pb2.ExecutionResponse(success=True, message="Order executed")

def serve():
    global leader_id
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    executor_pb2_grpc.add_ExecutorServiceServicer_to_server(ExecutorServicer(), server)
    local_port = 50055
    server.add_insecure_port(f"[::]:{local_port}")
    server.start()
    print(f"[Executor {EXECUTOR_ID}] gRPC Executor Service started on port {local_port}")

    heartbeat_sender = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_sender.start()
    heartbeat_monitor = threading.Thread(target=monitor_heartbeat, daemon=True)
    heartbeat_monitor.start()

    trigger_election()

    if is_leader():
        leader_thread = threading.Thread(target=leader_order_execution_loop, daemon=True)
        leader_thread.start()
    else:
        print(f"[Executor {EXECUTOR_ID}] Running as follower; not executing orders.")

    server.wait_for_termination()

if __name__ == "__main__":
    serve()
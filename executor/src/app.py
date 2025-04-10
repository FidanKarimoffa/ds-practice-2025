import os
import sys
import time
import json
import uuid
import grpc
from concurrent import futures
import threading

# Import the generated stubs from executor.proto (in the same executor package)
from bookstore.executor import executor_pb2, executor_pb2_grpc

# Import the Order Queue stubs (which were generated with package bookstore.order_queue)
from bookstore.order_queue import order_queue_pb2, order_queue_pb2_grpc

###############################################
# Global Variables for Election and Heartbeat
###############################################
# Global variable for tracking the last heartbeat timestamp.
last_heartbeat = None
heartbeat_lock = threading.Lock()

# Leader ID is a global variable updated during election.
leader_id = None
leader_lock = threading.Lock()

# Configuration for heartbeat intervals and timeouts.
HEARTBEAT_INTERVAL = 5  # seconds between heartbeats sent by the leader
HEARTBEAT_TIMEOUT = 30  # seconds to wait for heartbeat before triggering an election

###############################################
# Unique Executor ID and Peer List from Environment
###############################################
try:
    EXECUTOR_ID = int(os.getenv("EXECUTOR_ID"))
except (TypeError, ValueError):
    print("Error: EXECUTOR_ID environment variable is not set or invalid.")
    sys.exit(1)

# PEER_IDS provided as comma-separated list (including our own)
peer_ids_env = os.getenv("PEER_IDS", str(EXECUTOR_ID))
PEER_IDS = sorted([int(x.strip()) for x in peer_ids_env.split(",")])
print(f"[Executor {EXECUTOR_ID}] Peers in system: {PEER_IDS}")

###############################################
# Heartbeat Functions
###############################################
def send_heartbeat():
    """If this executor is the leader, continuously update the last heartbeat timestamp."""
    global last_heartbeat
    while True:
        if is_leader():
            with heartbeat_lock:
                last_heartbeat = time.time()
            print(f"[Executor {EXECUTOR_ID} - LEADER] Sent heartbeat at {last_heartbeat:.2f}")
        time.sleep(HEARTBEAT_INTERVAL)

def monitor_heartbeat():
    """
    For follower nodes:
      - Check periodically if a heartbeat has been received within HEARTBEAT_TIMEOUT seconds.
      - If not, trigger an election.
    """
    while True:
        if not is_leader():
            with heartbeat_lock:
                current_hb = last_heartbeat
            if current_hb is None or (time.time() - current_hb > HEARTBEAT_TIMEOUT):
                print(f"[Executor {EXECUTOR_ID} - FOLLOWER] Heartbeat timeout ({time.time()-current_hb if current_hb else 'None'} sec), triggering election.")
                trigger_election()
        time.sleep(HEARTBEAT_INTERVAL)

###############################################
# Bully Election Logic (Simplified)
###############################################
def is_leader():
    """Returns True if this executor is currently the leader."""
    with leader_lock:
        return leader_id == EXECUTOR_ID

def trigger_election():
    """
    Simplified Bully election:
      - If this executor detects a heartbeat failure, it triggers an election.
      - It sends messages to all peers with a higher ID.
      - For simulation, we assume all nodes are reachable.
      - The node with the highest ID becomes the leader.
    """
    global leader_id
    # Determine higher peers
    higher_peers = [pid for pid in PEER_IDS if pid > EXECUTOR_ID]
    if not higher_peers:
        # No higher peers: this node becomes leader
        with leader_lock:
            leader_id = EXECUTOR_ID
        print(f"[Executor {EXECUTOR_ID}] Elected as leader (no higher peers).")
    else:
        print(f"[Executor {EXECUTOR_ID}] Initiating election; sending election messages to higher peers: {higher_peers}.")
        # Simulate waiting for responses (here, we simply wait a fixed delay)
        time.sleep(3)
        # In a real implementation, responses would determine who is alive.
        # For simulation, assume the highest ID in the system becomes leader.
        new_leader = max(PEER_IDS)
        with leader_lock:
            leader_id = new_leader
        if leader_id == EXECUTOR_ID:
            print(f"[Executor {EXECUTOR_ID}] Elected as leader after election round.")
        else:
            print(f"[Executor {EXECUTOR_ID}] Remains a follower; new leader is Executor {leader_id}.")

###############################################
# Leader-Exclusive Order Dequeue and Processing
###############################################
def leader_order_execution_loop():
    """
    If this executor is the leader, continuously poll the Order Queue service to dequeue orders and process them.
    Only the leader will perform this action.
    """
    print(f"[Executor {EXECUTOR_ID} - LEADER] Starting order execution loop.")
    while True:
        try:
            with grpc.insecure_channel("order_queue:50054") as q_channel:
                oq_stub = order_queue_pb2_grpc.OrderQueueServiceStub(q_channel)
                dq_response = oq_stub.Dequeue(order_queue_pb2.DequeueRequest())
                if dq_response.success:
                    order = dq_response.order
                    print(f"[Executor {EXECUTOR_ID} - LEADER] Dequeued order: {order.orderId}")
                    # Process the order (simulate processing)
                    process_order(order)
                else:
                    print(f"[Executor {EXECUTOR_ID} - LEADER] Queue empty; waiting...")
                    time.sleep(5)
        except Exception as e:
            print(f"[Executor {EXECUTOR_ID} - LEADER] Error in Dequeue RPC: {e}")
            time.sleep(5)

def process_order(order):
    """Simulate processing the order retrieved from the queue."""
    print(f"[Executor {EXECUTOR_ID} - LEADER] Processing order {order.orderId} with data: {order.jsonData}")
    time.sleep(2)
    print(f"[Executor {EXECUTOR_ID} - LEADER] Finished processing order {order.orderId}")

###############################################
# gRPC Executor Service Implementation (for inter-node communication)
###############################################
class ExecutorServicer(executor_pb2_grpc.ExecutorServiceServicer):
    def ExecuteOrder(self, request, context):
        # This is an additional RPC which could be invoked by other executors
        # For now, we simply process the order
        return executor_pb2.ExecutionResponse(success=True, message="Order executed")

###############################################
# Main Function: Start gRPC Service and Election Mechanisms
###############################################
def serve():
    global leader_id
    # Start the executor's own gRPC service
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    executor_pb2_grpc.add_ExecutorServiceServicer_to_server(ExecutorServicer(), server)
    local_port = 50055
    server.add_insecure_port(f"[::]:{local_port}")
    server.start()
    print(f"[Executor {EXECUTOR_ID}] gRPC Executor Service started on port {local_port}")

    # Start heartbeat sender and monitor threads in background
    heartbeat_sender = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_sender.start()
    heartbeat_monitor = threading.Thread(target=monitor_heartbeat, daemon=True)
    heartbeat_monitor.start()

    # Immediately trigger an election on startup
    trigger_election()

    # If elected leader, launch the leader order execution loop in a background thread
    if is_leader():
        leader_thread = threading.Thread(target=leader_order_execution_loop, daemon=True)
        leader_thread.start()
    else:
        print(f"[Executor {EXECUTOR_ID}] Running as follower; not executing orders.")

    # Wait indefinitely for the gRPC server to run
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

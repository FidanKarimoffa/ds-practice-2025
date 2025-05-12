import os
import grpc
from concurrent import futures

from utils.pb import books_db_pb2_grpc as pb_grpc

from .servicer_base import BooksDatabaseServicer
from .primary        import PrimaryReplica

ROLE         = os.getenv("ROLE", "primary")
PORT         = int(os.getenv("PORT", 6000))
BACKUP_PEERS = os.getenv("BACKUP_PEERS", "")   # host:port,...

def build_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    if ROLE == "primary":
        stubs = []
        for peer in BACKUP_PEERS.split(","):
            if peer:
                ch = grpc.insecure_channel(peer)
                stubs.append(pb_grpc.BooksDatabaseStub(ch))
        servicer = PrimaryReplica(stubs)
    else:
        servicer = BooksDatabaseServicer()

    pb_grpc.add_BooksDatabaseServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    return server

if __name__ == "__main__":
    srv = build_server()
    print(f"[Books-DB:{ROLE}] listening on {PORT}")
    srv.start()
    srv.wait_for_termination()

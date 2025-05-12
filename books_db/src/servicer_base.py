import grpc
from concurrent import futures
from collections import defaultdict

import utils.pb.books_db_pb2 as db_pb2
import utils.pb.books_db_pb2_grpc as db_pb2_grpc

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [BooksDB] %(message)s'
)
logger = logging.getLogger()


class BooksDatabaseServicer(db_pb2_grpc.BooksDatabaseServicer):
    def __init__(self):
        # Real stock for each book
        self.inventory = defaultdict(lambda: 10)
        # Staged updates for prepare phase
        self.staged_updates = {}

    def Read(self, request, context):
        stock = self.inventory[request.title]
        logger.info(f"Read stock for '{request.title}': {stock}")
        return db_pb2.ReadResponse(stock=stock)

    def Write(self, request, context):
        self.inventory[request.title] = request.new_stock
        logger.info(f"Wrote stock for '{request.title}': {request.new_stock}")
        return db_pb2.WriteResponse(success=True)

    def Prepare(self, request, context):
        logger.info(f"Preparing update for order {request.order_id}, book: {request.title}")
        key = (request.order_id, request.title)
        self.staged_updates[key] = request.new_stock
        return db_pb2.PrepareResponse(ready=True)

    def Commit(self, request, context):
        logger.info(f"Committing updates for order {request.order_id}")
        to_commit = [(k, v) for k, v in self.staged_updates.items() if k[0] == request.order_id]
        for (order_id, title), new_stock in to_commit:
            self.inventory[title] = new_stock
            del self.staged_updates[(order_id, title)]
        return db_pb2.CommitResponse(success=True)

    def Abort(self, request, context):
        logger.warning(f"Aborting updates for order {request.order_id}")
        to_abort = [k for k in self.staged_updates if k[0] == request.order_id]
        for k in to_abort:
            del self.staged_updates[k]
        return db_pb2.AbortResponse(aborted=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_pb2_grpc.add_BooksDatabaseServicer_to_server(BooksDatabaseServicer(), server)
    server.add_insecure_port("[::]:6000")
    print("[BooksDB] Books Database Server started on port 6000")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

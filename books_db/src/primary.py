import grpc
import logging
from .servicer_base import BooksDatabaseServicer
from utils.pb import books_db_pb2 as pb, books_db_pb2_grpc as pb_grpc

# Configure logging at the top of the module
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class PrimaryReplica(BooksDatabaseServicer):
    def __init__(self, backup_stubs):
        super().__init__()
        self.backups = backup_stubs  # list[BooksDatabaseStub]

    def Write(self, request, context):
        # 1️⃣ Local commit
        self.store[request.title] = request.new_stock
        logger.info(f"[Primary] Local write: '{request.title}' → {request.new_stock}")

        # 2️⃣ Propagate to backups
        acks = 0
        for idx, stub in enumerate(self.backups, start=1):
            try:
                stub.Write(request, timeout=2)
                acks += 1
                logger.info(f"[Primary] Backup #{idx} ACKed write of '{request.title}'")
            except grpc.RpcError as e:
                logger.warning(f"[Primary] Backup #{idx} failed: {e.code()} – {e.details()}")

        # 3️⃣ Log overall result
        if acks > 0:
            logger.info(f"[Primary] Replication succeeded ({acks}/{len(self.backups)} backups)")
        else:
            logger.error("[Primary] Replication FAILED on all backups")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Replication failed on all backups")

        # 4️⃣ Return to client
        return pb.WriteResponse(success=(acks > 0))

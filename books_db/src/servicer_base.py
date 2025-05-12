from utils.pb import books_db_pb2 as pb, books_db_pb2_grpc as pb_grpc

class BooksDatabaseServicer(pb_grpc.BooksDatabaseServicer):
    def __init__(self):
        self.store = {
            "Harry Potter and the Philosopher's Stone": 10,
            "The Lord of the Rings": 10
        }                                  
    def Read(self, request, context):
        return pb.ReadResponse(stock=self.store.get(request.title, 0))

    def Write(self, request, context):
        self.store[request.title] = request.new_stock
        return pb.WriteResponse(success=True)

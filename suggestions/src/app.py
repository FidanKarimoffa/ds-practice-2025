import sys
import os
import json
from concurrent import futures

# For the LLM calls
from google import genai
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("API_KEY")
API_KEY = "AIzaSyA7k3mveCWpA5MrnZ92G3lbGQ_RE6FBjhI"  

FILE = __file__ if "__file__" in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/suggestions"))
sys.path.insert(0, utils_path)

import suggestions_pb2 as sug_pb
import suggestions_pb2_grpc as sug_grpc

import grpc

class BookSuggestionService(sug_grpc.SuggestionsServiceServicer):
    """
    We keep an optional caching approach + vector clocks, 
    storing 'OrderData' protobuf objects, not Python dicts.
    """

    def __init__(self):
        super().__init__()
        self.cached_orders = {}     # orderId -> sug_pb.OrderData  # <-- CHANGED
        self.vector_clocks = {}     # orderId -> [o, t, f, s]

    def CacheOrder(self, request, context):
        order_id = request.orderId
        print(f"[Suggestions] CacheOrder called for orderId={order_id}")

        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        # Suppose index 3 is "suggestions"
        merged_vc[3] += 1
        self.vector_clocks[order_id] = merged_vc

        # Store the protobuf OrderData  # <-- CHANGED
        self.cached_orders[order_id] = request.orderData

        resp = sug_pb.CacheOrderResponse()
        resp.updatedVectorClock.extend(merged_vc)
        return resp

    # (f) Generate suggestions
    def GenerateSuggestions(self, request, context):
        print("[Suggestions] GenerateSuggestions called.")
        order_id = request.orderId

        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[3] += 1
        self.vector_clocks[order_id] = merged_vc

        # Retrieve the cached protobuf OrderData <-- CHANGED
        data = self.cached_orders.get(order_id, None)

        # Extract first item name from data.items
        first_item_name = ""
        if data and data.items:
            first_item_name = data.items[0].name

        prompt = f"""
List a few popular books similar to {first_item_name} in JSON format.

Use this JSON schema:
SuggestedBooks = {{'book_title': str, 'book_author': str}}
Return: list[SuggestedBooks]
"""
        client = genai.Client(api_key=API_KEY)
        suggested_books = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        result_str = suggested_books.text.replace("```json", "").replace("```", "").strip()
        parsed_list = []
        try:
            parsed_list = json.loads(result_str)
        except:
            pass

        response = sug_pb.SuggestionsResponse()
        response.updatedVectorClock.extend(merged_vc)
        # Convert parsed_list into repeated <BookEntry>
        for entry in parsed_list:
            book_entry = sug_pb.BookEntry()
            book_entry.book_title = entry.get("book_title","Unknown")
            book_entry.book_author = entry.get("book_author","Unknown")
            response.suggestions.append(book_entry)
        return response

    # Legacy single-shot method if you want to keep SuggestBooks
    def SuggestBooks(self, request, context):
        print("[Suggestions] SuggestBooks called (legacy).")
        # Old code that calls gemini API, etc...
        response = sug_pb.SuggestionsResponse()
        # Not returning a vector clock in the legacy approach
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    sug_grpc.add_SuggestionsServiceServicer_to_server(BookSuggestionService(), server)
    port = "50053"
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Book Suggestion Server started on port {port}.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

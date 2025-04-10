# import sys
# import os
# import uuid
# import random
# import time
# import re
# import calendar
# from datetime import datetime
# # This set of lines are needed to import the gRPC stubs.
# # The path of the stubs is relative to the current file, or absolute inside the container.
# # Change these lines only if strictly needed.
# FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
# transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/bookstore/transaction_verification'))
# sys.path.insert(0, transaction_verification_grpc_path)
# import transaction_verification_pb2 as transaction_verification
# import transaction_verification_pb2_grpc as transaction_verification_grpc
# import grpc
# from concurrent import futures


# def validate_required_fields(request):
#     """Check that required fields are present and non-empty."""
#     missing = []
#     # User fields
#     if not request.user.name:
#         missing.append("user.name")
#     if not request.user.contact:
#         missing.append("user.contact")
#     # Credit card fields
#     if not request.creditCard.number:
#         missing.append("creditCard.number")
#     if not request.creditCard.expirationDate:
#         missing.append("creditCard.expirationDate")
#     if not request.creditCard.cvv:
#         missing.append("creditCard.cvv")
#     # Billing Address
#     if not request.billingAddress.street or not request.billingAddress.city or not request.billingAddress.country:
#         missing.append("billingAddress (street/city/country)")
#     # Shipping Address
#     # if not request.shippingAddress.street or not request.shippingAddress.city or not request.shippingAddress.country:
#     #     missing.append("shippingAddress (street/city/country)")
#     # Items list
#     if len(request.items) == 0:
#         missing.append("items (list is empty)")
#     return missing

# def validate_credit_card_number(number):
#     """Validate that the credit card number is exactly 16 digits."""
#     nDigits = len(number)
#     nSum =0 
#     isSecond = False
#     for i in range(nDigits-1,-1,-1):
#         d = ord(number[i]) - ord('0')
#         if (isSecond == True):
#             d= d*2
#         nSum +=d//10
#         nSum +=d%10
#         isSecond = not isSecond
#     if (nSum % 10 == 0):
#         return True
#     else:
#         return False
            

# def validate_expiration_date(date_str):
#     """Validate the expiration date is in MM/YY format and not expired (using end-of-month)."""
#     if not re.fullmatch(r"\d{2}/\d{2}", date_str):
#         return False
#     try:
#         month, year = date_str.split("/")
#         month = int(month)
#         year = int("20" + year)
#         if month < 1 or month > 12:
#             return False
#         last_day = calendar.monthrange(year, month)[1]
#         exp_date = datetime(year, month, last_day)
#         # The card is valid if current date is before or on the expiration date.
#         return datetime.now() <= exp_date
#     except Exception:
#         return False

# def validate_cvv(cvv):
#     """Validate that CVV is 3  digits."""
#     return bool(re.fullmatch(r"\d{3}", cvv))



# class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer):
#     def VerifyTransaction(self, request, context):
#         """
#         Implementation of VerifyTransaction.
#         Applies basic validation logic on the incoming transaction request.
#         """
#         print(f"Received transaction verification request : {request}")
        
#         if not request.items:
#             response.verification = False
#             response.errors = "Items list is empty"
#             return response
#         # 1. Validate required fields
#         missing = validate_required_fields(request)
#         if missing:
#             response = transaction_verification.TransactionVerificationResponse()
#             response.verification = False
#             response.errors = "Missing required fields: " + ", ".join(missing)
#             return response
        
#         # 2. Validate credit card number format
#         if not validate_credit_card_number(request.creditCard.number):
#             response = transaction_verification.TransactionVerificationResponse()
#             response.verification = False
#             response.errors = "Invalid credit card number."
#             return response

#         # 3. Validate expiration date format and check if card is expired
#         if not validate_expiration_date(request.creditCard.expirationDate):
#             response = transaction_verification.TransactionVerificationResponse()
#             response.verification = False
#             response.errors = "Invalid or expired credit card expiration date."
#             return response
        
#         # 4. Validate CVV
#         if not validate_cvv(request.creditCard.cvv):
#             response = transaction_verification.TransactionVerificationResponse()
#             response.verification = False
#             response.errors = "Invalid CVV. It must be 3 digits."
#             return response
        
#         # 5. Additional simple validations can be added here (e.g., checking email format)
#         # For demonstration, if all validations pass, we consider the transaction valid.
#         response = transaction_verification.TransactionVerificationResponse()
#         response.verification = True
#         response.errors = "No  errors"

#         return response
    
# def serve():
#     # Create a gRPC server
#     server = grpc.server(futures.ThreadPoolExecutor())
#     # Add TransactionDetectionService
#     transaction_verification_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
#     # Listen on port 50052
#     port = "50052"
#     server.add_insecure_port("[::]:" + port)
#     # Start the server
#     server.start()
#     print("Transaction Verification Server started. Listening on 50052.")
#     # Keep thread alive
#     server.wait_for_termination()

# if __name__ == '__main__':
#      serve()  









import sys
import os
import re
import calendar
from datetime import datetime
from concurrent import futures

import grpc

# gRPC stubs imports
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
transaction_verification_grpc_path = os.path.abspath(
    os.path.join(FILE, "../../../utils/pb/bookstore/transaction_verification")
)
sys.path.insert(0, transaction_verification_grpc_path)

import transaction_verification_pb2 as tx_pb
import transaction_verification_pb2_grpc as tx_grpc

########################################################
# HELPER VALIDATION FUNCTIONS
########################################################

def validate_credit_card_number(number: str) -> bool:
    """Validate credit card number with a Luhn-like approach."""
    n_sum = 0
    is_second = False
    for i in range(len(number) - 1, -1, -1):
        d = ord(number[i]) - ord("0")
        if is_second:
            d = d * 2
        n_sum += d // 10
        n_sum += d % 10
        is_second = not is_second
    return (n_sum % 10 == 0)

def validate_expiration_date(date_str: str) -> bool:
    """Validate the expiration date in MM/YY, not expired (using end-of-month)."""
    if not re.fullmatch(r"\d{2}/\d{2}", date_str):
        return False
    try:
        month, year = date_str.split("/")
        month = int(month)
        year = int("20" + year)  # e.g. '25' => 2025
        if month < 1 or month > 12:
            return False
        last_day = calendar.monthrange(year, month)[1]
        exp_date = datetime(year, month, last_day)
        return datetime.now() <= exp_date
    except Exception:
        return False

def validate_cvv(cvv: str) -> bool:
    """Validate that CVV is 3 digits."""
    return bool(re.fullmatch(r"\d{3}", cvv))

########################################################
# GRPC SERVICE IMPLEMENTATION
########################################################

class TransactionVerificationService(tx_grpc.TransactionVerificationServiceServicer):
    """
    Splits the verification logic into:
      - CacheOrder
      - CheckItemsNonEmpty (a)
      - CheckMandatoryFields (b)
      - CheckCreditCardFormat (c)
    Also tracks vector clocks per orderId.
    """

    def __init__(self):
        super().__init__()
        # Dictionary to cache order data keyed by orderId
        # Now storing protobuf OrderData objects, not dicts
        self.cached_orders = {}    # orderId -> tx_pb.OrderData  # <-- CHANGED
        # Dictionary to store vector clocks: orderId -> [o, t, f, s]
        self.vector_clocks = {}    # orderId -> list of 4 ints

    # 1) Cache the order data, so we don't run the checks all at once.
    def CacheOrder(self, request, context):
        """
        Receives an orderId, the order data, and the orchestrator's vector clock,
        merges and caches them.
        """
        order_id = request.orderId
        print(f"[Transaction] CacheOrder called for orderId={order_id}")

        # Merge vector clocks
        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        # This service is index 1 in the vector clock
        merged_vc[1] += 1

        # Store the protobuf OrderData, not a dict  # <-- CHANGED
        self.cached_orders[order_id] = request.orderData
        self.vector_clocks[order_id] = merged_vc

        # Return updated vector clock
        response = tx_pb.CacheOrderResponse()
        response.updatedVectorClock.extend(merged_vc)
        return response

    # (a) Check if the items list is not empty
    def CheckItemsNonEmpty(self, request, context):
        print("[Transaction] CheckItemsNonEmpty called.")
        order_id = request.orderId
        # Merge vector clocks
        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[1] += 1
        self.vector_clocks[order_id] = merged_vc

        # Extract the cached protobuf OrderData  # <-- CHANGED
        order_data = self.cached_orders.get(order_id, None)

        response = tx_pb.TransactionVerificationResponse()
        if not order_data:
            # If for some reason the data is missing
            response.verification = False
            response.errors = "No cached order data found."
        else:
            # Access 'items' field via dot notation  # <-- CHANGED
            items = order_data.items
            if len(items) == 0:
                response.verification = False
                response.errors = "Items list is empty."
            else:
                response.verification = True
                response.errors = "No errors: items are not empty."

        # Return updated vector clock
        response.vectorClock.extend(merged_vc)
        return response

    # (b) Check mandatory user fields and addresses
    def CheckMandatoryFields(self, request, context):
        print("[Transaction] CheckMandatoryFields called.")
        order_id = request.orderId
        # Vector clock merge
        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[1] += 1
        self.vector_clocks[order_id] = merged_vc

        order_data = self.cached_orders.get(order_id, None)  # <-- CHANGED
        response = tx_pb.TransactionVerificationResponse()
        if not order_data:
            response.verification = False
            response.errors = "No cached order data found."
        else:
            missing = []
            # user
            user = order_data.user
            if user.name == "":
                missing.append("user.name")
            if user.contact == "":
                missing.append("user.contact")

            # billing
            billing = order_data.billingAddress
            if not billing.street or not billing.city or not billing.country:
                missing.append("billingAddress (street/city/country)")

            if missing:
                response.verification = False
                response.errors = "Missing mandatory fields: " + ", ".join(missing)
            else:
                response.verification = True
                response.errors = "No errors: mandatory fields present."

        response.vectorClock.extend(merged_vc)
        return response

    # (c) Check credit card format (number, expiration, and CVV)
    def CheckCreditCardFormat(self, request, context):
        print("[Transaction] CheckCreditCardFormat called.")
        order_id = request.orderId
        # Vector clock merge
        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0, 0, 0, 0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[1] += 1
        self.vector_clocks[order_id] = merged_vc

        order_data = self.cached_orders.get(order_id, None)  # <-- CHANGED
        response = tx_pb.TransactionVerificationResponse()

        if not order_data:
            response.verification = False
            response.errors = "No cached order data found."
        else:
            cc = order_data.creditCard  # <-- CHANGED
            if not validate_credit_card_number(cc.number):
                response.verification = False
                response.errors = "Invalid credit card number."
                response.vectorClock.extend(merged_vc)
                return response

            if not validate_expiration_date(cc.expirationDate):
                response.verification = False
                response.errors = "Invalid or expired credit card expiration date."
                response.vectorClock.extend(merged_vc)
                return response

            if not validate_cvv(cc.cvv):
                response.verification = False
                response.errors = "Invalid CVV. Must be 3 digits."
                response.vectorClock.extend(merged_vc)
                return response

            response.verification = True
            response.errors = "No errors: credit card format is valid."

        response.vectorClock.extend(merged_vc)
        return response

    # Optional: legacy single-shot method
    def VerifyTransaction(self, request, context):
        print("[Transaction] Legacy VerifyTransaction called.")
        response = tx_pb.TransactionVerificationResponse()
        response.verification = False
        response.errors = "Legacy call not implemented in partial order mode."
        return response

def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor())
    tx_grpc.add_TransactionVerificationServiceServicer_to_server(
        TransactionVerificationService(), server
    )
    port = "50052"
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Transaction Verification Server started on port {port}.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

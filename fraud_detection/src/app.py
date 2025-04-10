# import sys
# import os
# import uuid
# import random
# import time
# import calendar
# from datetime import datetime
# import pandas as pd
# import joblib
# import xgboost as xgb
# # This set of lines are needed to import the gRPC stubs.
# # The path of the stubs is relative to the current file, or absolute inside the container.
# # Change these lines only if strictly needed.
# FILE = __file__ if "__file__" in globals() else os.getenv("PYTHONFILE", "")
# utils_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/fraud_detection"))
# sys.path.insert(0, utils_path)
# import fraud_detection_pb2 as fraud_detection
# import fraud_detection_pb2_grpc as fraud_detection_grpc

# import grpc
# from concurrent import futures

# # Create a class to define the server functions, derived from
# # fraud_detection_pb2_grpc.FraudDetectionServiceServicer

# def getReason(prediction,credit_card_valid,name_match,total_num_items,billing_shipping_match):
#      reasons = []
 
#      if prediction == 1:
#     # Check if credit card is invalid
#       if credit_card_valid == 0:
#         reasons.append("card is expired")
#     # Check for name mismatch (if names differ)
#       if name_match == 0:
#         reasons.append("card holder name does not match username")
#     # Check if total quantity is high (here > 3 is considered high)
#       if total_num_items > 3:
#         reasons.append("high quantity of items")
#     # Check if billing and shipping addresses do not match
#       if billing_shipping_match == 0:
#         reasons.append("shipping address does not match billing address")
#      return reasons

    
    



# def processRequest(data):
#     # 1. Extract base fields
#   try:
#      print("Data to process:", data)
#      username = data.user.name
#      contact = data.user.contact
#      card_holder_name = data.user.cardHolderName
    
#      credit_card_number = data.creditCard.number
#      expiration_date = data.creditCard.expirationDate
#      cvv = data.creditCard.cvv
    
#      user_comment = data.userComment  # not used for features, but you can log it

#      items = data.items  # this will be a repeated field of OrderItem objects

#      billing_street = data.billingAddress.street
#      billing_city = data.billingAddress.city
#      billing_country = data.billingAddress.country
    
#      shipping_street = data.shippingAddress.street
#      shipping_city = data.shippingAddress.city
#      shipping_country = data.shippingAddress.country

#      shipping_method = data.shippingMethod  # not used for your model if you decided to drop it
#      gift_wrapping = data.giftWrapping
#      terms_accepted = data.termsAccepted
    
#     # 2. Compute engineered features (similar to your example)
#      total_num_items = sum(item.quantity for item in items)
    
#      billing_shipping_match = (
#         (billing_street == shipping_street) and
#         (billing_city == shipping_city) and
#         (billing_country == shipping_country)
#      )
    
#     # Check credit card validity (assuming you have a helper function)
#      credit_card_valid = 1 if isCreditCardValid(expiration_date) else 0
    
#     # Compare username and card holder name
#      name_match = 1 if (username == card_holder_name) else 0
    
#     # 3. Build the feature dictionary
#      feature_cols = [
#         "total_num_items",
#         "billing_shipping_match",
#         "credit_card_valid",
#         "name_match",
#         "gift_wrapping",
#         "terms_accepted"
#     ]
    
#      input_data = {
#         "total_num_items": [total_num_items],
#         "billing_shipping_match": [1 if billing_shipping_match else 0],
#         "credit_card_valid": [credit_card_valid],
#         "name_match": [name_match],
#         "gift_wrapping": [1 if gift_wrapping else 0],
#         "terms_accepted": [1 if terms_accepted else 0]
#     }
    
#     # 4. Convert to DataFrame (and eventually to the array your model expects)
#      df_input = pd.DataFrame(input_data)
#      X_input = df_input.astype('float32').values
#   except Exception as e:
#     print("Error processing request:", e)
#     raise  Exception("Error processing request:", e)
#   print("X_input:", X_input)
#   return X_input, feature_cols,credit_card_valid,name_match,total_num_items,billing_shipping_match


# def isCreditCardValid(expiration_date_str):
#      try:
#         exp_month, exp_year = expiration_date_str.split("/")
#         exp_month = int(exp_month)
#         exp_year = int("20" + exp_year) if len(exp_year) == 2 else int(exp_year)
#         last_day = calendar.monthrange(exp_year, exp_month)[1]
#         expiration_date = datetime(exp_year, exp_month, last_day)
#         return datetime.now() < expiration_date
#      except Exception as e:
#         print("Error parsing expiration date:", e)
#         return False
    

# class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):
#     # Create an RPC function to detect fraud
#     def DetectUserFraud(self, request, context):
        
#         print("Request:",request)
#         X_input, feature_cols,credit_card_valid,name_match,total_num_items,billing_shipping_match = processRequest(request)
#         print("New Data:", X_input, feature_cols)  
#      # Use os.path.join for better path handling
#         model_path = os.path.join("/app/fraud_detection.pkl")
#         print(f"Loading model from: {model_path}")
#         model = joblib.load(model_path)
#         X_input_matrix = xgb.DMatrix(X_input, feature_names=feature_cols)
#        # 3. Use the model to predict (binary classification)
#         prediction = model.predict(X_input_matrix)[0] 
#         prob = 1 if prediction >= 0.5 else 0
#         reasons = getReason(prob,credit_card_valid,name_match,total_num_items,billing_shipping_match)# 0 or 1
#        # Or get probabilities if the model supports predict_proba
#     #  probabilities = model.predict_proba(X_input_matrix)[0]
#         print("Prediction:", prediction)
#         # print("Reasons:", reasons)
#         value = True if prediction >= 0.5 else False
#         print("Value:", value)
#         response = fraud_detection.FraudDetectionResponse(
#           isFraudulent = value,
#           reason = "" if len(reasons) == 0 else str(reasons[0])
#         )
#         print("Response isFraudulent:", response.isFraudulent)
#         print("Response reason:", response.reason)
      
#         return response
    
    
    
    
        
    
# def serve():
#     # Create a gRPC server
#     server = grpc.server(futures.ThreadPoolExecutor())
#     # Add FraudDetectionService
#     fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)
#     # Listen on port 50051
#     port = "50051"
#     server.add_insecure_port("[::]:" + port)
#     # Start the server
#     server.start()
#     print("Fraud Detection Server started. Listening on port 50051.")
#     # Keep thread alive
#     server.wait_for_termination()

# if __name__ == '__main__':
#     serve()









import sys
import os
import calendar
from datetime import datetime
from concurrent import futures

import pandas as pd
import joblib
import xgboost as xgb
import grpc

FILE = __file__ if "__file__" in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/fraud_detection"))
sys.path.insert(0, utils_path)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

########################################################
# HELPER FUNCTIONS
########################################################

def isCreditCardValid(expiration_date_str: str) -> bool:
    """Return True if the card has not expired, based on MM/YY."""
    try:
        exp_month, exp_year = expiration_date_str.split("/")
        exp_month = int(exp_month)
        exp_year = int("20" + exp_year) if len(exp_year) == 2 else int(exp_year)
        last_day = calendar.monthrange(exp_year, exp_month)[1]
        exp_date = datetime(exp_year, exp_month, last_day)
        return datetime.now() < exp_date
    except Exception as e:
        print("Error parsing expiration date:", e)
        return False

def load_model():
    model_path = os.path.join("/app/fraud_detection.pkl")
    print(f"Loading XGBoost model from: {model_path}")
    return joblib.load(model_path)

########################################################
# FRAUD DETECTION SERVICE
########################################################

class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):
    """
    Splits fraud checks into:
      - CacheOrder (store data + vector clock)
      - CheckUserDataFraud (d)
      - CheckCreditCardFraud (e)
    Uses vector clocks & in-memory caching of protobuf OrderData objects.
    """

    def __init__(self):
        super().__init__()
        self.cached_orders = {}   # orderId -> OrderData (protobuf)
        self.vector_clocks = {}   # orderId -> [orch, tx, fraud, sug]
        self.model = load_model() # Load XGBoost

    def CacheOrder(self, request, context):
        """Store the order data & merge the vector clock."""
        order_id = request.orderId
        print(f"[Fraud] CacheOrder called for orderId={order_id}")

        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0,0,0,0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[2] += 1  # index 2 for Fraud
        self.vector_clocks[order_id] = merged_vc

        self.cached_orders[order_id] = request.orderData

        resp = fraud_detection.CacheOrderResponse()
        resp.updatedVectorClock.extend(merged_vc)
        return resp

    def CheckUserDataFraud(self, request, context):
        """
        (d) Basic user check: name mismatch, terms not accepted, etc.
        """
        print("[Fraud] CheckUserDataFraud called.")
        order_id = request.orderId

        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0,0,0,0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[2] += 1
        self.vector_clocks[order_id] = merged_vc

        data = self.cached_orders.get(order_id)
        if not data:
            # If no data, consider it fraudulent or handle differently
            is_fraudulent = True
            reason = "No cached order data found"
        else:
            user = data.user
            # E.g., mismatch if user.name != user.cardHolderName
            if user.name != user.cardHolderName:
                is_fraudulent = True
                reason = "Name mismatch (user vs cardHolderName)"
            elif not data.termsAccepted:
                is_fraudulent = True
                reason = "User hasn't accepted terms"
            else:
                is_fraudulent = False
                reason = ""

        resp = fraud_detection.FraudDetectionResponse(
            isFraudulent=is_fraudulent,
            reason=reason
        )
        resp.vectorClock.extend(merged_vc)
        return resp

    def CheckCreditCardFraud(self, request, context):
        """
        (e) Advanced credit card fraud check using the XGBoost model.
        The model expects 6 features:
          [ 'total_num_items', 'billing_shipping_match',
            'credit_card_valid', 'name_match',
            'gift_wrapping', 'terms_accepted' ]
        """
        print("[Fraud] CheckCreditCardFraud called.")
        order_id = request.orderId

        # 1) Merge vector clocks
        incoming_vc = list(request.vectorClock)
        local_vc = self.vector_clocks.get(order_id, [0,0,0,0])
        merged_vc = [max(incoming_vc[i], local_vc[i]) for i in range(4)]
        merged_vc[2] += 1
        self.vector_clocks[order_id] = merged_vc

        data = self.cached_orders.get(order_id)
        if not data:
            is_fraudulent = True
            reason = "No cached order data found"
        else:
            # A) Compute total_num_items
            total_num_items = sum(item.quantity for item in data.items)

            # B) billing_shipping_match
            billing = data.billingAddress
            shipping = data.shippingAddress
            match = (billing.street == shipping.street and
                     billing.city == shipping.city and
                     billing.country == shipping.country)
            billing_shipping_match = 1 if match else 0

            # C) credit_card_valid
            cc = data.creditCard
            credit_card_valid = 1 if isCreditCardValid(cc.expirationDate) else 0

            # D) name_match
            name_match = 1 if data.user.name == data.user.cardHolderName else 0

            # E) gift_wrapping
            gift_wrapping = 1 if data.giftWrapping else 0

            # F) terms_accepted
            terms_accepted = 1 if data.termsAccepted else 0

            # Now build the DataFrame with all 6 columns
            feature_cols = [
                "total_num_items",
                "billing_shipping_match",
                "credit_card_valid",
                "name_match",
                "gift_wrapping",
                "terms_accepted"
            ]
            row = {
                "total_num_items": float(total_num_items),
                "billing_shipping_match": float(billing_shipping_match),
                "credit_card_valid": float(credit_card_valid),
                "name_match": float(name_match),
                "gift_wrapping": float(gift_wrapping),
                "terms_accepted": float(terms_accepted)
            }

            df_input = pd.DataFrame([row], columns=feature_cols, dtype='float32')
            x_input = xgb.DMatrix(df_input, feature_names=feature_cols)

            # Predict
            raw_pred = self.model.predict(x_input)[0]
            is_fraudulent = (raw_pred >= 0.5)
            reason = "Suspicious order by XGBoost model" if is_fraudulent else ""

        resp = fraud_detection.FraudDetectionResponse(
            isFraudulent=is_fraudulent,
            reason=reason
        )
        resp.vectorClock.extend(merged_vc)
        return resp

    def DetectUserFraud(self, request, context):
        """ Legacy single-shot approach """
        resp = fraud_detection.FraudDetectionResponse(
            isFraudulent=False,
            reason="Legacy path not used in partial order"
        )
        return resp

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(
        FraudDetectionService(), server
    )
    port = "50051"
    server.add_insecure_port(f"[::]:" + port)
    # Start the server
    server.start()
    print(f"Fraud Detection Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

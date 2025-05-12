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

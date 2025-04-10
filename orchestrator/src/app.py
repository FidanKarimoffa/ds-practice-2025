import sys
import os
import uuid
import concurrent.futures
import time
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
import grpc

# Adjust import paths as needed (make sure these paths match your folder structure)
FILE = __file__ if "__file__" in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/fraud_detection"))
suggestions_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/suggestions"))
transaction_verification_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/transaction_verification"))
order_queue_grpc_path = os.path.abspath(os.path.join(FILE, "../../../utils/pb/bookstore/order_queue"))

# Insert paths so Python can find the generated stubs
sys.path.insert(0, fraud_detection_grpc_path)
sys.path.insert(1, suggestions_path)
sys.path.insert(2, transaction_verification_path)
sys.path.insert(3, order_queue_grpc_path)

# Import stubs and messages from each microservice
import fraud_detection_pb2 as fraud_pb
import fraud_detection_pb2_grpc as fraud_grpc
import transaction_verification_pb2 as tx_pb
import transaction_verification_pb2_grpc as tx_grpc
import suggestions_pb2 as sug_pb
import suggestions_pb2_grpc as sug_grpc
import order_queue_pb2 as oq_pb
# Note: OrderQueue stubs are generated with package "bookstore.order_queue"
from bookstore.order_queue import order_queue_pb2_grpc as oq_grpc

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#####################################################################
# HELPER: MERGE VECTOR CLOCKS
#####################################################################
def merge_vector_clocks(vc1, vc2):
    """
    Merge two vector clocks element-wise by taking the maximum of each component.
    """
    return [max(vc1[i], vc2[i]) for i in range(len(vc1))]

#####################################################################
# HELPER: BUILD ORDERDATA MESSAGES
#####################################################################
def build_tx_order_data(req_json):
    """Convert orchestrator's JSON into TransactionVerificationService's OrderData."""
    return tx_pb.OrderData(
        user=tx_pb.TransactionUser(
            name=req_json.get("user", {}).get("name", ""),
            contact=req_json.get("user", {}).get("contact", "")
        ),
        creditCard=tx_pb.TransactionCreditCard(
            number=req_json.get("creditCard", {}).get("number", ""),
            expirationDate=req_json.get("creditCard", {}).get("expirationDate", ""),
            cvv=req_json.get("creditCard", {}).get("cvv", "")
        ),
        items=[
            tx_pb.TransactionItem(name=i.get("name", ""), quantity=i.get("quantity", 0))
            for i in req_json.get("items", [])
        ],
        billingAddress=tx_pb.TransactionBillingAddress(
            street=req_json.get("billingAddress", {}).get("street", ""),
            city=req_json.get("billingAddress", {}).get("city", ""),
            country=req_json.get("billingAddress", {}).get("country", "")
        ),
        shippingAddress=tx_pb.TransactionBillingAddress(
            street=req_json.get("shippingAddress", {}).get("street", ""),
            city=req_json.get("shippingAddress", {}).get("city", ""),
            country=req_json.get("shippingAddress", {}).get("country", "")
        ),
        termsAccepted=req_json.get("termsAccepted", False)
    )

def build_fraud_order_data(req_json):
    """Convert orchestrator's JSON into FraudDetectionService's OrderData."""
    return fraud_pb.OrderData(
        user=fraud_pb.User(
            name=req_json.get("user", {}).get("name", ""),
            contact=req_json.get("user", {}).get("contact", ""),
            cardHolderName=req_json.get("user", {}).get("cardHolderName", "")
        ),
        creditCard=fraud_pb.CreditCard(
            number=req_json.get("creditCard", {}).get("number", ""),
            expirationDate=req_json.get("creditCard", {}).get("expirationDate", ""),
            cvv=req_json.get("creditCard", {}).get("cvv", "")
        ),
        items=[
            fraud_pb.OrderItem(name=i.get("name", ""), quantity=i.get("quantity", 0))
            for i in req_json.get("items", [])
        ],
        billingAddress=fraud_pb.Address(
            street=req_json.get("billingAddress", {}).get("street", ""),
            city=req_json.get("billingAddress", {}).get("city", ""),
            country=req_json.get("billingAddress", {}).get("country", "")
        ),
        shippingAddress=fraud_pb.Address(
            street=req_json.get("shippingAddress", {}).get("street", ""),
            city=req_json.get("shippingAddress", {}).get("city", ""),
            country=req_json.get("shippingAddress", {}).get("country", "")
        ),
        termsAccepted=req_json.get("termsAccepted", False),
        giftWrapping=req_json.get("giftWrapping", False),
        shippingMethod=req_json.get("shippingMethod", ""),
        userComment=req_json.get("userComment", "")
    )

def build_suggestions_order_data(req_json):
    """Convert orchestrator's JSON into SuggestionsService's OrderData."""
    return sug_pb.OrderData(
        items=[
            sug_pb.BookItem(name=i.get("name", ""), quantity=i.get("quantity", 0))
            for i in req_json.get("items", [])
        ]
    )

#####################################################################
# HELPER: PARSE SUGGESTED BOOKS FOR FRONTEND RESPONSE
#####################################################################
def parseSuggestedBooks(suggestedBooksList):
    """
    Convert repeated BookEntry messages into a JSON list for the frontend.
    """
    result = []
    for entry in suggestedBooksList:
        book_id = str(uuid.uuid4())
        result.append({
            "bookId": book_id,
            "title": entry.book_title,
            "author": entry.book_author
        })
    return result

#####################################################################
# MAIN CHECKOUT FLOW ENDPOINT
#####################################################################
@app.route("/checkout", methods=["POST"])
def checkout():
    """
    Complete Flow:
      1) Cache order in all services.
      2) Perform parallel checks: (a) CheckItemsNonEmpty and (b) CheckMandatoryFields.
      3) CheckCreditCardFormat (c).
      4) CheckUserDataFraud (d).
      5) CheckCreditCardFraud (e).
      6) GenerateSuggestions (f).
      If all pass, enqueue the order in the Order Queue service, then return "Order Approved".
    """
    try:
        # Initialize orchestrator vector clock and assign order ID.
        orchestrator_vc = [0, 0, 0, 0]
        order_id = str(uuid.uuid4())

        # Parse the incoming JSON request.
        req_data = request.get_json() if request.is_json else json.loads(request.data)
        print(f"[Orchestrator] Received request for OrderID={order_id}: {req_data}")

        # --- Connect to backend services ---
        with grpc.insecure_channel("transaction_verification:50052") as tx_channel, \
             grpc.insecure_channel("fraud_detection:50051") as fraud_channel, \
             grpc.insecure_channel("suggestions:50053") as sug_channel:

            tx_stub = tx_grpc.TransactionVerificationServiceStub(tx_channel)
            fraud_stub = fraud_grpc.FraudDetectionServiceStub(fraud_channel)
            sug_stub = sug_grpc.SuggestionsServiceStub(sug_channel)

            #######################################################
            # 1) Cache the order in each service with detailed logging.
            #######################################################
            tx_data = build_tx_order_data(req_data)
            fraud_data = build_fraud_order_data(req_data)
            sug_data = build_suggestions_order_data(req_data)

            print(f"[Orchestrator] Sending CacheOrder to Transaction Service for OrderID={order_id} with VC: {orchestrator_vc}")
            tx_resp = tx_stub.CacheOrder(tx_pb.CacheOrderRequest(orderId=order_id, vectorClock=orchestrator_vc, orderData=tx_data))
            print(f"[Orchestrator] Transaction CacheOrder Response: Updated VC: {list(tx_resp.updatedVectorClock)}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(tx_resp.updatedVectorClock))

            print(f"[Orchestrator] Sending CacheOrder to Fraud Detection Service for OrderID={order_id} with VC: {orchestrator_vc}")
            f_resp = fraud_stub.CacheOrder(fraud_pb.CacheOrderRequest(orderId=order_id, vectorClock=orchestrator_vc, orderData=fraud_data))
            print(f"[Orchestrator] Fraud CacheOrder Response: Updated VC: {list(f_resp.updatedVectorClock)}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(f_resp.updatedVectorClock))

            print(f"[Orchestrator] Sending CacheOrder to Suggestions Service for OrderID={order_id} with VC: {orchestrator_vc}")
            s_resp = sug_stub.CacheOrder(sug_pb.CacheOrderRequest(orderId=order_id, vectorClock=orchestrator_vc, orderData=sug_data))
            print(f"[Orchestrator] Suggestions CacheOrder Response: Updated VC: {list(s_resp.updatedVectorClock)}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(s_resp.updatedVectorClock))

            #######################################################
            # 2) Run (a) and (b) checks in parallel
            #######################################################
            def event_a_checkItems(vc):
                print(f"[Orchestrator] Calling CheckItemsNonEmpty for OrderID={order_id} with VC: {vc}")
                return tx_stub.CheckItemsNonEmpty(tx_pb.EventRequest(orderId=order_id, vectorClock=vc))
            
            def event_b_checkMandatory(vc):
                print(f"[Orchestrator] Calling CheckMandatoryFields for OrderID={order_id} with VC: {vc}")
                return tx_stub.CheckMandatoryFields(tx_pb.EventRequest(orderId=order_id, vectorClock=vc))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as exec_pool:
                future_a = exec_pool.submit(event_a_checkItems, orchestrator_vc)
                future_b = exec_pool.submit(event_b_checkMandatory, orchestrator_vc)
                a_result = future_a.result()
                b_result = future_b.result()
            
            print(f"[Orchestrator] Received CheckItemsNonEmpty response for OrderID={order_id}: VC: {list(a_result.vectorClock)}, verification: {a_result.verification}")
            print(f"[Orchestrator] Received CheckMandatoryFields response for OrderID={order_id}: VC: {list(b_result.vectorClock)}, verification: {b_result.verification}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(a_result.vectorClock))
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(b_result.vectorClock))
            
            if not a_result.verification:
                print(f"[Orchestrator] (a) CheckItemsNonEmpty failed for OrderID={order_id}: {a_result.errors}")
                return jsonify({"orderId": order_id, "status": "Order Rejected (items check failed)", "suggestedBooks": []})
            if not b_result.verification:
                print(f"[Orchestrator] (b) CheckMandatoryFields failed for OrderID={order_id}: {b_result.errors}")
                return jsonify({"orderId": order_id, "status": "Order Rejected (mandatory fields check failed)", "suggestedBooks": []})

            #######################################################
            # 3) CheckCreditCardFormat (c) depends on (a)
            #######################################################
            print(f"[Orchestrator] Calling CheckCreditCardFormat for OrderID={order_id} with VC: {orchestrator_vc}")
            c_result = tx_stub.CheckCreditCardFormat(tx_pb.EventRequest(orderId=order_id, vectorClock=orchestrator_vc))
            print(f"[Orchestrator] Received CheckCreditCardFormat for OrderID={order_id}: VC: {list(c_result.vectorClock)}, verification: {c_result.verification}, errors: {c_result.errors}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(c_result.vectorClock))
            if not c_result.verification:
                return jsonify({"orderId": order_id, "status": "Order Rejected (credit card format check failed)", "suggestedBooks": []})

            #######################################################
            # 4) CheckUserDataFraud (d) depends on (b)
            #######################################################
            print(f"[Orchestrator] Calling CheckUserDataFraud for OrderID={order_id} with VC: {orchestrator_vc}")
            d_result = fraud_stub.CheckUserDataFraud(fraud_pb.EventRequest(orderId=order_id, vectorClock=orchestrator_vc))
            print(f"[Orchestrator] Received CheckUserDataFraud for OrderID={order_id}: VC: {list(d_result.vectorClock)}, isFraudulent: {d_result.isFraudulent}, reason: {d_result.reason}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(d_result.vectorClock))
            if d_result.isFraudulent:
                return jsonify({"orderId": order_id, "status": "Order Rejected (user data fraud)", "suggestedBooks": []})

            #######################################################
            # 5) CheckCreditCardFraud (e) depends on (c) & (d)
            #######################################################
            print(f"[Orchestrator] Calling CheckCreditCardFraud for OrderID={order_id} with VC: {orchestrator_vc}")
            e_result = fraud_stub.CheckCreditCardFraud(fraud_pb.EventRequest(orderId=order_id, vectorClock=orchestrator_vc))
            print(f"[Orchestrator] Received CheckCreditCardFraud for OrderID={order_id}: VC: {list(e_result.vectorClock)}, isFraudulent: {e_result.isFraudulent}, reason: {e_result.reason}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(e_result.vectorClock))
            if e_result.isFraudulent:
                return jsonify({"orderId": order_id, "status": "Order Rejected (advanced credit card fraud)", "suggestedBooks": []})

            #######################################################
            # 6) GenerateSuggestions (f) depends on (e)
            #######################################################
            print(f"[Orchestrator] Calling GenerateSuggestions for OrderID={order_id} with VC: {orchestrator_vc}")
            f_result = sug_stub.GenerateSuggestions(sug_pb.GenerateSuggestionsRequest(orderId=order_id, vectorClock=orchestrator_vc))
            print(f"[Orchestrator] Received GenerateSuggestions for OrderID={order_id}: updated VC: {list(f_result.updatedVectorClock)}")
            orchestrator_vc = merge_vector_clocks(orchestrator_vc, list(f_result.updatedVectorClock))
            suggested_books_list = []
            for entry in f_result.suggestions:
                book_id = str(uuid.uuid4())
                suggested_books_list.append({
                    "bookId": book_id,
                    "title": entry.book_title,
                    "author": entry.book_author
                })

        ############################################################################
        # Enqueue the order in the Order Queue Service (if final checks succeeded)
        ############################################################################
        try:
            print(f"[Orchestrator] Calling OrderQueue Enqueue for OrderID={order_id} with final VC: {orchestrator_vc}")
            with grpc.insecure_channel("order_queue:50054") as q_channel:
                q_stub = oq_grpc.OrderQueueServiceStub(q_channel)
                shipping_country = req_data.get("shippingAddress", {}).get("country", "")
                queue_order = oq_pb.QueueOrder(
                    orderId=order_id,
                    shippingCountry=shipping_country,
                    jsonData=json.dumps(req_data)
                )
                enq_response = q_stub.Enqueue(oq_pb.EnqueueRequest(order=queue_order))
                if enq_response.success:
                    print(f"[Orchestrator] Successfully enqueued order: {order_id}")
                else:
                    print(f"[Orchestrator] Failed to enqueue order: {order_id}, reason: {enq_response.message}")
        except Exception as q_err:
            print(f"[Orchestrator] Error enqueuing order in queue for OrderID={order_id}: {q_err}")

        ############################################################################
        # Final log and response to user.
        ############################################################################
        print(f"[Orchestrator] Order Approved for OrderID={order_id}. Final VC: {orchestrator_vc}")
        return jsonify({
            "orderId": order_id,
            "status": "Order Approved",
            "suggestedBooks": suggested_books_list
        })

    except Exception as e:
        print(f"[Orchestrator] Error in checkout: {str(e)}")
        import traceback
        print(f"[Orchestrator] Traceback: {traceback.format_exc()}")
        return jsonify({
            "orderId": str(uuid.uuid4()),
            "status": "Order Failed",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

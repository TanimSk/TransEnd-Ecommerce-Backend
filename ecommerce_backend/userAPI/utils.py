import requests
import json
import uuid


# Generate Payment Link
def make_payment(cus_name, cus_email, cus_phone, amount) -> dict:
    url = "https://sandbox.aamarpay.com/jsonpost.php"
    unique_id = str(uuid.uuid4())

    payload = json.dumps(
        {
            "store_id": "aamarpaytest",
            "tran_id": unique_id,
            "success_url": f"http://127.0.0.1:8000/consumer/ordered_product/mobile?uuid={unique_id}",
            "fail_url": "http://google.com/",
            "cancel_url": "http://www.merchantdomain.com/can",
            "amount": amount,
            "currency": "BDT",
            "signature_key": "dbb74894e82415a2f7ff0ec3a97e4183",
            "desc": "Customer Payment",
            "cus_name": cus_name,
            "cus_email": cus_email,
            "cus_phone": cus_phone,
            "type": "json",
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


# Verify Payment
def verify_payment(request_id):
    url = f"https://sandbox.aamarpay.com/api/v1/trxcheck/request.php?request_id={request_id}&store_id=aamarpaytest&signature_key=dbb74894e82415a2f7ff0ec3a97e4183&type=json"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response.get("mer_txnid", "") == request_id


def send_invoice():
    ...
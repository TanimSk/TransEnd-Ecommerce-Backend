from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import requests
import json
import uuid


# Generate Payment Link
def make_payment(cus_name, cus_email, cus_phone, amount) -> dict:
    sandbox = False

    if sandbox:
        url = "https://sandbox.aamarpay.com/jsonpost.php"
        store_id = "aamarpaytest"
        signature_key = "dbb74894e82415a2f7ff0ec3a97e4183"
    else:
        url = "https://secure.aamarpay.com/jsonpost.php"
        store_id = "transendcrafts"
        signature_key = "624898df9f5121e30557689d567befa5"

    unique_id = str(uuid.uuid4())

    payload = json.dumps(
        {
            "store_id": store_id,
            "tran_id": unique_id,
            "success_url": f"https://api.transendcrafts.com/consumer/ordered_product/mobile?uuid={unique_id}&email={cus_email}",
            "fail_url": "https://transendcrafts.com/",
            "cancel_url": "https://transendcrafts.com/",
            "amount": amount,
            "currency": "BDT",
            "signature_key": signature_key,
            "desc": f"{cus_name} - {timezone.now()}",
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
    sandbox = False

    if sandbox:
        url = "https://sandbox.aamarpay.com/jsonpost.php"
        store_id = "aamarpaytest"
        signature_key = "dbb74894e82415a2f7ff0ec3a97e4183"
    else:
        url = "https://secure.aamarpay.com/jsonpost.php"
        store_id = "transendcrafts"
        signature_key = "624898df9f5121e30557689d567befa5"

    url = f"{url}/api/v1/trxcheck/request.php?request_id={request_id}&store_id={store_id}&signature_key={signature_key}&type=json"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response.get("mer_txnid", "") == request_id


def send_invoice(to_mail, context):
    subject, from_email = "Invoice From TransEnd", "noreply.service.tanimsk@gmail.com"

    html_content = render_to_string(
        "invoice_email.html", context
    )  # render with dynamic value
    text_content = strip_tags(
        html_content
    )  # Strip the html tag. So people can see the pure text at least.

    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_mail])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def get_unique_number(name) -> str:
    now_time = timezone.now()
    total_milliseconds = (
        (now_time.hour * 3600) + (now_time.minute * 60) + now_time.second
    ) * 1000
    total_milliseconds = total_milliseconds + int(now_time.microsecond // 1000)

    return f"TE{now_time.day}{now_time.month}{str(now_time.year)[2:]}-{name[:3]}{total_milliseconds}"

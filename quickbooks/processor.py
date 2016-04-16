import logging

from django.conf import settings
from cartridge.shop.checkout import CheckoutError
from quickbooks.payments import Payments

logger = logging.getLogger(__name__)

def quickbooks_payment_handler(request, order_form, order):
    p = Payments()

    if(not p.session):
        raise CheckoutError("No payment session")

    data = order_form.cleaned_data

    try:
        charge = p.charge_create({
            "amount": str(order.total),
            "currency": "USD",
            "card": {
                "expYear": data['card_expiry_year'],
                "expMonth": data['card_expiry_month'],
                "address": {
                    "region": data['billing_detail_state'],
                    "postalCode": data['billing_detail_postcode'],
                    "streetAddress": data['billing_detail_street'],
                    "country": data['billing_detail_country'],
                    "city": data['billing_detail_city']
                },
                "name": data['card_name'],
                "cvc": data['card_ccv'],
                "number": data['card_number']
            },
            "description": str(order)
        })

        if(charge['status'] == "DECLINED"):
            raise CheckoutError("The card authorization was declined")

        return charge['id']

    except:
        logger.warning("There was a problem with payment for order %s" % order,
                       exc_info=True)
        raise CheckoutError("There was a problem with payment")

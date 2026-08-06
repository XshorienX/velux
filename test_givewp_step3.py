import requests
import json
import uuid
import random
import string
import urllib.parse

# using the output from step 2 for testing, but wait I need a valid card
# we will just use a generic card format, it will fail but we'll see the response
# Let's write the whole function to see the error structure

def test_stripe_confirm():
    session = requests.Session()
    # Step 0
    res0 = session.get("https://changesbristol.org.uk/?givewp-route=donation-form-view&form-id=100546")
    import re
    match = re.search(r'window\.givewpDonationFormExports = ({.*?});', res0.text)
    exports = json.loads(match.group(1))
    donate_url = exports["donateUrl"]

    # Step 1
    sid = "elements_session_" + "".join(random.choices(string.ascii_letters + string.digits, k=11))
    guid = str(uuid.uuid4())
    params = {
        "deferred_intent[mode]": "payment",
        "deferred_intent[amount]": "500",
        "deferred_intent[currency]": "gbp",
        "key": "pk_live_SMtnnvlq4TpJelMdklNha8iD",
        "_stripe_account": "acct_1IyaXDFXkg2oad08",
        "elements_init_source": "stripe.elements",
        "referrer_host": "changesbristol.org.uk",
        "session_id": sid,
        "stripe_js_id": guid,
        "top_level_referrer_host": "changesbristol.org.uk",
        "locale": "en-US",
        "type": "deferred_intent"
    }
    session.get("https://api.stripe.com/v1/elements/sessions", params=params)

    # Step 2
    multipart_data = {
        "amount": (None, "5"),
        "currency": (None, "GBP"),
        "levelId": (None, "custom"),
        "donationType": (None, "single"),
        "fundId[value]": (None, "1"),
        "fundId[label]": (None, "General"),
        "fundId[checked]": (None, "true"),
        "fundId[isDefault]": (None, "true"),
        "formId": (None, "100546"),
        "gatewayId": (None, "stripe_payment_element"),
        "giftAid[firstName]": (None, ""),
        "giftAid[lastName]": (None, ""),
        "giftAid[address]": (None, ""),
        "giftAid[postcode]": (None, ""),
        "giftAid[country]": (None, "GB"),
        "giftAid[optIn]": (None, "false"),
        "firstName": (None, "John"),
        "lastName": (None, "Doe"),
        "email": (None, "johndoe12312312@gmail.com"),
        "mailchimp": (None, "false"),
        "donationBirthday": (None, ""),
        "originUrl": (None, "https://changesbristol.org.uk/donations/one-off-donation-v2/"),
        "isEmbed": (None, "true"),
        "embedId": (None, "100546"),
        "locale": (None, "en_GB"),
        "gatewayData[stripePaymentMethod]": (None, "card"),
        "gatewayData[stripePaymentMethodIsCreditCard]": (None, "true"),
        "gatewayData[formId]": (None, "100546"),
        "gatewayData[stripeKey]": (None, "pk_live_SMtnnvlq4TpJelMdklNha8iD"),
        "gatewayData[stripeConnectedAccountId]": (None, "acct_1IyaXDFXkg2oad08")
    }
    res2 = session.post(donate_url, files=multipart_data)
    data2 = res2.json()
    client_secret = data2["data"]["clientSecret"]
    return_url = data2["data"]["returnUrl"]
    pi = client_secret.split("_secret_")[0]

    # Step 3
    confirm_url = f"https://api.stripe.com/v1/payment_intents/{pi}/confirm"
    payload = {
        "return_url": return_url,
        "payment_method_data[billing_details][name]": "John Doe",
        "payment_method_data[billing_details][email]": "johndoe12312312@gmail.com",
        "payment_method_data[billing_details][address][country]": "GB",
        "payment_method_data[type]": "card",
        "payment_method_data[card][number]": "4111111111111111",
        "payment_method_data[card][cvc]": "123",
        "payment_method_data[card][exp_year]": "25",
        "payment_method_data[card][exp_month]": "12",
        "payment_method_data[allow_redisplay]": "unspecified",
        "payment_method_data[payment_user_agent]": "stripe.js/b01c5e72b9; stripe-js-v3/b01c5e72b9; payment-element; deferred-intent; autopm",
        "payment_method_data[referrer]": "https://changesbristol.org.uk",
        "payment_method_data[time_on_page]": "52795",
        "payment_method_data[client_attribution_metadata][client_session_id]": guid,
        "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
        "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
        "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
        "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "deferred",
        "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
        "payment_method_data[client_attribution_metadata][elements_session_id]": sid,
        "payment_method_data[guid]": guid,
        "payment_method_data[muid]": str(uuid.uuid4()),
        "payment_method_data[sid]": str(uuid.uuid4()),
        "expected_payment_method_type": "card",
        "client_context[currency]": "gbp",
        "client_context[mode]": "payment",
        "use_stripe_sdk": "true",
        "key": "pk_live_SMtnnvlq4TpJelMdklNha8iD",
        "_stripe_account": "acct_1IyaXDFXkg2oad08",
        "client_secret": client_secret
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/"
    }

    res3 = session.post(confirm_url, data=payload, headers=headers)
    print(res3.status_code)
    print(res3.text)

test_stripe_confirm()

import requests
import uuid
import random
import string

sid = "elements_session_" + "".join(random.choices(string.ascii_letters + string.digits, k=11))
guid = str(uuid.uuid4())

url = "https://api.stripe.com/v1/elements/sessions"
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

res = requests.get(url, params=params)
print(res.status_code)
print(res.text[:300])

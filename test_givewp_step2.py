import requests
import re
import json

session = requests.Session()
# Step 0: Get the route
res0 = session.get("https://changesbristol.org.uk/?givewp-route=donation-form-view&form-id=100546")
match = re.search(r'window\.givewpDonationFormExports = ({.*?});', res0.text)
if not match:
    print("Export not found")
    exit(1)
exports = json.loads(match.group(1))
donate_url = exports["donateUrl"]
print("Donate URL:", donate_url)

# Step 2: POST to donate URL
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
print("Step 2 status:", res2.status_code)
print(res2.text[:500])

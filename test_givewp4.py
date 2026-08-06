import requests

res = requests.get("https://changesbristol.org.uk/?givewp-route=donation-form-view&form-id=100546")
for line in res.text.split('\n'):
    if "givewp-route-signature" in line:
        print(line.strip())

import requests

res = requests.get("https://changesbristol.org.uk/donations/one-off-donation-v2/")
for line in res.text.split('\n'):
    if "root-data-givewp-embed" in line:
        print(line.strip())

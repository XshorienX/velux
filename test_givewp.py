import requests
from bs4 import BeautifulSoup
import re

res = requests.get("https://changesbristol.org.uk/donations/one-off-donation-v2/")
print(res.status_code)
# look for givewp-route-signature
matches = re.findall(r'givewp-route-signature=([a-f0-9]+)', res.text)
print("Signatures:", set(matches))

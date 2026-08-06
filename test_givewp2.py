import requests

res = requests.get("https://changesbristol.org.uk/donations/one-off-donation-v2/")
print("givewp" in res.text.lower())
import re
# Print all givewp occurrences
for line in res.text.split('\n'):
    if "givewp" in line.lower():
        print(line.strip()[:100])

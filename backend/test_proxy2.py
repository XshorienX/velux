import requests
import urllib3
urllib3.disable_warnings()

def test_requests_proxy():
    raw = "gw.proxyrise.com:443:res-any:pgw-9d22cd6f11d92f6078ba05a0b8b2b845e16e9f980d24bedd"
    parts = raw.split(":")
    proxy_url = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    print("Testing proxy:", proxy_url)
    proxies = {"http": proxy_url, "https": proxy_url}
    
    try:
        res = requests.get("https://api.stripe.com/healthcheck", proxies=proxies, timeout=10, verify=False)
        print("Stripe:", res.status_code)
    except Exception as e:
        print("Stripe Error:", e)

    try:
        res = requests.get("https://shopify.com", proxies=proxies, timeout=10, verify=False)
        print("Shopify:", res.status_code)
    except Exception as e:
        print("Shopify Error:", e)

if __name__ == "__main__":
    test_requests_proxy()
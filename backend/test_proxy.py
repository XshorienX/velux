import httpx
import asyncio

async def test_proxy():
    proxy_url = "http://res-any:pgw-9d22cd6f11d92f6078ba05a0b8b2b845e16e9f980d24bedd@gw.proxyrise.com:443"
    print(f"Testing {proxy_url}")
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=15.0, verify=False) as client:
            res_stripe = await client.get("https://api.stripe.com/healthcheck", follow_redirects=True)
            print("Stripe status:", res_stripe.status_code)
            res_shopify = await client.get("https://checkout.shopify.com", follow_redirects=True)
            print("Shopify status:", res_shopify.status_code)
    except Exception as e:
        print("Error:", type(e), e)

asyncio.run(test_proxy())
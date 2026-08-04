import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
import httpx
import asyncio

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
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Indexes
    await db.users.create_index("username", unique=True)
    await db.login_attempts.create_index("identifier")
    
    # Admin seeding
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
            "credits": 999999,
            "limits": "unlimited",
            "created_at": datetime.now(timezone.utc)
        })
    elif not verify_password(admin_pass, existing["password_hash"]):
        await db.users.update_one(
            {"username": admin_user}, 
            {"$set": {"password_hash": hashed}}
        )

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

# Auth Helpers
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

# Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    credits: int = 0
    limits: str = "standard"

class UserUpdate(BaseModel):
    status: Optional[str] = None
    credits: Optional[int] = None
    limits: Optional[str] = None
    password: Optional[str] = None
    telegram_id: Optional[str] = None
    shopify_urls: Optional[str] = None
    total_checked_ccs: Optional[int] = None
@app.patch("/api/auth/me")
async def update_me(req: UserUpdate, user: dict = Depends(get_current_user)):
    update_data = {}
    if req.password is not None and req.password.strip():
        update_data["password_hash"] = hash_password(req.password)
    if req.telegram_id is not None:
        update_data["telegram_id"] = req.telegram_id
    if req.shopify_urls is not None:
        update_data["shopify_urls"] = req.shopify_urls
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"_id": ObjectId(user["_id"])}, {"password_hash": 0})
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
    return updated_user


class ProxyCheckRequest(BaseModel):
    proxies: str

# Routes
@app.post("/api/auth/login")
async def login(req: LoginRequest, request: Request, response: Response):
    ip = request.client.host
    identifier = f"{ip}:{req.username}"
    
    # Check rate limit
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
    
    user["_id"] = str(user["_id"])
    user.pop("password_hash", None)
    return {"message": "Logged in successfully", "user": user}

@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("refresh_token", path="/", secure=True, httponly=True, samesite="none")
    return {"message": "Logged out successfully"}

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
        "credits": req.credits,
        "limits": req.limits,
        "created_at": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)
    new_user.pop("password_hash", None)
    return new_user

@app.patch("/api/admin/users/{user_id}")
async def update_user(user_id: str, req: UserUpdate, admin: dict = Depends(require_admin)):
    update_data = {}
    if req.status is not None:
        update_data["status"] = req.status
    if req.credits is not None:
        update_data["credits"] = req.credits
    if req.limits is not None:
        update_data["limits"] = req.limits
    if req.password is not None and req.password.strip():
        update_data["password_hash"] = hash_password(req.password)
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
    return updated_user

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    if user_id == str(admin["_id"]):
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted"}

# Proxy Routes
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
    # Sometimes users paste with weird line breaks like \n:, so let's normalize \n: to :
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
            
        try:
            async with httpx.AsyncClient(proxy=proxy_url, timeout=10.0, verify=False) as client:
                res_stripe = await client.get("https://api.stripe.com/healthcheck", follow_redirects=True)
                res_shopify = await client.get("https://shopify.com", follow_redirects=True)
                
                if res_stripe.status_code and res_shopify.status_code:
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
        except Exception as e:
            print(f"Proxy failed: {raw_proxy} Error: {str(e)}")
            pass
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

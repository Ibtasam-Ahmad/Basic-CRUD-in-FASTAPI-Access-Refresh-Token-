from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

# ========== FAKE DB ==========
fake_users_db = {}
fake_data_store = {}

# ========== CONFIG ==========
SECRET_KEY = "your_secret_key"
REFRESH_SECRET_KEY = "your_refresh_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # Fixed path

# ========== SCHEMAS ==========
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Item(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

# ========== UTILS ==========
def create_token(data: dict, expires_delta: timedelta, secret_key: str):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

def create_access_token(username: str):
    return create_token(
        {"sub": username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        SECRET_KEY
    )

def create_refresh_token(username: str):
    return create_token(
        {"sub": username},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        REFRESH_SECRET_KEY
    )

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ========== AUTH ROUTES ==========
@app.post("/signup")
def signup(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    fake_users_db[user.username] = {
        "username": user.username,
        "password": get_password_hash(user.password)
    }
    return {"msg": "User created"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    access_token = create_access_token(form_data.username)
    refresh_token = create_refresh_token(form_data.username)

    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/refresh", response_model=Token)
def refresh(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        return Token(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username)
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

# ========== PROTECTED CRUD ==========
@app.post("/items/", response_model=Item)
def create_item(item: Item, username: str = Depends(get_current_user)):
    item.id = str(uuid4())
    fake_data_store[item.id] = item.dict()
    return item

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str, username: str = Depends(get_current_user)):
    item = fake_data_store.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, item: Item, username: str = Depends(get_current_user)):
    if item_id not in fake_data_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item.id = item_id
    fake_data_store[item_id] = item.dict()
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: str, username: str = Depends(get_current_user)):
    if item_id not in fake_data_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del fake_data_store[item_id]
    return {"msg": "Item deleted"}


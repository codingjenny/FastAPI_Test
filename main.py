from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from jwt import PyJWTError
import zipfile
import io
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "You are a FastAPI genius!"}

# 常量和配置
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 數據存儲
users = []
upload_records = []

# 密碼上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模型定義
class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

class UploadRecord(BaseModel):
    filename: str
    upload_time: datetime
    user: str
    status: str

# 身份驗證函數
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except PyJWTError:
        raise credentials_exception

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = next((u for u in users if u["username"] == username), None)
    if not user or not pwd_context.verify(password, user["password"]):
        return None
    return User(username=user["username"], password=password)

# 用戶註冊
@app.post("/register", response_model=UserResponse)
async def register(user: User):
    hashed_password = get_password_hash(user.password)
    user_record = {"username": user.username, "password": hashed_password}
    users.append(user_record)
    return UserResponse(username=user.username)

# 用戶登錄，取得token
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

# 上傳文件
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

    try:
        zip_contents = await file.read()
        with zipfile.ZipFile(io.BytesIO(zip_contents)) as zip_file:
            zip_name = os.path.splitext(file.filename)[0]
            required_files = {f'{zip_name}/A.txt', f'{zip_name}/B.txt'}
            
            if not required_files.issubset(set(zip_file.namelist())):
                raise HTTPException(status_code=400, detail="ZIP must contain A.txt and B.txt")

        status = "Success"
        message = "File uploaded successfully"
    except HTTPException as he:
        status = f"Failed: {he.detail}"
        raise
    except Exception:
        status = "Failed: Unexpected error"
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        record = UploadRecord(
            filename=file.filename,
            upload_time=datetime.utcnow(),
            user=current_user.username,
            status=status
        )
        upload_records.append(record)

    return {"filename": file.filename, "status": status, "message": message}

# 獲取上傳記錄  
@app.get("/upload-records/", response_model=List[UploadRecord])
async def get_upload_records(user: str, current_user: User = Depends(get_current_user)):
    user_records = [record for record in upload_records if record.user == user]
    if not user_records:
        raise HTTPException(status_code=404, detail="No records found for the user")
    return user_records

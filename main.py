from fastapi import FastAPI, UploadFile, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from jwt import PyJWTError
import zipfile
import io
import os
import branch.models as models, branch.schemas as schemas, branch.database as database
from branch.database import engine, get_db
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()

# 創建資料表
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "You are a FastAPI genius!"}

# 常量和配置
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密碼上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        return schemas.TokenData(username=username)
    except PyJWTError:
        raise credentials_exception

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 修改用戶驗證
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.UserName == username).first()
    if not user or not verify_password(password, user.Password):
        return None
    return user

# 修改用戶註冊
@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(UserName=user.username, Password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserResponse(idUser=db_user.idUser, username=db_user.UserName)

# 修改用戶登錄
@app.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.UserName})
    return schemas.Token(access_token=access_token, token_type="bearer")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.UserName == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# 上傳文件
@app.post("/uploadfile/", response_model=schemas.UploadFileResponse)
async def create_upload_file(file: UploadFile, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        upload_time = datetime.utcnow()
        
        record = models.UploadFile(
            FileName=file.filename,
            UploadTime=upload_time,
            idUser=current_user.idUser,
            Status=status,
            ZipFile=zip_contents
        )
        db.add(record)
        db.commit()
        db.refresh(record)

    except HTTPException as he:
        status = f"Failed: {he.detail}"
        raise
    except Exception as e:
        status = "Failed: Unexpected error"
        print(f"Error: {str(e)}")  # 打印詳細錯誤信息
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    return schemas.UploadFileResponse(
        idUploadFile=record.idUploadFile,
        filename=record.FileName,
        upload_time=record.UploadTime,
        status=record.Status
    )

# 獲取上傳記錄  
@app.get("/uploadrecords/", response_model=List[schemas.UploadFileResponse])
async def get_upload_files(
    username: Optional[str] = Query(None, description="Username to filter records"),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if username:
        user = db.query(models.User).filter(models.User.UserName == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if current_user.UserName != username: 
            raise HTTPException(status_code=403, detail="Not authorized to view other user's records")
        
        upload_files = db.query(models.UploadFile).filter(models.UploadFile.idUser == user.idUser).all()
    else:
        upload_files = db.query(models.UploadFile).filter(models.UploadFile.idUser == current_user.idUser).all()

    if not upload_files:
        raise HTTPException(status_code=404, detail="No upload files found for the user")
    
    return [
        schemas.UploadFileResponse(
            idUploadFile=file.idUploadFile,
            filename=file.FileName,
            upload_time=file.UploadTime,
            status=file.Status
        ) for file in upload_files
    ]

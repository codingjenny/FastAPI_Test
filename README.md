# FastAPI_Test
## 1. 取得程式碼的檔案夾（語法適用Linux或MacOS）
```bash
git clone https://github.com/codingjenny/FastAPI_Test.git
```
## 2. 進入檔案夾
```bash
cd FastAPI_Test
```
## 3. 使用 Dockerfile 構建 Docker Image
```bash
docker build -t fastapi-test .
```

## 4. 運行 Docker 容器，將 8000 端口映射到本地
```bash
docker run -d -p 8000:8000 fastapi-test
```
## 5. 打開瀏覽器或使用 curl 訪問 FastAPI 的根路徑，若是看到"You are a FastAPI genius!”代表服務正在運行。
瀏覽器：http://localhost:8000/
```bash
curl http://localhost:8000/
```

## 6. 測試API

### 註冊一個新使用者
```bash 
curl -i -X 'POST' \
  'http://localhost:8000/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "password": "testpassword"
}'
```

### 登錄並獲取 token
```bash
curl -i -X 'POST' \
  'http://localhost:8000/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser&password=testpassword'
```

### 使用獲取的 token 上傳文件（將 <token> 替換為實際的 access_token）
```bash
curl -I -X 'POST' \
  'http://localhost:8000/uploadfile/' \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@/path/to/your/file.zip'
```

### 獲取上傳記錄，查詢特定使用者的上傳記錄（將 <token> 替換為實際的 access_token）
```bash
curl -I -X 'GET' \
  'http://localhost:8000/upload-records/?user=testuser' \
  -H 'Authorization: Bearer <token>'
```

## 7. 進行測試
### 在檔案夾所在位置打開終端機，輸入pytest，可進行測試
```bash
pytest
``` 
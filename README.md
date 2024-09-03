# FastAPI_Test
# 1. 取得程式碼的檔案夾（語法適用Linux或MacOS）
git clone <URL>

# 2. 進入檔案夾
cd <文件夾>

# 3. 使用 Dockerfile 構建 Docker Image
docker build -t my-fastapi-app .

# 4. 運行 Docker 容器，將 8000 端口映射到本地
docker run -d -p 8000:8000 my-fastapi-app

# 5. 打開瀏覽器或使用 curl 訪問 FastAPI 的根路徑，若是看到"You are a FastAPI genius!”代表服務正在運行。
瀏覽器：http://localhost:8000/


# 6. 可以測試看看API

# 註冊一個新使用者
curl -i -X 'POST' \
  'http://localhost:8000/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "password": "testpassword"
}'

# 登錄並獲取 token
curl -i -X 'POST' \
  'http://localhost:8000/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser&password=testpassword'

# 使用獲取的 token 上傳文件（將 <token> 替換為實際的 access_token）
curl -I -X 'POST' \
  'http://localhost:8000/uploadfile/' \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@/path/to/your/file.zip'

# 獲取上傳記錄，查詢特定使用者的上傳記錄（將 <token> 替換為實際的 access_token）
curl -I -X 'GET' \
  'http://localhost:8000/upload-records/?user=testuser' \
  -H 'Authorization: Bearer <token>'
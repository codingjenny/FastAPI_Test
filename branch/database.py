import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 資料庫連接配置（連接到現有的資料庫）
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root@localhost/mydb"

# 創建資料庫引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 創建會話
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基礎類，用於 ORM 模型
Base = sqlalchemy.orm.declarative_base()

# 建立與資料庫連接的上下文管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 新增測試連接函數
def test_connection():
    try:
        # 嘗試建立連接
        with engine.connect() as connection:
            # 執行一個簡單的 SQL 查詢
            connection.execute(sqlalchemy.text("SELECT 1"))
            print("成功連接到資料庫！")
            return True
    except Exception as e:
        print(f"連接失敗：{str(e)}")
        return False

# 如果直接運行此檔案，則執行測試
if __name__ == "__main__":
    test_connection()

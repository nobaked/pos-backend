from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings  # settings を使用

# SSL接続用のconnect_argsを準備
connect_args = {}

# DATABASE_URLにssl=trueが含まれている場合、SSL設定を追加
if "ssl=true" in settings.DATABASE_URL or "ssl_disabled=false" in settings.DATABASE_URL:
    # PyMySQLの場合、connect_argsでSSLを指定
    connect_args = {
        "ssl": {
            "check_hostname": False,
            "verify_mode": False
        }
    }

# SQLAlchemyエンジンを作成
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,      # 接続の健全性チェック
    pool_recycle=3600,       # 1時間ごとに接続をリサイクル
    echo=settings.DEBUG      # DEBUGモードでSQLログ出力
)

# セッションファクトリーを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義用のベースクラス
Base = declarative_base()

# データベースセッションの依存性
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

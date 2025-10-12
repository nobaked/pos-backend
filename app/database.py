from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings  # settings を使用

# SQLAlchemyエンジンを作成
engine = create_engine(
    settings.DATABASE_URL,
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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import pos
from app.database import Base, engine
from app.config import CORS_ORIGINS, ENV, DEBUG
from app.middleware.health import HealthMetricsMiddleware
from app.middleware.error import ErrorHandlerMiddleware
import logging
from datetime import datetime


# ロギング設定
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# FastAPIアプリケーションの作成
app = FastAPI(
    title="POS System API",
    description="POSシステムのバックエンドAPI",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,  # 本番環境ではDocsを非公開
    redoc_url="/redoc" if DEBUG else None
)


# ============================================
# ミドルウェア設定（順番が重要）
# ============================================


# 1. CORS設定（最初に設定）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"✅ CORS middleware enabled: {CORS_ORIGINS}")


# 2. エラーハンドリングミドルウェア（本番環境対応）
app.add_middleware(ErrorHandlerMiddleware)
logger.info("✅ Error handler middleware enabled")


# 3. ヘルスチェックミドルウェア（開発環境のみ）
if DEBUG:
    app.add_middleware(HealthMetricsMiddleware)
    logger.info("✅ Health metrics middleware enabled (debug mode)")


# ============================================
# アプリケーションイベント
# ============================================


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("=" * 50)
    logger.info("POS System API Starting...")
    logger.info(f"Environment: {ENV}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info("=" * 50)
    
    # 開発環境のみテーブル作成を試みる
    if ENV == "development":
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified successfully")
        except Exception as e:
            logger.warning(f"⚠️  Database connection failed: {e}")
            logger.info("Continuing without database (API documentation still available)")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("🛑 POS System API Shutting down...")


# ============================================
# グローバルエラーハンドラ（FastAPIレベル）
# ============================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    予期しないエラーをキャッチして適切に処理
    ミドルウェアで処理されなかったエラーのフォールバック
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if ENV.lower() == "production":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "内部サーバーエラーが発生しました",
                "timestamp": datetime.now().isoformat()
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "内部サーバーエラーが発生しました",
                "error": str(exc),
                "path": str(request.url),
                "timestamp": datetime.now().isoformat()
            }
        )


# ============================================
# ルーター登録
# ============================================


app.include_router(pos.router)


# ============================================
# エンドポイント
# ============================================


@app.get("/")
async def read_root():
    """APIのルートエンドポイント"""
    return {
        "message": "Welcome to the POS System API!",
        "version": "1.0.0",
        "environment": ENV,
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "health_detailed": "/health/detailed" if DEBUG else "disabled",
            "docs": "/docs" if DEBUG else "disabled",
            "products_search": "/api/products/search/{barcode}",
            "products_list": "/api/products",
            "purchase": "/api/purchase"
        }
    }


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    Azure App ServiceやKubernetesの監視に使用
    """
    try:
        # データベース接続チェック（簡易版）
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENV,
        "debug": DEBUG,
        "database": db_status,
        "version": "1.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """詳細なヘルスチェック（デバッグ用）"""
    if not DEBUG:
        return {"detail": "This endpoint is only available in debug mode"}
    
    import sys
    import platform
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENV,
        "debug": DEBUG,
        "cors_origins": CORS_ORIGINS,
        "python_version": sys.version,
        "platform": platform.platform(),
        "fastapi_version": "0.115.5"
    }

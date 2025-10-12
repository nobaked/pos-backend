"""
本番環境用エラーハンドリングミドルウェア
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import ENV
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    本番環境でエラー詳細を隠すミドルウェア
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            
            # 本番環境ではエラー詳細を隠す
            if ENV.lower() == "production":
                return JSONResponse(
                    status_code=500,
                    content={"message": "Internal server error"}
                )
            else:
                # 開発環境では詳細を返す
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": "Internal server error",
                        "detail": str(e),
                        "type": type(e).__name__
                    }
                )

"""
ヘルスチェックとパフォーマンス監視用ミドルウェア
リクエストの処理時間を計測し、レスポンスヘッダーに追加
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class HealthMetricsMiddleware(BaseHTTPMiddleware):
    """
    リクエスト処理時間を記録するミドルウェア
    開発・デバッグ時のパフォーマンス分析に使用
    """
    
    async def dispatch(self, request: Request, call_next):
        # リクエスト開始時刻
        start_time = time.time()
        
        # リクエスト処理
        response = await call_next(request)
        
        # 処理時間計算（ミリ秒）
        process_time = (time.time() - start_time) * 1000
        
        # レスポンスヘッダーに処理時間を追加
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # ログ出力（遅いリクエストのみ警告）
        if process_time > 1000:  # 1秒以上
            logger.warning(
                f"⚠️  Slow request: {request.method} {request.url.path} - {process_time:.2f}ms"
            )
        else:
            logger.debug(
                f"{request.method} {request.url.path} - {process_time:.2f}ms"
            )
        
        return response

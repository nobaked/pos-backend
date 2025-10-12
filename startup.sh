#!/bin/bash

# ==============================================
# POS System Backend Startup Script
# Azure App Service / Local Development
# ==============================================

# Azure App Service は PORT 環境変数を自動設定
export PORT="${PORT:-8000}"

# ワーカー数を自動計算
# 環境変数 WORKERS_PER_CORE が設定されていればそれを使用
WORKERS_PER_CORE="${WORKERS_PER_CORE:-2}"

if command -v nproc > /dev/null 2>&1; then
    CPU_COUNT=$(nproc)
    export WORKERS=$((CPU_COUNT * WORKERS_PER_CORE + 1))
elif command -v sysctl > /dev/null 2>&1; then
    CPU_COUNT=$(sysctl -n hw.ncpu)
    export WORKERS=$((CPU_COUNT * WORKERS_PER_CORE + 1))
else
    export WORKERS=4
fi

# 最大ワーカー数の制限（メモリ保護）
MAX_WORKERS=8
if [ $WORKERS -gt $MAX_WORKERS ]; then
    export WORKERS=$MAX_WORKERS
fi

# 最小ワーカー数の保証
MIN_WORKERS=2
if [ $WORKERS -lt $MIN_WORKERS ]; then
    export WORKERS=$MIN_WORKERS
fi

echo "=========================================="
echo "POS System Backend Starting..."
echo "Port: $PORT"
echo "Workers: $WORKERS (CPU × $WORKERS_PER_CORE + 1)"
echo "Environment: ${ENV:-development}"
echo "Log Level: ${LOG_LEVEL:-INFO}"
echo "=========================================="

# Gunicorn起動
exec gunicorn app.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:$PORT" \
    --timeout 600 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --preload

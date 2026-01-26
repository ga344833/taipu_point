#!/bin/bash 
# windows 開發須將右下角點擊更變為 LF 行尾符號
set -e

echo "等待資料庫連線..."
while ! pg_isready -h postgres -U ${DB_USER:-postgres} -d ${DB_NAME:-taipu_point}; do
  echo "資料庫尚未就緒，等待中..."
  sleep 2
done

echo "資料庫連線成功！"

# 執行資料庫遷移
echo "=========================================="
echo "執行資料庫遷移..."
echo "=========================================="

# 先為 users app 建立 migration（因為 AUTH_USER_MODEL 設定）
echo "1. 建立 users app migration..."
if python manage.py makemigrations users --noinput; then
    echo "   ✓ users migration 建立成功或無變更"
else
    echo "   ⚠ users migration 建立失敗（已忽略）"
fi

# 然後為所有 app 建立 migration
echo "2. 建立所有 app migration..."
if python manage.py makemigrations --noinput; then
    echo "   ✓ 所有 app migration 建立成功或無變更"
else
    echo "   ⚠ migration 建立失敗（已忽略）"
fi

# 執行 migration
echo "3. 執行 migration..."
python manage.py migrate --noinput
echo "   ✓ Migration 執行完成"
echo "=========================================="

# 收集靜態檔案
echo "收集靜態檔案..."
python manage.py collectstatic --noinput || true

# 建立預設測試帳號
echo "建立預設測試帳號..."
python manage.py seed_data || true

# 啟動服務
echo "啟動 Django 服務..."
if [ "$DEBUG" = "true" ]; then
    echo "開發模式：使用 runserver"
    python manage.py runserver 0.0.0.0:8000
else
    echo "生產模式：使用 gunicorn"
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
fi

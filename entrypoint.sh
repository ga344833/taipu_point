#!/bin/bash

set -e

echo "等待資料庫連線..."
while ! pg_isready -h postgres -U ${DB_USER:-postgres} -d ${DB_NAME:-taipu_point}; do
  echo "資料庫尚未就緒，等待中..."
  sleep 2
done

echo "資料庫連線成功！"

# 執行資料庫遷移
echo "執行資料庫遷移..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 收集靜態檔案
echo "收集靜態檔案..."
python manage.py collectstatic --noinput || true

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

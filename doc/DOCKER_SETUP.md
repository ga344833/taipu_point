# Docker 環境架設說明

## 概述

本專案使用 Docker Compose 建立開發環境，包含以下服務：

- **point_app**: Django 主服務
- **postgres**: PostgreSQL 資料庫

## 檔案說明

### docker-compose.yml
定義了兩個服務：
- `point_app`: Django 應用服務，綁定 volume 以支援熱重載
- `postgres`: PostgreSQL 15 資料庫服務

### Dockerfile
- 基於 Python 3.11-slim
- 安裝 PostgreSQL 客戶端和依賴
- 安裝 Python 套件
- 設定工作目錄為 `/app`

### entrypoint.sh
啟動腳本，執行以下操作：
1. 等待資料庫連線就緒
2. 執行資料庫遷移
3. 收集靜態檔案
4. 根據 DEBUG 模式啟動服務（開發模式使用 runserver，生產模式使用 gunicorn）

## 使用方式

### 1. 環境變數設定

複製 `env.example` 為 `.env`：

```bash
cp env.example .env
```

編輯 `.env` 檔案，確認以下設定：

```env
# Django 設定
SECRET_KEY=your-secret-key-here
DEBUG=true
TIME_ZONE=Asia/Taipei

# 資料庫設定（Docker 環境）
DB_ENGINE=postgresql
DB_NAME=taipu_point
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
```

### 2. 啟動服務

```bash
# 建立並啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 僅查看 point_app 的日誌
docker-compose logs -f point_app
```

### 3. 執行 Django 管理命令

```bash
# 建立超級用戶
docker-compose exec point_app python manage.py createsuperuser

# 執行遷移
docker-compose exec point_app python manage.py migrate

# 進入容器 shell
docker-compose exec point_app bash

# 執行 Django shell
docker-compose exec point_app python manage.py shell
```

### 4. 停止服務

```bash
# 停止服務（保留資料）
docker-compose stop

# 停止並移除容器（保留 volume）
docker-compose down

# 停止並移除容器和 volume（清除資料）
docker-compose down -v
```

## Volume 說明

### 綁定的 Volume

1. **專案目錄** (`./:/app`): 
   - 將本地專案目錄掛載到容器內
   - 支援程式碼熱重載，修改程式碼後無需重建容器

2. **靜態檔案** (`static_volume:/app/static_collect`):
   - 持久化靜態檔案

3. **媒體檔案** (`media_volume:/app/media`):
   - 持久化上傳的媒體檔案

4. **資料庫資料** (`postgres_data:/var/lib/postgresql/data`):
   - 持久化 PostgreSQL 資料

## 開發流程

### 1. 首次啟動

```bash
# 1. 設定環境變數
cp env.example .env

# 2. 啟動服務
docker-compose up -d

# 3. 等待服務啟動完成（約 10-30 秒）

# 4. 建立超級用戶
docker-compose exec point_app python manage.py createsuperuser

# 5. 存取服務
# API: http://localhost:8000
# 文件: http://localhost:8000/api/docs/
```

### 2. 日常開發

```bash
# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f point_app

# 修改程式碼後，Django 會自動重載（開發模式）
```

### 3. 資料庫操作

```bash
# 建立遷移檔案
docker-compose exec point_app python manage.py makemigrations

# 執行遷移
docker-compose exec point_app python manage.py migrate

# 進入資料庫
docker-compose exec postgres psql -U postgres -d taipu_point
```

## 疑難排解

### 1. 容器無法啟動

```bash
# 查看詳細日誌
docker-compose logs point_app

# 檢查環境變數
docker-compose config
```

### 2. 資料庫連線失敗

- 確認 `.env` 中的資料庫設定正確
- 確認 `DB_HOST=postgres`（使用服務名稱）
- 等待資料庫完全啟動（entrypoint.sh 會自動等待）

### 3. 權限問題

```bash
# 確保 entrypoint.sh 有執行權限（Linux/Mac）
chmod +x entrypoint.sh
```

### 4. 重建容器

```bash
# 重建並啟動
docker-compose up -d --build

# 強制重建（不使用快取）
docker-compose build --no-cache
docker-compose up -d
```

## 生產環境部署

生產環境建議：

1. 設定 `DEBUG=false`
2. 使用強密碼的 `SECRET_KEY`
3. 使用環境變數管理敏感資訊
4. 設定適當的 `ALLOWED_HOSTS`
5. 使用 gunicorn 搭配 nginx 反向代理
6. 設定 SSL/TLS 憑證

## 相關指令速查

```bash
# 啟動
docker-compose up -d

# 停止
docker-compose down

# 查看日誌
docker-compose logs -f

# 重建
docker-compose up -d --build

# 執行命令
docker-compose exec point_app <command>

# 查看狀態
docker-compose ps

# 清理（移除所有容器、網路、volume）
docker-compose down -v
```

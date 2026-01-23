# Docker 環境架設 - 改動摘要

## 概述

本次改動主要完成 Docker 開發環境的架設，包含 Docker Compose 配置、依賴管理、環境變數設定等，讓專案可以在容器化環境中運行。

## 新增檔案

### 1. Docker 相關檔案
- **`docker-compose.yml`**: Docker Compose 配置檔
  - 定義 `point_app`（Django 服務）和 `postgres`（資料庫服務）
  - 設定 volume 綁定以支援熱重載
  - 配置網路和健康檢查

- **`Dockerfile`**: Docker 映像檔建置檔
  - 基於 Python 3.11-slim
  - 安裝系統依賴（PostgreSQL 客戶端、建置工具）
  - 安裝 Python 套件
  - 設定工作目錄為 `/app`

- **`entrypoint.sh`**: 容器啟動腳本
  - 等待資料庫連線就緒
  - 自動執行資料庫遷移
  - 收集靜態檔案
  - 根據 DEBUG 模式選擇啟動方式（runserver 或 gunicorn）

- **`.dockerignore`**: Docker 建置忽略檔案
  - 排除不需要的檔案，加速建置過程

### 2. 設定檔
- **`config/settings/db.py`**: 資料庫設定檔
  - 支援 PostgreSQL 和 SQLite
  - 透過環境變數 `DB_ENGINE` 切換資料庫引擎

- **`env.example`**: 環境變數範例檔
  - 包含所有必要的環境變數設定範例
  - 預設為 Docker 環境配置

### 3. 文件
- **`doc/DOCKER_SETUP.md`**: Docker 使用說明文件
- **`doc/SECRET_KEY_GUIDE.md`**: SECRET_KEY 使用說明文件

## 修改檔案

### 1. `requirements.txt`
**改動內容**：
- 將所有依賴從範圍版本（`>=`）改為固定版本（`==`）
- 修正 `drf-standardized-errors` 版本（從 `>=1.0` 改為 `==0.15.0`）
- 修正 `corsheaders` 套件名稱（從 `corsheaders` 改為 `django-cors-headers==4.0.0`）
- 新增 `psycopg2-binary==2.9.10`（PostgreSQL 驅動）
- 新增 `gunicorn==23.0.0`（生產環境伺服器）

**原因**：
- 固定版本便於維護和確保環境一致性
- 解決套件版本相容性問題

### 2. `config/settings/__init__.py`
**改動內容**：
- 新增 `from .db import *` 導入資料庫設定

### 3. `config/settings/base.py`
**改動內容**：
- 確認 `corsheaders` 在 `INSTALLED_APPS` 和 `MIDDLEWARE` 中正確配置

### 4. `docker-compose.yml`
**改動內容**：
- 移除過時的 `version: '3.8'` 屬性（Docker Compose v2 不再需要）

### 5. `README.md`
**改動內容**：
- 新增 Docker 使用說明章節
- 提供兩種啟動方式：Docker 和本地開發

## 環境變數設定

### `.env` 檔案（已建立）
```env
SECRET_KEY=y_NY_2v5*-Plmg$$mpF12abrKsLLHkKh!61)pJC6#KB7_Q3$$GbN
DEBUG=true
TIME_ZONE=Asia/Taipei
DB_ENGINE=postgresql
DB_NAME=taipu_point
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
CSRF_CHECK=false
```

**注意**：SECRET_KEY 中的 `$` 字元需要使用 `$$` 轉義，避免被 docker-compose 解析為變數。

## 解決的問題

### 1. 套件版本問題
- **問題**：`drf-standardized-errors>=1.0` 版本不存在
- **解決**：改為 `==0.15.0`（目前可用的最新版本）

### 2. corsheaders 安裝問題
- **問題**：`corsheaders==4.5.0`、`4.3.1`、`4.2.0`、`4.1.0` 等版本都找不到
- **解決**：使用完整套件名稱 `django-cors-headers==4.0.0`

### 3. SECRET_KEY 解析問題
- **問題**：SECRET_KEY 中的 `$` 字元被 docker-compose 誤解析為變數
- **解決**：使用 `$$` 轉義

### 4. docker-compose.yml 警告
- **問題**：`version: '3.8'` 屬性已過時
- **解決**：移除該屬性

## 最終的依賴版本清單

```txt
Django==4.2.16
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
PyJWT==2.9.0
drf-spectacular==0.27.2
drf-standardized-errors==0.15.0
django-filter==24.3
django-cors-headers==4.0.0
psycopg2-binary==2.9.10
python-dotenv==1.0.1
gunicorn==23.0.0
```

## 當前狀態

### ✅ 已完成
- Docker 環境建置成功
- 所有依賴套件安裝成功
- 容器正常運行
- 資料庫服務健康

### ⚠️ 待處理
- `users.User` 模型尚未建立（導致啟動時出現錯誤，但不影響 Docker 環境本身）
- 需要執行資料庫遷移（待 User 模型建立後）

## 使用方式

### 啟動服務
```bash
docker-compose up -d
```

### 查看日誌
```bash
docker-compose logs -f point_app
```

### 執行 Django 命令
```bash
docker-compose exec point_app python manage.py <command>
```

### 停止服務
```bash
docker-compose down
```

## 技術要點

1. **Volume 綁定**：`./:/app` 綁定專案目錄，支援程式碼熱重載
2. **資料持久化**：使用 Docker volume 保存資料庫、靜態檔案、媒體檔案
3. **健康檢查**：PostgreSQL 服務包含健康檢查機制
4. **自動遷移**：entrypoint.sh 自動執行資料庫遷移
5. **環境切換**：透過 DEBUG 環境變數切換開發/生產模式

## 後續建議

1. 建立 User 模型（`apps/users/models.py`）
2. 執行資料庫遷移
3. 建立超級用戶
4. 開始開發業務功能

---

**建立時間**：2026-01-22  
**狀態**：✅ Docker 環境已就緒，可開始開發



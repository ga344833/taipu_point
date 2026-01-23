# 點數兌換贈品系統 - 後端 API

## 專案簡介

本專案為點數兌換贈品平台的後端 API，使用 Django + Django REST Framework 開發。

## 專案結構

```
taipu_point/
├── config/                 # Django 設定檔
│   ├── settings/          # 設定檔分離
│   │   ├── __init__.py
│   │   ├── base.py        # 基礎設定
│   │   └── drf.py         # DRF 相關設定
│   ├── middlewares.py     # 中間件
│   ├── urls.py            # 主路由
│   ├── wsgi.py
│   └── asgi.py
├── core/                   # 核心組件
│   └── models/
│       └── base_model.py  # BaseModel（自動記錄操作者）
├── apps/                   # 業務應用模組
│   ├── users/             # 用戶管理
│   ├── products/          # 商品管理
│   ├── points/            # 點數管理
│   ├── orders/            # 訂單管理
│   └── payments/          # 支付管理（綠界整合）
├── utils/                  # 共用工具
│   ├── pagination.py      # 分頁器
│   ├── exceptions.py      # 自定義異常
│   ├── custom_exception_handler.py  # 異常處理器
│   └── views/             # View 基礎類
├── manage.py
├── requirements.txt
└── README.md
```

## 快速開始

### 方式一：使用 Docker（推薦）

#### 1. 環境變數設定

複製 `env.example` 為 `.env` 並設定相關變數：

```bash
cp env.example .env
```

編輯 `.env` 檔案，設定必要的環境變數（資料庫設定已預設為 Docker 環境）。

#### 2. 啟動服務

```bash
# 建立並啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

#### 3. 建立超級用戶

```bash
docker-compose exec point_app python manage.py createsuperuser
```

#### 4. 存取服務

- API 服務: http://localhost:8000
- API 文件: http://localhost:8000/api/docs/
- 資料庫: localhost:5432

詳細說明請參考 [Docker 環境架設文件](doc/DOCKER_SETUP.md)

### 方式二：本地開發

#### 1. 環境設定

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

#### 2. 環境變數設定

複製 `env.example` 為 `.env` 並設定相關變數：

```bash
# 本地開發使用 SQLite
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
SECRET_KEY=your-secret-key-here
DEBUG=true
TIME_ZONE=Asia/Taipei
```

#### 3. 資料庫遷移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 4. 建立超級用戶

```bash
python manage.py createsuperuser
```

#### 5. 啟動開發伺服器

```bash
python manage.py runserver
```

## API 文件

啟動伺服器後，可透過以下網址查看 API 文件：

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 技術棧

- **Django**: 4.2+
- **Django REST Framework**: 3.14+
- **JWT 認證**: djangorestframework-simplejwt
- **API 文件**: drf-spectacular
- **分頁**: 自定義分頁器
- **異常處理**: drf-standardized-errors

## 開發規範

### 模型設計

所有業務模型應繼承 `BaseModel`，自動獲得：
- `created_at`: 創建時間
- `created_by`: 創建者
- `updated_at`: 修改時間
- `updated_by`: 修改者

範例：
```python
from core.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=100)
    # 自動擁有 created_at, created_by, updated_at, updated_by
```

### View 設計

使用 `utils.views.ModelViewSet` 作為基礎類別：

```python
from utils.views import ModelViewSet

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

## 待開發功能

- [ ] 用戶認證與註冊
- [ ] 商品 CRUD
- [ ] 點數儲值與查詢
- [ ] 訂單建立與查詢
- [ ] 綠界支付整合
- [ ] 併發控制優化

## 授權

本專案為內部專案。


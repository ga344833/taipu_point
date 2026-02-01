# 點數兌換贈品系統 - 後端 API

## 專案簡介

本專案為點數兌換贈品平台的後端 API，使用 Django + Django REST Framework 開發。系統提供完整的點數管理、商品管理與兌換功能，支援店家上架商品、會員儲值點數並兌換商品。

### 主要功能

- **用戶認證**：JWT 認證機制，支援註冊、登入、Token 刷新
- **商品管理**：店家可上架、修改、查詢與下架商品
- **點數管理**：會員可儲值點數、查詢餘額與交易紀錄
- **商品兌換**：會員可使用點數兌換商品（支援多數量兌換，最多 5 個）
- **權限控制**：基於角色的權限管理（MEMBER、STORE、ADMIN）
- **併發控制**：使用資料庫事務確保資料一致性

### 角色功能&流程圖

[DrawIO 連結](https://drive.google.com/file/d/1bLPiNbW3bQsYYEzwATy0lkXqXLYCLB11/view?usp=sharing)

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
│       └── base_model.py  # BaseModel（提供時間戳記）
│   └── permissions.py     # 自定義權限類別
├── apps/                   # 業務應用模組
│   ├── users/             # 用戶管理
│   │   ├── models/        # User, UserPoints 模型
│   │   ├── serializers/   # 序列化器
│   │   ├── views/         # View 層
│   │   ├── tests/         # 單元測試
│   │   └── dev_doc/       # 開發文件
│   ├── products/           # 商品管理
│   ├── points/             # 點數管理
│   ├── orders/             # 訂單管理（預留）
│   └── payments/           # 支付管理（預留）
├── utils/                  # 共用工具
│   ├── pagination.py      # 分頁器
│   ├── exceptions.py      # 自定義異常
│   ├── custom_exception_handler.py  # 異常處理器
│   └── views/             # View 基礎類
├── doc/                    # 專案文件
│   ├── ARCHITECTURE.md    # 架構設計文件
│   ├── DEVELOPMENT_PLAN.md # 開發計劃
│   └── DOCKER_SETUP.md    # Docker 設定說明
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

#### 3. 建立測試資料（可選）

建立預設測試帳號（管理者、店家、會員）：

```bash
docker-compose exec point_app python manage.py seed_data
```

預設帳號：
- `admin / admin12345!` (ADMIN)
- `teststore / store123!` (STORE)
- `testuser / user123!` (MEMBER)

#### 4. 建立超級用戶

```bash
docker-compose exec point_app python manage.py createsuperuser
```

#### 5. 存取服務

- **API 服務**: http://localhost:8000
- **API 文件 (Swagger)**: http://localhost:8000/api/docs/
- **API 文件 (ReDoc)**: http://localhost:8000/api/redoc/
- **資料庫**: localhost:5432

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

#### 4. 建立測試資料（可選）

建立預設測試帳號：

```bash
python manage.py seed_data
```

#### 5. 建立超級用戶

```bash
python manage.py createsuperuser
```

#### 6. 啟動開發伺服器

```bash
python manage.py runserver
```

## 測試

### 執行測試

**Docker 環境**：
```bash
# 執行所有測試
docker exec point_app python manage.py test

# 執行特定 app 的測試
docker exec point_app python manage.py test apps.users.tests
docker exec point_app python manage.py test apps.products.tests
docker exec point_app python manage.py test apps.points.tests

# 執行特定測試類別
docker exec point_app python manage.py test apps.points.tests.test_point_exchange.PointExchangeTestCase

# 保留測試資料庫（用於除錯）
docker exec point_app python manage.py test --keepdb
```

**本地環境**：
```bash
# 執行所有測試
python manage.py test

# 執行特定 app 的測試
python manage.py test apps.users.tests
python manage.py test apps.products.tests
python manage.py test apps.points.tests
```

### 測試內容

- **認證測試** (`apps/users/tests/test_auth.py`)：登入、Token 刷新
- **商品權限測試** (`apps/products/tests/test_products_permissions.py`)：CRUD 權限控制
- **點數儲值測試** (`apps/points/tests/test_point_deposit.py`)：儲值功能與權限
- **點數兌換測試** (`apps/points/tests/test_point_exchange.py`)：兌換功能、併發控制

### 建立測試資料

使用 `seed_data` 指令快速建立測試帳號：

```bash
# Docker 環境
docker exec point_app python manage.py seed_data

# 本地環境
python manage.py seed_data
```

詳細說明請參考 [測試文件](doc/TESTING.md)

## API 文件與認證

### API 文件

啟動伺服器後，可透過以下網址查看 API 文件：

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

所有 API 均已添加 OpenAPI 註解，包含詳細的參數說明與回應格式。

### API 認證流程

1. **註冊帳號**：`POST /api/auth/register/`（無需認證）
2. **取得 Token**：`POST /api/auth/token/`（使用 username 和 password）
3. **使用 Token**：在請求 Header 中加入 `Authorization: Bearer <access_token>`
4. **刷新 Token**：`POST /api/auth/token/refresh/`（使用 refresh_token）

範例：
```bash
# 登入取得 Token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "user123!"}'

# 使用 Token 存取 API
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your_access_token>"
```

## 技術棧

- **Django**: 4.2.16
- **Django REST Framework**: 3.15.2
- **JWT 認證**: djangorestframework-simplejwt 5.3.1
- **API 文件**: drf-spectacular 0.27.2
- **異常處理**: drf-standardized-errors 0.15.0
- **資料庫**: PostgreSQL（生產環境）/ SQLite（開發環境）
- **分頁**: 自定義分頁器
- **過濾**: django-filter 24.3

## 架構設計決策

### 1. User 與 UserPoints 分離設計

**設計**：`User` 與 `UserPoints` 使用 OneToOne 關係分離，而非直接在 User 模型中包含點數欄位。

**原因**：
- **關注點分離**：用戶基本資訊與點數業務邏輯分離
- **擴充性**：未來可輕鬆擴充 UserPoints（如：鎖定機制、交易限額等）
- **資料完整性**：透過 Signal 自動建立，確保每個 User 都有對應的 UserPoints
- **查詢優化**：可獨立查詢與優化點數相關操作

### 2. PointTransaction 流水帳審計機制

**設計**：所有點數異動（儲值、兌換）都記錄在 `PointTransaction` 表中，包含異動前後餘額、交易類型、成功狀態。

**原因**：
- **可追溯性**：完整的交易歷史，便於對帳與審計
- **資料一致性**：使用 `transaction.atomic()` 確保餘額更新與交易紀錄同時完成
- **錯誤處理**：記錄失敗交易，便於問題排查
- **餘額驗證**：`balance_after` 欄位可用於驗證餘額計算正確性

### 3. 模組化目錄結構

**設計**：每個 app 內部採用模組化結構（`models/`, `serializers/`, `views/`, `filters/`, `tests/`, `dev_doc/`）

**原因**：
- **可維護性**：功能相關的檔案集中管理
- **可擴充性**：新增功能時結構清晰
- **團隊協作**：多人開發時減少衝突

### 4. BaseModel 簡化設計

**設計**：`BaseModel` 僅提供 `created_at` 和 `updated_at` 時間戳記，不包含 `created_by` 和 `updated_by`。

**原因**：
- **簡化實作**：避免複雜的 Middleware 與循環依賴問題
- **效能考量**：減少不必要的資料庫查詢
- **未來擴充**：如需要操作者記錄，可透過 Audit Log 機制實作

### 5. 高併發安全性處理

**設計**：使用 `transaction.atomic()` + `select_for_update()` 處理高併發場景。

**實作細節**：

1. **資料庫事務**：使用 `transaction.atomic()` 確保所有操作要麼全部成功，要麼全部失敗
2. 使用 `select_for_update()` 鎖定關鍵資源（Product、UserPoints）
3. **鎖定順序**：先鎖定 Product，再鎖定 UserPoints，避免死鎖
4. **驗證時機**：在鎖定後才進行庫存和餘額檢查，避免競態條件

**範例**（商品兌換）：
```python
with transaction.atomic():
    # 鎖定商品（先鎖定，避免死鎖）
    product = Product.objects.select_for_update().get(id=product_id)
    
    # 鎖定後檢查庫存
    if product.stock < quantity:
        return Response({"detail": "庫存不足"})
    
    # 鎖定用戶點數
    user_points = UserPoints.objects.select_for_update().get(user=request.user)
    
    # 鎖定後檢查餘額
    if user_points.balance < total_points:
        return Response({"detail": "餘額不足"})
    
    # 更新庫存和餘額（原子操作）
    product.stock -= quantity
    user_points.balance -= total_points
    product.save()
    user_points.save()
```

**效果**：
- **防止超賣**：即使多個用戶同時兌換，庫存也不會變成負數
- **防止餘額錯誤**：確保點數扣除的正確性
- **資料一致性**：庫存、餘額、交易紀錄三者保持一致

### 6. 錯誤處理統一格式

**設計**：使用 `drf-standardized-errors` + 自定義異常處理器。

**原因**：
- **一致性**：所有 API 錯誤回應格式統一
- **前端友善**：提供結構化的錯誤資訊
- **除錯便利**：保留原始錯誤資訊供後端除錯

詳細架構說明請參考 [架構設計文件](doc/ARCHITECTURE.md)

## 開發規範

### 模型設計

所有業務模型應繼承 `BaseModel`，自動獲得：
- `created_at`: 創建時間
- `updated_at`: 修改時間

範例：
```python
from core.models.base_model import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=100)
    # 自動擁有 created_at, updated_at
```

### View 設計

使用 `utils.views.ModelViewSet` 作為基礎類別：

```python
from utils.views import ModelViewSet

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### 權限設計

使用自定義權限類別控制 API 存取：

```python
from core.permissions import IsStore, IsAdmin, IsProductOwner

class ProductViewSet(ModelViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsStore()]
        elif self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsProductOwner()]
        return [AllowAny()]
```

## 主要 API 端點

### 認證相關
- `POST /api/auth/register/` - 使用者註冊
- `POST /api/auth/token/` - 取得 JWT Token
- `POST /api/auth/token/refresh/` - 刷新 Token
- `POST /api/auth/token/verify/` - 驗證 Token

### 用戶相關
- `GET /api/users/me/` - 查詢當前登入用戶個人資料（含點數餘額）

### 商品相關
- `GET /api/products/` - 查詢商品列表（不需登入）
- `GET /api/products/{id}/` - 查詢單一商品（不需登入）
- `POST /api/products/` - 建立商品（需店家權限）
- `PATCH /api/products/{id}/` - 更新商品（需商品擁有者）
- `DELETE /api/products/{id}/` - 刪除商品（軟刪除，需商品擁有者）

### 點數相關
- `POST /api/points/deposit/` - 儲值點數（需會員權限）
- `POST /api/points/exchange/` - 兌換商品（需會員權限，支援多數量）
- `GET /api/points/transactions/` - 查詢交易紀錄（MEMBER 僅能查看自己的）

## 功能清單 (Roadmap)

### 已完成功能 ✅

- ✅ **用戶認證與註冊**：JWT 認證機制，支援註冊、登入、Token 刷新與驗證
- ✅ **商品 CRUD**：完整的商品管理功能，包含軟刪除與 N+1 查詢優化（`select_related`）
- ✅ **點數儲值與異動日誌**：會員儲值功能，所有異動記錄於 `PointTransaction` 流水帳
- ✅ **高併發商品交換**：使用 `select_for_update()` 悲觀鎖確保商品不超賣，支援多數量兌換（最多 5 個）
- ✅ **自動化單元測試**：涵蓋認證、權限、儲值、兌換等核心功能，包含併發測試
- ✅ **API 文件化**：使用 drf-spectacular 自動生成 Swagger/ReDoc 文件
- ✅ **權限控制**：基於角色的權限管理（MEMBER、STORE、ADMIN）
- ✅ **用戶個人資料查詢**：查詢當前登入用戶資訊與點數餘額

### 待開發功能

#### 近期規劃
- [ ] 兌換紀錄查詢 API（會員查詢自己的兌換紀錄）
- [ ] 交換序號核銷功能（店家核銷兌換紀錄）
- [ ] 取消兌換功能（僅限 PENDING 狀態）

#### 未來擴展
- [ ] 綠界支付整合（點數儲值）
- [ ] 訂單管理系統
- [ ] 通知功能（Email、簡訊、推播）
- [ ] 管理後台功能
- [ ] 統計報表功能

## 相關文件

- [架構設計文件](doc/ARCHITECTURE.md)
- [開發計劃](doc/DEVELOPMENT_PLAN.md)
- [Docker 環境設定](doc/DOCKER_SETUP.md)
- [測試文件](doc/TESTING.md)

## 授權

本專案為內部專案。

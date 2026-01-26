# 測試說明文件

## 測試結構

```
apps/
├── users/
│   └── tests/
│       ├── __init__.py
│       └── test_auth.py          # 認證測試（登入、Token）
└── products/
    └── tests/
        ├── __init__.py
        └── test_products_permissions.py  # 商品權限測試
```

## 執行測試

### 在 Docker 容器中執行

```bash
# 執行所有測試
docker exec point_app python manage.py test

# 執行特定 app 的測試
docker exec point_app python manage.py test apps.users.tests
docker exec point_app python manage.py test apps.products.tests

# 執行特定測試檔案
docker exec point_app python manage.py test apps.users.tests.test_auth
docker exec point_app python manage.py test apps.products.tests.test_products_permissions

# 執行特定測試方法
docker exec point_app python manage.py test apps.users.tests.test_auth.AuthTestCase.test_login_success
```

### 本地執行（需設定環境）

```bash
# 執行所有測試
python manage.py test

# 執行特定測試
python manage.py test apps.users.tests
```

## 測試內容

### 認證測試 (`test_auth.py`)

- ✅ 登入成功：正確帳密 → 200 OK，取得 access token
- ✅ 登入失敗：錯誤密碼 → 401 Unauthorized
- ✅ 登入失敗：不存在的用戶 → 401 Unauthorized
- ✅ Token 刷新：使用 refresh token 取得新的 access token

### 商品權限測試 (`test_products_permissions.py`)

- ✅ 匿名用戶可以查詢商品列表（GET /api/products/）
- ✅ 匿名用戶可以查詢單一商品（GET /api/products/{id}/）
- ✅ MEMBER 無法建立商品（POST → 403 Forbidden）
- ✅ STORE 可以建立商品（POST → 201 Created，store 自動帶入）
- ✅ STORE A 無法修改 STORE B 的商品（PATCH → 403 Forbidden）
- ✅ STORE A 可以修改自己的商品（PATCH → 200 OK）
- ✅ ADMIN 可以刪除任何商品（DELETE → 204 No Content，軟刪除）

## 測試資料庫

Django TestCase 會自動：
- 建立獨立的測試資料庫（`test_taipu_point`）
- 每個測試前執行 `setUp()` 建立測試資料
- 每個測試後執行 `tearDown()` 清理
- 所有測試結束後自動銷毀測試資料庫

## 注意事項

1. 測試使用 PostgreSQL（與開發環境一致）
2. 測試資料庫會自動建立和銷毀，不會影響開發資料庫
3. 每個測試方法都是獨立的，不會互相影響

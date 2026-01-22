# 點數兌換贈品系統 - 架構設計文件

## 一、系統概述

本系統為點數兌換贈品平台之後端 API，主要服務對象為**店家**與**會員**兩類用戶。店家可上架商品並設定兌換點數，會員可進行點數儲值並兌換商品。系統採用 Django REST Framework 開發，提供 RESTful API 介面。

## 二、技術架構

### 技術棧
- **後端框架**: Django 4.x + Django REST Framework
- **資料庫**: PostgreSQL（生產環境）/ SQLite（開發環境）
- **認證機制**: JWT (JSON Web Token)
- **第三方支付**: 綠界科技 ECPay API
- **版控**: Git

### 專案結構
```
taipu_point/
├── config/          # Django 設定檔
├── apps/
│   ├── users/       # 用戶管理模組
│   ├── products/    # 商品管理模組
│   ├── points/      # 點數管理模組
│   ├── orders/      # 訂單管理模組
│   └── payments/    # 支付模組（綠界整合）
├── requirements.txt
└── manage.py
```

## 三、資料庫設計

### 核心資料表

**User (用戶表)**
- 繼承 Django AbstractUser
- 角色區分：`MEMBER`（會員）、`MERCHANT`（店家）
- 欄位：username, email, role, is_active, date_joined

**PointAccount (點數帳戶表)**
- 關聯 User (OneToOne)
- 欄位：balance（餘額）、total_earned（累計獲得）、total_spent（累計消費）

**Product (商品表)**
- 關聯 User (ForeignKey - 店家)
- 欄位：name, description, points_required, stock, is_active, created_at

**PointTransaction (點數交易記錄表)**
- 關聯 User, PointAccount
- 欄位：transaction_type（儲值/消費/退款）、amount, balance_after, created_at

**Order (訂單表)**
- 關聯 User (會員), Product
- 欄位：order_number, product, quantity, points_cost, status, created_at

**Payment (支付記錄表)**
- 關聯 User, Order
- 欄位：payment_method, amount, ecpay_trade_no, status, created_at

## 四、API 端點設計

### 認證相關
- `POST /api/auth/register/` - 註冊（區分會員/店家）
- `POST /api/auth/login/` - 登入（回傳 JWT token）
- `POST /api/auth/refresh/` - 刷新 token

### 會員功能
- `GET /api/members/points/` - 查詢點數餘額
- `POST /api/members/points/recharge/` - 發起儲值（建立綠界訂單）
- `GET /api/members/products/` - 瀏覽商品列表
- `POST /api/members/orders/` - 建立兌換訂單
- `GET /api/members/orders/` - 查詢訂單歷史
- `GET /api/members/transactions/` - 查詢點數交易記錄

### 店家功能
- `GET /api/merchants/products/` - 查詢我的商品
- `POST /api/merchants/products/` - 上架商品
- `PUT /api/merchants/products/{id}/` - 更新商品資訊
- `DELETE /api/merchants/products/{id}/` - 下架商品
- `GET /api/merchants/orders/` - 查詢訂單（我的商品被兌換記錄）

### 支付回調
- `POST /api/payments/ecpay/callback/` - 綠界支付回調（驗證簽章、更新訂單狀態）

## 五、功能模組

### 1. 用戶認證模組 (users)
- JWT 認證機制
- 角色權限控制（使用 Django permissions）
- 註冊時自動建立點數帳戶（會員）

### 2. 商品管理模組 (products)
- CRUD 操作
- 庫存管理
- 商品上下架狀態控制

### 3. 點數管理模組 (points)
- 點數餘額查詢
- 點數交易記錄（原子性操作，使用資料庫事務）
- 點數增減 API（儲值、消費、退款）

### 4. 訂單管理模組 (orders)
- 訂單建立（檢查庫存、點數餘額）
- 訂單狀態管理（pending, completed, cancelled）
- 多用戶併發購買優化（使用 select_for_update 鎖定庫存）

### 5. 支付模組 (payments)
- 綠界 API 整合
- 儲值訂單建立
- 支付回調處理（驗證簽章、更新點數、記錄交易）

## 六、併發優化策略

### 多用戶購買情境
1. **資料庫層級鎖定**: 使用 `select_for_update()` 鎖定商品庫存與用戶點數帳戶
2. **樂觀鎖機制**: 商品表增加 `version` 欄位，更新時檢查版本號
3. **事務隔離**: 使用 `@transaction.atomic` 確保訂單建立的原子性
4. **庫存檢查**: 訂單建立前雙重驗證（API 層 + 資料庫層）

## 七、開發時程規劃

- **Day 1-2**: 專案初始化、資料庫設計、用戶認證模組
- **Day 3-4**: 商品管理、點數管理、訂單管理模組
- **Day 5-6**: 綠界支付整合、併發優化、API 測試
- **Day 7**: 文件整理、部署準備、最終測試

## 八、安全性考量

- JWT token 過期機制
- API 權限驗證（permission classes）
- 綠界回調簽章驗證
- SQL 注入防護（使用 ORM）
- 敏感資訊環境變數管理


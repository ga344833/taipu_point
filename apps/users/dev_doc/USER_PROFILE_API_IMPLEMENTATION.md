# 用戶個人資料查詢 API 實作總結

## 一、實作內容

### 功能說明
提供會員查詢個人基本資料及點數餘額的 API 端點，方便用戶在兌換商品前確認資產狀態。

### 目錄結構

```
apps/users/
├── serializers/
│   └── me_serializer.py        # MeSerializer（新增）
├── views/
│   └── me_view.py              # MeView（新增）
└── urls.py                     # URL 路由（已更新）
```

### 1. MeSerializer

**位置**：`apps/users/serializers/me_serializer.py`

**功能**：
- 序列化當前登入用戶的基本資訊和點數餘額
- 使用 `source='points.balance'` 直接取得點數餘額
- 提供 `role_display` 欄位，方便前端顯示中文角色名稱

**欄位**：
- `id`: 用戶 ID
- `username`: 帳號
- `email`: 電子郵件
- `role`: 角色（MEMBER/STORE/ADMIN）
- `role_display`: 角色顯示名稱（一般會員/店家/管理者）
- `balance`: 點數餘額
- `date_joined`: 註冊時間

### 2. MeView

**位置**：`apps/users/views/me_view.py`

**功能**：
- 使用 `RetrieveAPIView` 提供查詢功能
- 權限控制：`IsAuthenticated`（僅限已登入用戶）
- 查詢優化：使用 `select_related("points")` 避免 N+1 問題

**設計決策**：
- 採用 `RetrieveAPIView` 而非 `ViewSet`，因為目前只有單一查詢功能
- 在 `get_object()` 中使用 `select_related("points")` 確保一次查詢就取得 UserPoints 資料

### 3. URL 路由

**端點**：`GET /api/users/me/`

**權限**：需要 JWT Token 認證

## 二、API 使用方式

### 請求範例

```http
GET /api/users/me/
Authorization: Bearer <your_jwt_token>
```

### 回應範例

```json
{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com",
  "role": "MEMBER",
  "role_display": "一般會員",
  "balance": 1000,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

## 三、技術細節

### 查詢優化

使用 `select_related("points")` 確保：
- 一次查詢就取得 User 和 UserPoints 資料
- 避免 N+1 查詢問題
- 提升 API 回應速度

### 權限控制

- 僅限已登入用戶存取（`IsAuthenticated`）
- 自動回傳當前登入用戶的資料（`self.request.user`）
- 無需額外權限檢查，因為用戶只能查詢自己的資料

## 四、相關文件

- [使用者認證與註冊功能實作總結](./AUTH_IMPLEMENTATION.md)
- [UserPoints 模型實作總結](./USER_POINTS_IMPLEMENTATION.md)

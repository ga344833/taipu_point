# 點數兌換功能實作總結

## 一、實作內容

### 目錄結構

點數兌換功能擴展了 `points` app 的模組化設計：

```
apps/points/
├── models/
│   ├── __init__.py
│   ├── point_transaction_model.py    # PointTransaction 模型（已存在）
│   └── point_exchange_model.py      # PointExchange 模型（新增）
├── serializers/
│   ├── __init__.py
│   ├── point_deposit_serializer.py   # PointDepositSerializer（已存在）
│   ├── point_transaction_serializer.py  # PointTransactionSerializer（已存在）
│   └── point_exchange_serializer.py  # PointExchangeSerializer（新增）
├── views/
│   ├── __init__.py
│   ├── point_deposit_view.py         # PointDepositView（已存在）
│   ├── point_transaction_viewset.py  # PointTransactionViewSet（已存在）
│   └── point_exchange_view.py        # PointExchangeView（新增）
├── tests/
│   ├── __init__.py
│   ├── test_point_deposit.py         # 儲值功能測試（已存在）
│   └── test_point_exchange.py        # 兌換功能測試（新增）
├── urls.py                            # URL 路由（已更新）
└── apps.py
```

### 1. PointExchange 模型

**位置**：`apps/points/models/point_exchange_model.py`

**繼承**：`BaseModel`（提供 `created_at`, `updated_at` 時間戳記）

**欄位定義**：

| 欄位名稱 | 資料型態 | 說明 | 預設值 |
|---------|---------|------|--------|
| `user` | ForeignKey(User) | 兌換會員 | - |
| `product` | ForeignKey(Product) | 兌換商品 | - |
| `exchange_code` | CharField(20) | 交換序號（格式：EX + YYYYMMDD + 6位隨機碼） | - |
| `points_spent` | IntegerField | 消費點數，紀錄當時交換的點數價格 | - |
| `status` | CharField(20) | 交換狀態（PENDING=待核銷, VERIFIED=已核銷） | PENDING |

**設計決策**：

1. **交換狀態**：使用 `TextChoices`（"PENDING", "VERIFIED"）
   - 與 `PointTransaction` 的 `tx_type` 設計一致
   - 提升可讀性，便於後續擴展（如 CANCELLED）

2. **交換序號唯一性**：
   - `exchange_code` 設為 `unique=True`
   - 格式：`EX + YYYYMMDD + 6位隨機碼`（例如：`EX20260126A1B2C3`）
   - 使用 `secrets.token_hex(3).upper()` 生成隨機碼，確保安全性

3. **資料庫索引**：
   - `(user, status)`：快速查詢用戶的待核銷/已核銷紀錄
   - `(product, status)`：快速查詢商品的兌換紀錄
   - `exchange_code`：快速查詢特定交換序號
   - `status`：快速篩選不同狀態的紀錄

4. **外鍵保護**：
   - `product` 使用 `on_delete=models.PROTECT`，防止誤刪商品時遺失兌換紀錄
   - `user` 使用 `on_delete=models.CASCADE`，用戶刪除時一併刪除兌換紀錄

### 2. PointExchangeSerializer

**位置**：`apps/points/serializers/point_exchange_serializer.py`

**功能**：
- 接收 `product_id` 並驗證有效性
- 檢查商品是否存在
- 檢查商品是否上架（`is_active=True`）
- 檢查庫存是否足夠（`stock > 0`）

**設計決策**：
- 使用 `Serializer` 而非 `ModelSerializer`，因為只需要驗證輸入的 `product_id`
- 驗證邏輯放在 Serializer 中，減少 View 的複雜度
- 錯誤訊息清晰，便於前端顯示

### 3. PointExchangeView

**位置**：`apps/points/views/point_exchange_view.py`

**功能**：
- 僅限已登入的 MEMBER 存取
- 使用 `transaction.atomic()` 確保資料一致性
- 使用 `select_for_update()` 鎖定 Product 和 UserPoints，防止併發問題
- 自動生成唯一的交換序號
- 建立 `PointExchange` 和 `PointTransaction` 紀錄

**核心流程**：

1. 檢查用戶角色（必須為 MEMBER）
2. 驗證 Serializer（檢查商品有效性）
3. 在事務中執行：
   - 鎖定並取得商品（`select_for_update()`）
   - 驗證庫存
   - 鎖定並取得用戶點數（`select_for_update()`）
   - 檢查錢包是否鎖定
   - 驗證餘額是否足夠
   - 更新庫存（`product.stock -= 1`）
   - 更新餘額（`user_points.balance -= required_points`）
   - 生成交換序號（確保唯一性）
   - 建立 `PointExchange` 紀錄
   - 建立 `PointTransaction` 紀錄（`amount` 為負數，表示扣點）

**併發控制**：

1. **鎖定順序**：先鎖定 Product，再鎖定 UserPoints
   - 避免死鎖（所有交易遵循相同順序）
   - 符合業務邏輯（先確認商品，再扣點）

2. **悲觀鎖**：使用 `select_for_update()`
   - 確保高併發環境下的資料一致性
   - 防止超賣（庫存不會變成負數）
   - 防止餘額錯誤（不會出現負餘額）

3. **事務原子性**：使用 `transaction.atomic()`
   - 確保所有操作要麼全部成功，要麼全部失敗
   - 庫存、餘額、兌換紀錄、交易紀錄的一致性

**交換序號生成**：

```python
def generate_exchange_code():
    date_str = datetime.now().strftime("%Y%m%d")
    random_code = secrets.token_hex(3).upper()  # 6 位隨機碼（大寫）
    return f"EX{date_str}{random_code}"
```

- 使用 `secrets` 模組確保隨機性
- 包含日期資訊，便於查詢和排序
- 如果序號已存在（機率極低），會重新生成

### 4. URL 路由

**位置**：`apps/points/urls.py`

**新增端點**：
- `POST /api/points/exchange/` - 會員兌換商品

### 5. 測試

**位置**：`apps/points/tests/test_point_exchange.py`

**測試案例**：

1. **test_member_can_exchange_product**：基本兌換功能
   - 驗證 MEMBER 可以成功兌換商品
   - 驗證庫存和餘額正確減少
   - 驗證 `PointExchange` 和 `PointTransaction` 紀錄正確建立

2. **test_store_cannot_exchange**：權限控制
   - 驗證 STORE 無法兌換商品（回傳 403）

3. **test_insufficient_balance**：餘額不足處理
   - 驗證餘額不足時無法兌換（回傳 400）

4. **test_insufficient_stock**：庫存不足處理
   - 驗證庫存不足時無法兌換（回傳 400）

5. **test_inactive_product**：下架商品處理
   - 驗證下架商品無法兌換（回傳 400）

6. **test_concurrent_exchange_prevent_overselling**：併發測試
   - 模擬兩位會員同時兌換同一商品（庫存為 1）
   - 驗證僅有一人成功
   - 驗證庫存不會變成負數
   - 驗證只有一筆兌換紀錄

**測試注意事項**：

1. **UserPoints 餘額設定**：
   - 使用 `get_or_create` 確保 `UserPoints` 存在
   - 檢查並更新餘額，確保測試資料正確
   - 在讀取 `initial_balance` 前使用 `refresh_from_db()` 避免快取問題

2. **併發測試限制**：
   - Django 測試環境中，threading 可能不會真正模擬資料庫層級的併發
   - 此測試主要驗證邏輯正確性
   - 真正的併發測試需要在生產環境或使用更複雜的測試工具（如 locust）

## 二、API 端點

### POST /api/points/exchange/

**功能**：會員使用點數兌換商品

**權限**：`IsAuthenticated`（僅限已登入的 MEMBER）

**請求格式**：

```json
{
  "product_id": 1
}
```

**回應格式（成功）**：

```json
{
  "message": "兌換成功",
  "exchange_id": 1,
  "exchange_code": "EX20260126A1B2C3",
  "product": {
    "id": 1,
    "name": "限量商品"
  },
  "points_spent": 500,
  "balance_before": 1000,
  "balance_after": 500,
  "transaction_id": 1
}
```

**回應格式（失敗）**：

```json
{
  "detail": "點數餘額不足",
  "required": 500,
  "balance": 100
}
```

**錯誤情況**：

- `400 Bad Request`：商品不存在、已下架、庫存不足、餘額不足、錢包已鎖定
- `403 Forbidden`：非 MEMBER 角色

## 三、設計決策與技術細節

### 1. 資料一致性保證

- **事務原子性**：使用 `transaction.atomic()` 確保所有操作要麼全部成功，要麼全部失敗
- **悲觀鎖**：使用 `select_for_update()` 防止併發問題
- **鎖定順序**：先鎖定 Product，再鎖定 UserPoints，避免死鎖

### 2. 併發控制

- **防止超賣**：使用 `select_for_update()` 鎖定商品庫存，確保庫存不會變成負數
- **防止餘額錯誤**：使用 `select_for_update()` 鎖定用戶點數，確保餘額計算正確
- **鎖定範圍**：僅在事務中鎖定必要的資料，減少鎖定時間

### 3. 交換序號設計

- **唯一性**：使用 `unique=True` 確保交換序號唯一
- **可讀性**：包含日期資訊，便於查詢和排序
- **安全性**：使用 `secrets` 模組生成隨機碼，確保安全性
- **重試機制**：如果序號已存在（機率極低），會重新生成

### 4. 錯誤處理

- **驗證層級**：在 Serializer 和 View 中都有驗證，確保資料正確性
- **錯誤訊息**：提供清晰的錯誤訊息，便於前端顯示和除錯
- **狀態碼**：使用適當的 HTTP 狀態碼（400, 403）

## 四、測試結果

所有測試均通過：

```
test_concurrent_exchange_prevent_overselling ... ok
test_inactive_product ... ok
test_insufficient_balance ... ok
test_insufficient_stock ... ok
test_member_can_exchange_product ... ok
test_store_cannot_exchange ... ok

----------------------------------------------------------------------
Ran 6 tests in 1.926s

OK
```

## 五、後續擴展建議

1. **交換序號查詢 API**：
   - 提供根據 `exchange_code` 查詢兌換紀錄的 API
   - 供店家核銷時使用

2. **核銷功能**：
   - 提供 API 供店家將 `PointExchange` 的狀態從 `PENDING` 改為 `VERIFIED`
   - 需要權限控制（僅商品所屬店家可核銷）

3. **兌換紀錄查詢**：
   - 提供 `PointExchangeViewSet` 供會員查詢自己的兌換紀錄
   - 支援篩選（狀態、商品、日期範圍）

4. **取消兌換**：
   - 提供取消兌換功能（僅限 PENDING 狀態）
   - 需要退還點數並恢復庫存
   - 需要權限控制（僅兌換者本人可取消）

5. **併發測試增強**：
   - 使用更專業的測試工具（如 locust）進行壓力測試
   - 驗證在高併發環境下的效能和穩定性

6. **通知功能**：
   - 兌換成功後發送通知（Email、簡訊、推播）
   - 核銷後通知會員

## 六、相關文件

- [點數儲值功能實作總結](./POINT_DEPOSIT_IMPLEMENTATION.md)
- [測試文件](../../../doc/TESTING.md)

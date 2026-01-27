# 點數儲值功能實作總結

## 一、實作內容

### 目錄結構

採用模組化設計，將點數相關功能分離到各自的資料夾：

```
apps/points/
├── models/
│   ├── __init__.py
│   └── point_transaction_model.py    # PointTransaction 模型
├── serializers/
│   ├── __init__.py
│   ├── point_deposit_serializer.py   # PointDepositSerializer
│   └── point_transaction_serializer.py  # PointTransactionSerializer
├── views/
│   ├── __init__.py
│   ├── point_deposit_view.py         # PointDepositView
│   └── point_transaction_viewset.py  # PointTransactionViewSet
├── tests/
│   ├── __init__.py
│   └── test_point_deposit.py         # 儲值功能測試
├── urls.py                            # URL 路由
└── apps.py
```

### 1. PointTransaction 模型

**位置**：`apps/points/models/point_transaction_model.py`

**繼承**：`BaseModel`（提供 `created_at`, `updated_at` 時間戳記）

**欄位定義**：

| 欄位名稱 | 資料型態 | 說明 | 預設值 |
|---------|---------|------|--------|
| `user` | ForeignKey(User) | 所屬用戶 | - |
| `amount` | IntegerField | 異動點數（儲值為正數，兌換為負數） | - |
| `tx_type` | CharField | 交易類型（DEPOSIT=儲值, REDEMPTION=兌換） | - |
| `is_success` | BooleanField | 交易狀態（True=成功, False=失敗） | True |
| `balance_after` | IntegerField | 異動後餘額，用於後續對帳審核 | - |
| `memo` | CharField(300) | 備註 | 可選 |

**設計決策**：

1. **交易類型**：使用 `TextChoices`（"DEPOSIT", "REDEMPTION"）
   - 與 User 的 role 設計一致
   - 提升可讀性，無需記數字對應

2. **交易狀態**：使用布林值 `is_success`
   - 簡化設計，初期僅需成功/失敗兩種狀態
   - 未來如需更多狀態（如 PENDING），可改為 `TextChoices`

3. **異動後餘額**：記錄 `balance_after`
   - 用於後續對帳審核
   - 確保財務資料的可追溯性

4. **索引優化**：
   - `(user, tx_type)`：依用戶和交易類型查詢
   - `(user, created_at)`：依用戶和時間查詢交易歷史
   - `is_success`：查詢成功/失敗的交易

### 2. PointDepositSerializer

**位置**：`apps/points/serializers/point_deposit_serializer.py`

**功能**：
- 驗證儲值金額必須大於 0（`min_value=1`）
- 支援可選的 `memo` 欄位

**驗證邏輯**：
- Serializer 層：使用 `min_value=1` 參數
- 自訂 `validate_amount()` 方法進行雙重驗證

### 3. PointTransactionSerializer

**位置**：`apps/points/serializers/point_transaction_serializer.py`

**功能**：
- 用於查詢交易紀錄，包含所有交易資訊
- 提供 `tx_type_display` 欄位，顯示交易類型的中文名稱

**欄位**：
- `id`：交易紀錄 ID
- `amount`：異動點數
- `tx_type`：交易類型（DEPOSIT/REDEMPTION）
- `tx_type_display`：交易類型顯示名稱（儲值/兌換）
- `is_success`：交易狀態
- `balance_after`：異動後餘額
- `memo`：備註
- `created_at`：建立時間

### 4. PointDepositView

**位置**：`apps/points/views/point_deposit_view.py`

**功能**：
- 僅限已登入的 MEMBER 存取
- 使用 `transaction.atomic()` 確保資料一致性
- 使用 `select_for_update()` 悲觀鎖，防止競爭條件
- 檢查錢包鎖定狀態
- 自動更新餘額並建立交易紀錄

**權限控制**：
- `IsAuthenticated`：必須登入
- 角色檢查：僅允許 `role == RoleChoices.MEMBER`

**資料庫事務**：
```python
with transaction.atomic():
    # 使用 select_for_update() 鎖定 UserPoints
    user_points = UserPoints.objects.select_for_update().get(user=request.user)
    
    # 檢查錢包鎖定狀態
    if user_points.is_locked:
        return Response(...)
    
    # 更新餘額
    new_balance = user_points.balance + amount
    user_points.balance = new_balance
    user_points.save(update_fields=["balance"])
    
    # 建立交易紀錄
    PointTransaction.objects.create(...)
```

**API 端點**：
- `POST /api/points/deposit/`

**請求格式**：
```json
{
  "amount": 1000,
  "memo": "儲值備註（可選）"
}
```

**回應格式**：
```json
{
  "message": "儲值成功",
  "transaction_id": 1,
  "amount": 1000,
  "balance_before": 0,
  "balance_after": 1000
}
```

### 5. PointTransactionViewSet

**位置**：`apps/points/views/point_transaction_viewset.py`

**功能**：
- 提供交易紀錄的查詢功能（List、Retrieve）
- 支援篩選（交易類型、交易狀態）
- 支援搜尋（備註欄位）
- 支援排序（建立時間、金額）

**權限控制**：
- `IsAuthenticated`：必須登入
- **MEMBER**：僅能查看自己的交易紀錄（透過 `get_queryset()` 過濾）
- **ADMIN**：可以查看所有交易紀錄（用於對帳、異常處理等）
- **STORE**：目前不允許查看交易紀錄

**查詢過濾**：
- `tx_type`：交易類型篩選（DEPOSIT=儲值, REDEMPTION=兌換）
- `is_success`：交易狀態篩選（true=成功, false=失敗）
- 搜尋：支援在 `memo` 欄位中搜尋
- 排序：支援依 `created_at`、`amount` 排序

**API 端點**：
- `GET /api/points/transactions/` - 查詢交易紀錄列表
- `GET /api/points/transactions/{id}/` - 查詢單一交易紀錄

**請求範例**：
```
GET /api/points/transactions/?tx_type=DEPOSIT&is_success=true
GET /api/points/transactions/?search=儲值備註
GET /api/points/transactions/?ordering=-created_at
```

**回應格式**：
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "amount": 1000,
      "tx_type": "DEPOSIT",
      "tx_type_display": "儲值",
      "is_success": true,
      "balance_after": 1000,
      "memo": "儲值備註",
      "created_at": "2026-01-26T10:00:00Z"
    }
  ]
}
```

## 二、設計決策

### 1. 模型位置

**決策**：將 `PointTransaction` 放在 `apps/points/models/` 而非 `apps/users/models/`

**原因**：
- 點數相關業務邏輯集中管理
- 未來擴充（兌換、退款）更容易維護
- 符合模組化設計原則

### 2. 交易類型定義

**決策**：使用 `TextChoices` 而非 `IntegerChoices`

**原因**：
- 與 User 的 role 設計一致
- 提升可讀性，無需記數字對應
- 程式碼更直觀（`TransactionTypeChoices.DEPOSIT` vs `1`）

### 3. 交易狀態

**決策**：使用布林值 `is_success` 而非 `TextChoices`

**原因**：
- 簡化設計，初期僅需成功/失敗兩種狀態
- 未來如需更多狀態（如 PENDING, CANCELLED），可改為 `TextChoices`

### 4. 資料庫事務與鎖定

**決策**：使用 `transaction.atomic()` + `select_for_update()`

**原因**：
- **事務一致性**：確保 UserPoints 餘額更新與 PointTransaction 建立同時成功或失敗
- **防止競爭條件**：使用 `select_for_update()` 悲觀鎖，防止併發儲值時的餘額計算錯誤
- **財務資料完整性**：所有點數異動都必須有對應的交易紀錄

**技術說明**：
- `transaction.atomic()`：將多個資料庫操作包裝在一個事務中
- `select_for_update()`：在 SELECT 時鎖定資料列，直到事務結束
- 其他併發請求會等待鎖定釋放，確保資料一致性

### 5. 權限控制方式

**決策**：在 View 中直接檢查 `request.user.role`

**原因**：
- 儲值功能僅限 MEMBER，邏輯簡單
- 不需要建立額外的權限類別
- 未來如需更複雜的權限控制，可改為自訂權限類別

### 6. 交易紀錄查詢權限

**決策**：MEMBER 僅能查看自己的交易紀錄，ADMIN 可查看所有

**原因**：
- **隱私保護**：交易紀錄屬於個人財務資訊，應限制存取
- **最小權限原則**：MEMBER 只需查看自己的交易紀錄
- **管理需求**：ADMIN 需要查看所有交易紀錄進行對帳、異常處理等
- **未來擴充**：如需更細緻的權限控制（如查詢日誌），可後續加入

**實作方式**：
- 在 `get_queryset()` 中根據用戶角色過濾
- 在 `retrieve()` 中再次檢查權限（雙重保障）

## 三、技術細節

### 1. 資料庫事務流程

```
1. 開始事務 (transaction.atomic())
2. 鎖定 UserPoints (select_for_update())
3. 檢查錢包鎖定狀態
4. 計算新餘額
5. 更新 UserPoints.balance
6. 建立 PointTransaction 紀錄
7. 提交事務（或發生錯誤時回滾）
```

### 2. 競爭條件防護

**問題情境**：
- 用戶同時發起兩筆儲值請求
- 如果沒有鎖定，可能導致餘額計算錯誤

**解決方案**：
- 使用 `select_for_update()` 鎖定 UserPoints
- 第二個請求會等待第一個請求完成
- 確保餘額計算的正確性

**範例**：
```python
# 請求 1：儲值 1000
user_points = UserPoints.objects.select_for_update().get(user=user)
balance = 0 + 1000 = 1000  # 鎖定中，請求 2 等待

# 請求 2：儲值 500（等待請求 1 完成）
user_points = UserPoints.objects.select_for_update().get(user=user)
balance = 1000 + 500 = 1500  # 正確的餘額
```

### 3. 錯誤處理

- **錢包鎖定**：返回 400 Bad Request
- **非 MEMBER 角色**：返回 403 Forbidden
- **未登入**：返回 401 Unauthorized（由 `IsAuthenticated` 處理）
- **金額驗證失敗**：返回 400 Bad Request（由 Serializer 處理）

## 四、測試內容

### 單元測試 (`test_point_deposit.py`)

- ✅ MEMBER 可以儲值，餘額正確增加，且建立交易紀錄
- ✅ STORE 無法儲值，回傳 403
- ✅ 未登入用戶無法儲值，回傳 401
- ✅ 儲值金額必須大於 0
- ✅ 儲值時可以加入備註
- ✅ 多次儲值，餘額累積正確

## 五、API 端點總覽

| 端點 | Method | 權限 | 說明 |
|------|--------|------|------|
| `/api/points/deposit/` | POST | IsAuthenticated + MEMBER | 會員儲值 |
| `/api/points/transactions/` | GET | IsAuthenticated | 查詢交易紀錄列表（MEMBER 僅能查看自己的） |
| `/api/points/transactions/{id}/` | GET | IsAuthenticated | 查詢單一交易紀錄（MEMBER 僅能查看自己的） |

## 六、後續擴充建議

1. **兌換功能**：實作 `PointRedemptionView`，使用相同的交易機制
2. **餘額查詢**：實作 `UserPointsRetrieveView`，查詢用戶點數餘額
3. **交易狀態擴充**：如需更多狀態（PENDING, CANCELLED），可改為 `TextChoices`
4. **批次儲值**：支援一次儲值多筆金額
5. **儲值上限**：加入單次儲值上限和每日儲值上限
6. **管理員查詢日誌**：記錄管理員查詢交易紀錄的行為，提升隱私保護

## 七、注意事項

1. **財務資料完整性**：所有點數異動都必須記錄在 `PointTransaction` 中
2. **事務一致性**：餘額更新和交易紀錄建立必須在同一事務中完成
3. **併發控制**：使用 `select_for_update()` 防止競爭條件
4. **錢包鎖定**：儲值前必須檢查錢包是否鎖定
5. **餘額驗證**：確保餘額不會變成負數（由 UserPoints 的 `MinValueValidator(0)` 處理）
6. **隱私保護**：MEMBER 僅能查看自己的交易紀錄，防止越權存取
7. **查詢優化**：使用 `select_related("user")` 避免 N+1 查詢問題

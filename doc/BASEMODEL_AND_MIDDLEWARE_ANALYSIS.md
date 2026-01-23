# BaseModel 與 Middleware 功能分析

## 一、BaseModel 功能說明

### 功能概述

`BaseModel` 是一個抽象模型類別，提供共用的基礎欄位與自動記錄功能。

### 提供的欄位

1. **created_at** (DateTimeField)
   - 自動記錄資料建立時間
   - 使用 `auto_now_add=True`

2. **created_by** (ForeignKey to User)
   - 記錄資料建立者
   - 可為空（`null=True, blank=True`）
   - 刪除時設為 NULL（`on_delete=models.SET_NULL`）

3. **updated_at** (DateTimeField)
   - 自動記錄資料最後修改時間
   - 使用 `auto_now=True`

4. **updated_by** (ForeignKey to User)
   - 記錄資料最後修改者
   - 可為空（`null=True, blank=True`）
   - 刪除時設為 NULL（`on_delete=models.SET_NULL`）

### 自動記錄機制

`BaseModel` 覆寫了 `save()` 方法，會自動：
- 從 `CurrentUserMiddleware` 取得當前登入用戶
- 建立時：自動設定 `created_by` 為當前用戶
- 更新時：自動設定 `updated_by` 為當前用戶

### 使用場景

**適用場景**：
- 需要追蹤資料建立者與修改者的系統（如：審計需求）
- 需要記錄操作歷史的業務場景
- 多用戶協作系統

**不適用場景**：
- 簡單的業務模型，不需要追蹤操作者
- 系統自動產生的資料（如：Signal 建立的資料）
- 不需要審計追蹤的系統

### 目前專案使用狀況

**檢查結果**：目前專案中**沒有任何模型繼承 BaseModel**

---

## 二、CurrentUserMiddleware 功能說明

### 功能概述

`CurrentUserMiddleware` 是一個 Django 中間件，用於從 JWT token 中解析用戶資訊，並提供線程本地儲存。

### 主要功能

1. **JWT Token 解析**
   - 從 HTTP Header 的 `Authorization` 中取得 token
   - 支援多種格式：`Bearer <token>`、`token <token>`、`Basic <token>` 或直接 token
   - 使用 `settings.SECRET_KEY` 進行驗證

2. **用戶認證**
   - 從 token payload 中取得 `user_id`
   - 查詢資料庫取得對應的 User 物件
   - 將用戶資訊儲存在線程本地變數中

3. **線程本地儲存**
   - 使用 Python `threading.local()` 儲存當前用戶
   - 提供 `get_current_user()` 靜態方法供其他模組使用
   - 請求結束後自動清理

### 使用場景

**適用場景**：
- 需要取得當前登入用戶的場景
- BaseModel 的自動記錄功能
- 需要在非 View 層取得當前用戶的場景

**不適用場景**：
- 不使用 JWT 認證的系統
- 不需要追蹤操作者的系統
- 純 API 服務，不需要中間件處理

### 目前專案使用狀況

**檢查結果**：
- 已在 `settings/base.py` 的 `MIDDLEWARE` 中註冊
- 目前僅被 `BaseModel.save()` 方法使用
- 如果移除 BaseModel 的 save 功能，此 middleware 將不再被使用

---

## 三、是否需要保留的建議

### BaseModel 保留建議

#### 方案 A：保留 BaseModel（僅欄位，移除 save 方法）

**優點**：
- 保留時間戳記功能（`created_at`, `updated_at`）
- 未來如需追蹤操作者，可直接使用欄位
- 不影響現有功能

**缺點**：
- 保留 `created_by` 和 `updated_by` 欄位但不會自動填入
- 需要手動設定或保持為 NULL

**建議**：如果未來可能需要審計功能，建議保留欄位但移除 save 方法。

#### 方案 B：完全移除 BaseModel

**優點**：
- 程式碼更簡潔
- 不需要維護不需要的功能
- 減少依賴關係

**缺點**：
- 未來如需追蹤功能，需要重新實作
- 各模型需要自行定義時間戳記欄位

**建議**：如果確定不需要追蹤功能，建議完全移除。

### CurrentUserMiddleware 保留建議

#### 方案 A：保留 Middleware

**優點**：
- 未來如需取得當前用戶，可直接使用
- 已實作完整的 JWT 解析邏輯
- 不影響現有功能

**缺點**：
- 目前沒有被使用，增加維護成本
- 如果未來改用其他認證方式，需要修改

**建議**：如果未來可能需要取得當前用戶（如：記錄操作日誌），建議保留。

#### 方案 B：移除 Middleware

**優點**：
- 減少不必要的程式碼
- 降低維護成本

**缺點**：
- 未來如需取得當前用戶，需要重新實作

**建議**：如果確定不需要取得當前用戶的功能，建議移除。

---

## 四、建議方案

### 針對「點數兌換贈品系統」的建議

#### 1. BaseModel 處理

**建議**：**簡化 BaseModel，僅保留時間戳記欄位**

```python
class BaseModel(models.Model):
    """基本模型樣板，提供共用的時間戳記欄位"""
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="創建時間",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="修改時間",
    )
    
    class Meta:
        abstract = True
```

**理由**：
- 時間戳記是常見需求，保留可減少重複程式碼
- 移除 `created_by` 和 `updated_by`，因為不需要追蹤操作者
- 移除 `save()` 方法，簡化邏輯

#### 2. CurrentUserMiddleware 處理

**建議**：**暫時保留，但標註為「未來可能使用」**

**理由**：
- 未來實作 JWT 登入時，可能需要取得當前用戶
- 如果實作操作日誌功能，會需要此 middleware
- 目前不影響系統運作，保留成本低

**如果確定不需要**：可以移除，未來需要時再重新實作。

---

## 五、移除步驟（如果決定移除）

### 移除 BaseModel 的 save 功能

1. 修改 `core/models/base_model.py`，移除 `save()` 方法
2. 移除 `created_by` 和 `updated_by` 欄位（如果不需要）
3. 更新相關文件

### 移除 CurrentUserMiddleware

1. 從 `config/settings/base.py` 的 `MIDDLEWARE` 中移除
2. 刪除或註解 `config/middlewares.py` 中的 `CurrentUserMiddleware` 類別
3. 保留 `LogApiEndpointMiddleware`（如果還在使用）

---

## 六、總結

### 推薦方案

1. **BaseModel**：簡化為僅提供時間戳記欄位（`created_at`, `updated_at`）
2. **CurrentUserMiddleware**：暫時保留，標註為「未來可能使用」

### 決策依據

- **專案需求**：點數兌換系統不需要追蹤操作者
- **開發效率**：移除不需要的功能，減少維護成本
- **未來擴充**：保留可能需要的基礎功能（時間戳記、用戶取得）

---

**最後更新**：Day 2 開發前分析

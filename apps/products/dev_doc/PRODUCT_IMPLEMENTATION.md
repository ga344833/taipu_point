# Product 模型與 API 實作總結

## 一、實作內容

### 目錄結構

採用模組化設計，將不同功能的程式碼分離到各自的資料夾：

```
apps/products/
├── models/
│   ├── __init__.py
│   └── product_model.py          # Product 模型
├── serializers/
│   ├── __init__.py
│   └── product_serializer.py     # ProductSerializer
├── filters/
│   ├── __init__.py
│   └── product_filter.py         # ProductFilter
├── views/
│   ├── __init__.py
│   └── product_viewset.py        # ProductViewSet
├── urls.py                        # URL 路由
└── apps.py
```

### 模型設計

**位置**：`apps/products/models/product_model.py`

**繼承**：`BaseModel`（提供 `created_at`, `updated_at` 時間戳記）

**欄位定義**：

| 欄位名稱 | 資料型態 | 說明 | 預設值 |
|---------|---------|------|--------|
| `store` | ForeignKey(User) | 所屬店家 | - |
| `name` | CharField(200) | 商品名稱 | - |
| `required_points` | IntegerField | 兌換所需點數，不得為負數 | - |
| `stock` | IntegerField | 庫存數量，不得為負數 | 0 |
| `is_active` | BooleanField | 上架狀態 | True |
| `memo` | CharField(300) | 商品備註 | 可選 |

**設計決策**：
- 使用 `MinValueValidator(0)` 在 Model 層驗證不為負數
- 建立索引優化查詢：`(store, is_active)` 和 `is_active`
- `is_active` 用於軟刪除，不實際刪除資料

## 二、Serializer 實作

**位置**：`apps/products/serializers/product_serializer.py`

### 雙重驗證機制

1. **Model 層驗證**：使用 `MinValueValidator(0)`
2. **Serializer 層驗證**：
   - 使用 `min_value=0` 參數
   - 自訂 `validate_required_points()` 和 `validate_stock()` 方法

**優點**：
- 雙重保障，確保資料正確性
- Model 層驗證：防止直接操作 ORM 時輸入錯誤資料
- Serializer 層驗證：提供更清楚的錯誤訊息給 API 使用者

## 三、Filter 實作

**位置**：`apps/products/filters/product_filter.py`

**篩選欄位**：
- `store`：依店家 ID 篩選
- `is_active`：依上架狀態篩選
- `required_points_min`：最低兌換點數
- `required_points_max`：最高兌換點數

**使用方式**：
```
GET /api/products/?store=1&is_active=true&required_points_min=100&required_points_max=500
```

## 四、ViewSet 實作

**位置**：`apps/products/views/product_viewset.py`

### 功能實作

1. **CRUD 操作**：
   - List: `GET /api/products/`
   - Retrieve: `GET /api/products/{id}/`
   - Create: `POST /api/products/`
   - Update: `PATCH /api/products/{id}/`
   - Destroy: `DELETE /api/products/{id}/`（軟刪除）

2. **軟刪除實作**：
   - 覆寫 `destroy()` 方法
   - 不實際刪除資料，僅將 `is_active` 設為 `False`
   - 保留資料用於未來可能的恢復或審計需求

3. **store 自動設定**：
   - 在 `perform_create()` 中自動設定 `store = request.user`
   - 加入 TODO 註解，標註未來需加入權限檢查

### 查詢優化技術

**技術摘要**：使用 `select_related()` 避免 N+1 查詢問題

**問題說明**：
- 當查詢商品列表時，如果沒有使用 `select_related`，Django 會對每個商品都執行一次額外的查詢來取得 `store` 的資料
- 例如：查詢 10 筆商品，會執行 1 次商品查詢 + 10 次店家查詢 = 11 次查詢

**解決方案**：
```python
queryset = Product.objects.select_related("store").all()
```

**技術原理**：
- `select_related()` 使用 SQL JOIN 一次取得關聯資料
- 適用於 ForeignKey 和 OneToOneField
- 將多次查詢合併為一次，大幅提升效能

**效能提升**：
- 原本：N+1 次查詢（N 為商品數量）
- 優化後：1 次查詢（使用 JOIN）
- 當商品數量多時，效能提升非常明顯

**實作位置**：
- 在 `get_queryset()` 方法中使用 `select_related("store")`
- 確保所有查詢都自動優化

## 五、URL 路由

**位置**：`apps/products/urls.py`

**路由結構**：
- 使用 DRF 的 `DefaultRouter` 自動產生 RESTful 路由
- 註冊到 `api/products/`（採用方案 B，不建立版本化路由）

**API 端點**：
- `GET /api/products/` - 商品列表
- `POST /api/products/` - 建立商品
- `GET /api/products/{id}/` - 查詢單一商品
- `PATCH /api/products/{id}/` - 更新商品
- `DELETE /api/products/{id}/` - 軟刪除商品

## 六、API 文件化

### Swagger 整合

使用 `drf-spectacular` 的 `@extend_schema` 裝飾器：

1. **ViewSet 層級**：為整個 ViewSet 添加說明
2. **Action 層級**：為每個 action 添加詳細說明
3. **參數說明**：使用 `OpenApiParameter` 說明篩選參數

**效果**：
- 在 Swagger UI (`/api/docs/`) 中可以看到完整的 API 說明
- 包含欄位描述、參數說明、範例等

## 七、權限控制預留空間

### 目前狀態

- **Create**：開放所有登入用戶（自動設定 store）
- **Update/Delete**：開放所有登入用戶
- **List/Retrieve**：開放所有登入用戶

### 未來規劃

在程式碼中已加入 TODO 註解，標註未來需加入的權限檢查：

1. **Create 權限**：
   ```python
   # TODO: 檢查用戶是否為店家或管理者
   if self.request.user.role not in [RoleChoices.STORE, RoleChoices.ADMIN]:
       raise PermissionDenied("僅店家和管理者可建立商品")
   ```

2. **Update/Delete 權限**：
   ```python
   # TODO: 僅店家可修改/刪除自己的商品，管理者可操作任何商品
   if instance.store != request.user and request.user.role != RoleChoices.ADMIN:
       raise PermissionDenied("僅可操作自己的商品")
   ```

3. **List 權限**：
   - 未來可加入篩選邏輯，讓店家只能看到自己的商品

## 八、測試計劃（待實作）

### 單元測試項目

1. **模型驗證測試**
   - [ ] required_points 不允許負數
   - [ ] stock 不允許負數

2. **Serializer 驗證測試**
   - [ ] required_points 驗證
   - [ ] stock 驗證

3. **ViewSet 功能測試**
   - [ ] Create 商品時 store 自動設定
   - [ ] 軟刪除功能（is_active 設為 False）
   - [ ] 查詢優化（select_related）

4. **Filter 測試**
   - [ ] store 篩選
   - [ ] is_active 篩選
   - [ ] required_points 範圍篩選

### 測試檔案位置

建議建立：`apps/products/tests/test_product.py`

## 九、使用範例

### 建立商品

```python
POST /api/products/
{
    "name": "測試商品",
    "required_points": 100,
    "stock": 50,
    "memo": "這是測試商品"
}
```

### 查詢商品列表（帶篩選）

```python
GET /api/products/?store=1&is_active=true&required_points_min=100
```

### 軟刪除商品

```python
DELETE /api/products/1/
# 商品不會被實際刪除，僅 is_active 設為 False
```

---

**最後更新**：Day 2 實作完成

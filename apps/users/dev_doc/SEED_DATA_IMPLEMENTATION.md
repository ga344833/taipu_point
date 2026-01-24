# 預設資料建立功能實作總結

## 一、實作內容

### 目錄結構

採用服務層分離設計，將業務邏輯從 command 中分離：

```
apps/users/
├── services/
│   ├── __init__.py
│   └── seed_data_service.py          # 預設資料建立服務
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_data.py               # Django 管理指令
└── ...
```

### 1. 服務層設計

#### SeedDataService

**位置**：`apps/users/services/seed_data_service.py`

**設計理念**：
- 將業務邏輯從 command 中分離，提高可重用性和可測試性
- Command 僅負責呼叫服務層和輸出訊息
- 符合單一職責原則

**功能**：
- 建立預設測試帳號（管理者、商家、一般會員）
- 檢查帳號是否已存在，避免重複建立
- 驗證 UserPoints 是否自動建立（Signal 觸發）
- 返回詳細的建立結果

**預設帳號配置**：

| 帳號 (Username) | 密碼 (Password) | Email | 身分 (Role) | 說明 |
|----------------|-----------------|-------|------------|------|
| admin | admin12345! | admin@gmail.com | ADMIN | 系統最高管理權限 |
| teststore | store123! | teststore@gmail.com | STORE | 具備商品上架與管理權限 |
| testuser | user123! | testuser@gmail.com | MEMBER | 一般兌換與儲值用戶 |

**建立方式**：
- 管理員：使用 `User.objects.create_superuser()`（自動設定 `is_staff=True`, `is_superuser=True`）
- 商家與會員：使用 `User.objects.create_user()`

**防重複機制**：
- 建立前檢查 `User.objects.filter(username=username).exists()`
- 如果帳號已存在，則跳過建立

**UserPoints 驗證**：
- Signal 會在 User 建立時自動觸發，建立對應的 UserPoints
- 使用 `get_or_create()` 確保即使 Signal 未觸發也能建立
- 記錄 UserPoints 是否由 Signal 自動建立

### 2. Django 管理指令

#### seed_data Command

**位置**：`apps/users/management/commands/seed_data.py`

**功能**：
- 呼叫 `SeedDataService.create_default_accounts()`
- 輸出建立結果（成功、跳過、失敗）
- 使用 Django 的 `self.stdout.write()` 和 `self.style` 輸出格式化的訊息

**使用方式**：
```bash
python manage.py seed_data
```

**輸出範例**：
```
開始建立預設測試帳號...
成功建立 3 個帳號：
  ✓ admin (ADMIN) - admin@gmail.com
  ✓ teststore (STORE) - teststore@gmail.com
  ✓ testuser (MEMBER) - testuser@gmail.com

完成！總共處理 3 個帳號：成功 3 個，跳過 0 個，失敗 0 個
```

### 3. 自動執行整合

**位置**：`entrypoint.sh`

**實作方式**：
在資料庫遷移完成後、啟動服務前執行 `seed_data` 指令：

```bash
# 建立預設測試帳號
echo "建立預設測試帳號..."
python manage.py seed_data || true
```

**注意事項**：
- 使用 `|| true` 確保即使指令失敗也不會中斷容器啟動
- 在開發和生產環境中都會執行，但由於有防重複機制，不會造成問題

## 二、設計決策

### 1. 服務層分離

**決策**：將業務邏輯從 command 中分離到 service 層

**原因**：
- 提高程式碼可重用性：服務層可以在其他地方（如測試、API）重複使用
- 提高可測試性：可以單獨測試服務層邏輯，無需執行 command
- 符合單一職責原則：command 只負責執行和輸出，業務邏輯在 service 層

**實作方式**：
- `SeedDataService` 類別提供 `create_default_accounts()` 類別方法
- 返回結構化的結果字典，方便 command 處理和輸出

### 2. 防重複機制

**決策**：建立前檢查帳號是否存在，存在則跳過

**原因**：
- 避免重複建立導致錯誤（username 和 email 都有唯一性約束）
- 允許重複執行指令而不會出錯
- 適合在 entrypoint.sh 中自動執行

**實作方式**：
```python
if User.objects.filter(username=username).exists():
    result["skipped"].append({
        "username": username,
        "reason": "帳號已存在",
    })
    continue
```

### 3. UserPoints 驗證

**決策**：使用 `get_or_create()` 確保 UserPoints 一定存在

**原因**：
- Signal 理論上會自動觸發，但為了安全起見，使用 `get_or_create()` 作為備援
- 如果 Signal 正常觸發，`get_or_create()` 會返回已存在的物件（`created=False`）
- 如果 Signal 未觸發，`get_or_create()` 會建立新的物件（`created=True`）

**實作方式**：
```python
user_points, created = UserPoints.objects.get_or_create(
    user=user,
    defaults={
        "balance": 0,
        "is_locked": False,
    }
)
# created=False 表示已存在（Signal 觸發）
# created=True 表示手動建立（Signal 未觸發）
```

### 4. Email 設定

**決策**：為每個測試帳號設定對應的 email

**原因**：
- Django 的 `create_superuser()` 通常需要 email
- 提供完整的測試資料，方便測試和開發
- Email 格式：`{username}@gmail.com`

## 三、使用範例

### 手動執行

```bash
# 在 Docker 容器內執行
docker-compose exec point_app python manage.py seed_data

# 或本地開發環境
python manage.py seed_data
```

### 自動執行

當 Docker 容器啟動時，`entrypoint.sh` 會自動執行 `seed_data` 指令，建立預設帳號。

### 驗證帳號

建立後可以使用以下方式驗證：

```python
from django.contrib.auth import get_user_model
from apps.users.models import UserPoints

User = get_user_model()

# 檢查帳號是否存在
admin = User.objects.get(username="admin")
print(f"管理員：{admin.username} ({admin.role})")

# 檢查 UserPoints 是否建立
user_points = UserPoints.objects.get(user=admin)
print(f"點數餘額：{user_points.balance}")
```

### 登入測試

使用建立的帳號進行登入測試：

```bash
# 使用 curl 測試登入
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin12345!"
  }'
```

## 四、測試建議

### 1. 功能測試

- [ ] 執行 `seed_data` 指令，驗證三個帳號是否成功建立
- [ ] 重複執行指令，驗證已存在的帳號是否正確跳過
- [ ] 驗證每個帳號的 UserPoints 是否自動建立
- [ ] 驗證管理員帳號的 `is_staff` 和 `is_superuser` 是否正確設定

### 2. 登入測試

- [ ] 使用 admin 帳號登入，取得 JWT Token
- [ ] 使用 teststore 帳號登入，取得 JWT Token
- [ ] 使用 testuser 帳號登入，取得 JWT Token
- [ ] 驗證 Token 是否有效

### 3. 權限測試

- [ ] 使用 teststore 帳號建立商品（應成功）
- [ ] 使用 testuser 帳號建立商品（應失敗）
- [ ] 使用 admin 帳號建立商品（應成功）

### 4. 自動執行測試

- [ ] 重新建立 Docker 容器，驗證 `entrypoint.sh` 是否自動執行 `seed_data`
- [ ] 驗證容器啟動後，預設帳號是否已建立

## 五、後續優化建議

1. **環境變數控制**：可以透過環境變數控制是否執行 `seed_data`（如 `SEED_DATA=true`）
2. **更多測試資料**：可以擴充建立更多測試資料（如多個商家、多個會員）
3. **初始點數設定**：可以為不同角色設定不同的初始點數
4. **資料清理選項**：可以加入 `--reset` 選項，刪除現有資料後重新建立

---

**最後更新**：Day 2 實作完成

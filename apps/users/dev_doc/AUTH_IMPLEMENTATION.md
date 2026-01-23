# 使用者認證與註冊功能實作總結

## 一、實作內容

### 目錄結構

採用模組化設計，將認證相關功能分離到各自的資料夾：

```
apps/users/
├── serializers/
│   ├── __init__.py
│   └── user_register_serializer.py    # UserRegisterSerializer
├── views/
│   ├── __init__.py
│   └── user_register_view.py          # UserRegisterView
├── urls.py                             # 認證相關 URL 路由
└── ...

core/
└── permissions.py                     # 自訂權限類別
```

### 1. 註冊功能

#### UserRegisterSerializer

**位置**：`apps/users/serializers/user_register_serializer.py`

**功能**：
- 密碼確認驗證（`password` 與 `password_confirm` 必須一致）
- 密碼長度驗證（至少 8 個字元）
- Email 唯一性驗證
- Username 唯一性驗證
- Role 限制驗證（僅允許註冊為 MEMBER 或 STORE，不允許 ADMIN）

**欄位定義**：

| 欄位名稱 | 資料型態 | 必填 | 說明 |
|---------|---------|------|------|
| `username` | CharField | Y | 帳號（用於系統登入） |
| `email` | EmailField | Y | 電子郵件（需唯一） |
| `password` | CharField | Y | 密碼（至少 8 個字元，write_only） |
| `password_confirm` | CharField | Y | 密碼確認（write_only） |
| `role` | ChoiceField | Y | 使用者身分（MEMBER/STORE，預設 MEMBER） |

**密碼加密機制**：
- 使用 `User.objects.create_user()` 方法建立使用者
- Django 會自動透過 `set_password()` 加密密碼
- 儲存到資料庫時已經是加密後的 hash，不會以明文儲存

#### UserRegisterView

**位置**：`apps/users/views/user_register_view.py`

**功能**：
- 提供開放註冊端點（`AllowAny` 權限）
- 註冊成功後自動觸發 Signal 建立 `UserPoints` 紀錄
- 返回註冊成功訊息和使用者基本資訊（不含密碼）

**API 端點**：
- `POST /api/auth/register/`

**回應格式**：
```json
{
  "message": "註冊成功",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "MEMBER"
  }
}
```

### 2. JWT 認證端點

**位置**：`apps/users/urls.py`

使用 `djangorestframework-simplejwt` 提供的內建 View：

| 端點 | Method | 說明 |
|------|--------|------|
| `/api/auth/token/` | POST | 登入取得 Access Token 和 Refresh Token |
| `/api/auth/token/refresh/` | POST | 使用 Refresh Token 刷新 Access Token |
| `/api/auth/token/verify/` | POST | 驗證 Token 是否有效 |

**JWT 設定**（`config/settings/drf.py`）：
- Access Token 有效期：1 小時
- Refresh Token 有效期：7 天
- 啟用 Token 輪換（`ROTATE_REFRESH_TOKENS: True`）
- 啟用 Token 黑名單（`BLACKLIST_AFTER_ROTATION: True`）

**登入請求格式**：
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**登入回應格式**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. 自訂權限類別

**位置**：`core/permissions.py`

#### IsStore

僅允許 `role=STORE` 的用戶操作。

**使用場景**：
- 建立商品（`ProductViewSet.create`）

#### IsAdmin

僅允許 `role=ADMIN` 的用戶操作。

**使用場景**：
- 未來管理功能（如：管理所有商品、管理使用者等）

#### IsProductOwner

僅允許商品所屬店家進行修改，管理者可以操作任何商品。

**權限邏輯**：
- 讀取操作（GET）：允許所有人
- 修改操作（POST/PUT/PATCH/DELETE）：
  - 未登入用戶：不允許
  - 管理者（ADMIN）：允許操作任何商品
  - 一般用戶：僅允許操作自己的商品

**使用場景**：
- 更新商品（`ProductViewSet.update`）
- 刪除商品（`ProductViewSet.destroy`）

## 二、設計決策

### 1. 註冊 Role 限制

**決策**：不允許註冊為 ADMIN

**原因**：
- 安全性考量：管理者帳號應由系統管理員手動建立
- 防止權限濫用：避免一般使用者註冊為管理者

**實作方式**：
- 在 `UserRegisterSerializer` 的 `validate()` 方法中檢查
- 在 `ChoiceField` 的 `choices` 參數中僅提供 `[MEMBER, STORE]`

### 2. 密碼加密機制

**決策**：使用 Django 內建的 `create_user()` 方法

**原因**：
- Django 會自動處理密碼加密（使用 PBKDF2 演算法）
- 不需要手動處理密碼 hash
- 符合 Django 最佳實踐

**注意事項**：
- ❌ 錯誤：`user.password = "raw_password"`（不會加密）
- ✅ 正確：`User.objects.create_user(password="raw_password")`（自動加密）

### 3. 權限控制方式

**決策**：使用 `get_permissions()` 動態設定權限

**原因**：
- 不同操作需要不同權限（查詢不需要登入，建立需要店家權限）
- 比靜態 `permission_classes` 更靈活
- 符合 DRF 最佳實踐

**實作範例**（`ProductViewSet`）：
```python
def get_permissions(self):
    if self.action in ['list', 'retrieve']:
        return [AllowAny()]  # 查詢不需要登入
    elif self.action == 'create':
        return [IsAuthenticated(), IsStore()]  # 建立需要店家權限
    else:
        return [IsAuthenticated(), IsProductOwner()]  # 修改需要是擁有者
```

### 4. 循環導入問題處理

**問題**：`core/__init__.py` 直接導入 `permissions` 導致 `AppRegistryNotReady` 錯誤

**原因**：
- `core/__init__.py` 在模組層級導入 `permissions`
- `permissions.py` 導入 `apps.users.models.RoleChoices`
- Django 初始化階段觸發模型導入，導致錯誤

**解決方案**：
- 移除 `core/__init__.py` 中的直接導入
- 使用時直接從 `core.permissions` 導入：
  ```python
  from core.permissions import IsStore, IsAdmin, IsProductOwner
  ```

## 三、API 端點總覽

### 認證相關

| 端點 | Method | 權限 | 說明 |
|------|--------|------|------|
| `/api/auth/register/` | POST | AllowAny | 使用者註冊 |
| `/api/auth/token/` | POST | AllowAny | 登入取得 Token |
| `/api/auth/token/refresh/` | POST | AllowAny | 刷新 Token |
| `/api/auth/token/verify/` | POST | AllowAny | 驗證 Token |

### 商品管理（權限更新）

| 端點 | Method | 權限 | 說明 |
|------|--------|------|------|
| `/api/products/` | GET | AllowAny | 查詢商品列表 |
| `/api/products/{id}/` | GET | AllowAny | 查詢商品詳情 |
| `/api/products/` | POST | IsAuthenticated + IsStore | 建立商品 |
| `/api/products/{id}/` | PATCH | IsAuthenticated + IsProductOwner | 更新商品 |
| `/api/products/{id}/` | DELETE | IsAuthenticated + IsProductOwner | 軟刪除商品 |

## 四、技術細節

### 1. JWT Token 使用方式

在需要認證的 API 請求中，於 Header 中加入：

```
Authorization: Bearer <access_token>
```

**範例**：
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://localhost:8000/api/products/
```

### 2. Token 刷新流程

1. 使用 Access Token 進行 API 請求
2. 當 Access Token 過期時（1 小時後），使用 Refresh Token 取得新的 Access Token
3. 請求 `/api/auth/token/refresh/`，提供 `refresh` token
4. 取得新的 `access` 和 `refresh` token

### 3. 權限檢查流程

1. **ViewSet 層級**：`get_permissions()` 根據 `action` 動態設定權限
2. **Permission 類別**：檢查 `request.user` 是否符合條件
3. **物件層級**：`IsProductOwner` 檢查物件擁有者

### 4. Signal 自動觸發

註冊成功後，Django Signal 會自動觸發 `create_user_points`，建立對應的 `UserPoints` 紀錄：

```python
@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.get_or_create(
            user=instance,
            defaults={"balance": 0, "is_locked": False}
        )
```

## 五、測試建議

### 1. 註冊功能測試

- [ ] 註冊 MEMBER 使用者（成功）
- [ ] 註冊 STORE 使用者（成功）
- [ ] 嘗試註冊 ADMIN（應失敗）
- [ ] 密碼與確認密碼不一致（應失敗）
- [ ] Email 重複註冊（應失敗）
- [ ] Username 重複註冊（應失敗）
- [ ] 密碼長度不足 8 字元（應失敗）

### 2. 登入功能測試

- [ ] 使用正確帳號密碼登入（成功）
- [ ] 使用錯誤密碼登入（應失敗）
- [ ] 使用不存在的帳號登入（應失敗）
- [ ] 使用 Refresh Token 刷新 Access Token（成功）
- [ ] 使用過期的 Access Token 請求 API（應失敗）

### 3. 權限控制測試

- [ ] 未登入查詢商品列表（成功）
- [ ] 未登入建立商品（應失敗）
- [ ] MEMBER 登入建立商品（應失敗）
- [ ] STORE 登入建立商品（成功）
- [ ] STORE 更新自己的商品（成功）
- [ ] STORE 更新他人的商品（應失敗）
- [ ] ADMIN 更新任何商品（成功）

## 六、後續優化建議

1. **密碼強度驗證**：加入更嚴格的密碼規則（大小寫、數字、特殊字元）
2. **Email 驗證**：實作 Email 驗證機制，確保使用者提供有效的 Email
3. **登入失敗限制**：實作登入失敗次數限制，防止暴力破解
4. **Token 黑名單**：實作完整的 Token 黑名單機制（需安裝 `django-rest-framework-simplejwt[blacklist]`）
5. **記住我功能**：提供更長的 Token 有效期選項
6. **第三方登入**：整合 Google、Facebook 等第三方登入

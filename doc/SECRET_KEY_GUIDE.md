# SECRET_KEY 使用說明

## 什麼是 SECRET_KEY？

`SECRET_KEY` 是 Django 專案中最重要的安全設定之一，它是一個用於加密和簽名的密鑰字串。Django 使用它來保護各種安全相關的功能。

## SECRET_KEY 的用途

### 1. **Session 加密**
- Django 使用 SECRET_KEY 來加密和簽名 session 資料
- 確保用戶的 session 資料不會被篡改

### 2. **CSRF Token 生成**
- 用於生成和驗證 CSRF（跨站請求偽造）保護 token
- 防止惡意網站偽造請求

### 3. **密碼重置 Token**
- 生成密碼重置連結的簽名
- 確保重置連結的安全性

### 4. **訊息框架簽名**
- 用於簽名 Django 的訊息（如成功/錯誤訊息）
- 防止訊息被篡改

### 5. **Cookie 簽名**
- 簽名和加密 cookie 資料
- 保護用戶的 cookie 不被偽造

### 6. **其他加密操作**
- 各種需要加密或簽名的操作都會使用 SECRET_KEY

## 為什麼 SECRET_KEY 很重要？

### ⚠️ 安全風險

如果 SECRET_KEY 洩露或被猜測到，攻擊者可以：

1. **偽造 session**：冒充其他用戶登入
2. **繞過 CSRF 保護**：發送惡意請求
3. **偽造密碼重置連結**：重置其他用戶的密碼
4. **篡改 cookie**：修改用戶的資料

### ✅ 正確做法

- **永遠不要**將 SECRET_KEY 提交到版本控制系統（Git）
- **永遠不要**在程式碼中硬編碼 SECRET_KEY
- **使用環境變數**來管理 SECRET_KEY
- **每個環境**（開發、測試、生產）使用不同的 SECRET_KEY

## 如何生成安全的 SECRET_KEY？

### 方法一：使用 Django 內建工具

```bash
# 在 Django shell 中生成
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()
```

### 方法二：使用 Python 腳本

```python
# generate_secret_key.py
from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()
print(secret_key)
```

執行：
```bash
python generate_secret_key.py
```

### 方法三：使用線上工具（不推薦用於生產環境）

可以使用 Django 官方或可信的線上工具生成，但**不建議**用於生產環境。

### 方法四：使用 Python 直接生成

```python
import secrets
print(secrets.token_urlsafe(50))
```

## 在本專案中的使用方式

### 1. 開發環境設定

在 `.env` 檔案中設定：

```env
SECRET_KEY=django-insecure-dev-key-change-in-production
```

⚠️ **注意**：開發環境可以使用簡單的 key，但生產環境必須使用強隨機字串。

### 2. 生產環境設定

```env
SECRET_KEY=your-very-long-random-secret-key-generated-by-django
```

### 3. 環境變數讀取

在 `config/settings/base.py` 中：

```python
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")
```

這表示：
- 優先從環境變數 `.env` 讀取 `SECRET_KEY`
- 如果沒有設定，使用預設值（僅用於開發，生產環境必須設定）

## 最佳實踐

### ✅ 應該做的

1. **使用環境變數**
   ```env
   # .env 檔案（不要提交到 Git）
   SECRET_KEY=your-secret-key-here
   ```

2. **不同環境使用不同 KEY**
   - 開發環境：可以使用簡單的 key
   - 測試環境：使用不同的 key
   - 生產環境：使用強隨機生成的 key

3. **定期更換**（如果可能）
   - 如果懷疑 SECRET_KEY 洩露，立即更換
   - 更換後需要清除所有 session

4. **使用 .gitignore**
   ```
   # .gitignore
   .env
   ```

### ❌ 不應該做的

1. **不要硬編碼在程式碼中**
   ```python
   # ❌ 錯誤示範
   SECRET_KEY = "django-insecure-12345"
   ```

2. **不要提交到版本控制**
   ```bash
   # ❌ 不要這樣做
   git add .env
   git commit -m "Add env file"
   ```

3. **不要在公開場所分享**
   - 不要貼在論壇、聊天室
   - 不要放在公開的程式碼倉庫

4. **不要使用預設值**
   ```python
   # ⚠️ 僅用於開發，生產環境必須設定
   SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this")
   ```

## 在本專案中的設定步驟

### 1. 生成 SECRET_KEY

```bash
# 方法一：使用 Django
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())

# 方法二：使用 Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. 建立 .env 檔案

```bash
# 複製範例檔案
cp env.example .env
```

### 3. 編輯 .env 檔案

```env
# 將生成的 SECRET_KEY 貼上
SECRET_KEY=生成的長字串
DEBUG=true
TIME_ZONE=Asia/Taipei
# ... 其他設定
```

### 4. 確認 .gitignore

確保 `.env` 在 `.gitignore` 中：

```
.env
.env.local
```

## 常見問題

### Q: 如果忘記了 SECRET_KEY 會怎樣？

A: 如果忘記了生產環境的 SECRET_KEY：
- 所有用戶的 session 會失效（需要重新登入）
- 所有密碼重置 token 會失效
- 需要重新生成新的 SECRET_KEY 並更新設定

### Q: 可以共用同一個 SECRET_KEY 嗎？

A: **不建議**。每個專案和環境都應該使用不同的 SECRET_KEY。

### Q: SECRET_KEY 需要多長？

A: Django 預設生成的 SECRET_KEY 約 50 個字元，這已經足夠安全。

### Q: 如何驗證 SECRET_KEY 是否正確設定？

A: 啟動 Django 服務，如果沒有錯誤訊息，通常表示設定正確。

## 快速生成指令

```bash
# 一行指令生成 SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
```

這個指令會直接輸出 `SECRET_KEY=...` 格式，可以直接複製到 `.env` 檔案中。

## 總結

- **SECRET_KEY 是 Django 安全的核心**
- **永遠不要提交到版本控制**
- **使用環境變數管理**
- **生產環境必須使用強隨機生成的 key**
- **定期檢查和更換（如需要）**



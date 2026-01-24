# JWT 登入 500 錯誤修正記錄

## 問題描述

測試 JWT 登入 API (`POST /api/auth/token/`) 時出現 `500 Internal Server Error`。

**錯誤訊息**：`TypeError: Expected a string value`

**錯誤位置**：JWT token 生成時，`jwt.encode()` 嘗試將 `SIGNING_KEY` 轉換為 bytes 失敗。

## 問題原因

在 `config/settings/drf.py` 中，`SIMPLE_JWT` 設定中的 `SIGNING_KEY` 被設為 `None`：

```python
SIMPLE_JWT = {
    ...
    "SIGNING_KEY": None,  # 使用 SECRET_KEY（但實際上仍為 None）
    ...
}
```

JWT 簽名需要字串類型的簽名金鑰，但設定為 `None` 導致無法生成 token。

## 解決方案

在 `config/settings/drf.py` 中，從環境變數讀取 `SECRET_KEY` 並設定給 `SIGNING_KEY`：

```python
# JWT Settings
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv(".env")

# 取得 SECRET_KEY（與 base.py 中的邏輯一致）
_JWT_SIGNING_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": _JWT_SIGNING_KEY,  # 使用 SECRET_KEY
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
```

**設計決策**：使用 `os.getenv()` 重新讀取環境變數，避免循環導入問題，並與 `base.py` 中的邏輯保持一致。

## 驗證結果

**修正前**：`HTTP 500 Internal Server Error`  
**修正後**：`HTTP 200 OK`，成功返回 `access` 和 `refresh` token

✅ 登入 API 正常運作

## 相關檔案

- `config/settings/drf.py` - 修正 `SIMPLE_JWT` 設定中的 `SIGNING_KEY`
- `config/settings/base.py` - 定義 `SECRET_KEY`
- `.env` - 環境變數設定檔（需包含 `SECRET_KEY`）

## 注意事項

1. 確保 `.env` 檔案中包含 `SECRET_KEY`
2. 生產環境必須設定強而有力的 `SECRET_KEY`，不要使用預設值

---

**修正日期**：2026-01-24  
**修正狀態**：✅ 已完成並驗證

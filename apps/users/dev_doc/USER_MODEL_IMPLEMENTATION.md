# User 模型實作總結

## 一、新增資料表

### 實作內容
建立客製化 `User` 模型，繼承 Django `AbstractUser`，新增以下欄位：
- `role`: 使用者身分（CharField，選項：MEMBER/STORE/ADMIN）
- `is_enable`: 帳號啟用狀態（BooleanField，預設 True）
- `memo`: 備註（CharField，可選）

### 設計決策與異動

1. **role 欄位型態**
   - 初始設計：`SmallIntegerField` + `IntegerChoices`（1/2/3）
   - 最終採用：`CharField` + `TextChoices`（"MEMBER"/"STORE"/"ADMIN"）
   - 原因：提升可讀性，無需記數字對應，程式碼更直觀

2. **id 主鍵設計**
   - 初始設計：`UUIDField`（UUID 格式）
   - 最終採用：`BigAutoField`（自動遞增整數）
   - 原因：簡化設計，一般系統無需 UUID，查詢效率更高

3. **移除便利方法**
   - 移除 `is_member`、`is_store`、`is_admin` 三個 `@property`
   - 原因：非必要，直接使用 `user.role == RoleChoices.MEMBER` 即可

## 二、環境修正

### Windows 行尾符號問題
- 問題：`entrypoint.sh` 在 Windows 編輯後產生 CRLF，導致容器執行錯誤
- 解決方案：
  - 安裝 `dos2unix` 工具於 Dockerfile
  - 建立 `.gitattributes` 確保 `.sh` 檔案使用 LF
  - 在 Dockerfile 中自動轉換行尾符號

### Django 初始化問題
- 問題：`apps/users/__init__.py` 導入模型導致 `AppRegistryNotReady` 錯誤
- 解決方案：移除 `__init__.py` 中的模型導入，需要時直接從 `apps.users.models` 導入

### Migration 設定
- 建立 `apps/users/migrations/` 目錄
- 更新 `entrypoint.sh` 確保先建立 users migration（因 `AUTH_USER_MODEL` 設定）

## 三、簡易測試建立

建立 `check_users.py` 檢查腳本，功能包含：
- 檢查資料表是否存在
- 統計資料筆數
- 顯示資料表結構（欄位名稱、型態、長度）
- 顯示前 5 筆資料（不顯示密碼）
- 顯示 RoleChoices 定義

腳本僅讀取資料，不進行任何新增或修改操作。

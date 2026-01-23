# UserPoints 模型實作總結

## 一、實作內容

### 模型設計

建立 `UserPoints` 模型，與 `User` 建立 One-to-One 關係，用於存放使用者的點數餘額。

**位置**：`apps/users/models/userpoint_model.py`

**繼承**：`BaseModel`（提供 `created_at`, `updated_at` 時間戳記）

### 欄位定義

| 欄位名稱 | 資料型態 | 說明 | 預設值 |
|---------|---------|------|--------|
| `user` | OneToOneField | 所屬用戶（與 User 一對一關聯） | - |
| `balance` | IntegerField | 點數餘額，不得為負數 | 0 |
| `is_locked` | BooleanField | 錢包鎖定狀態 | False |

### 設計決策

1. **balance 型態**：使用 `IntegerField` 而非 `DecimalField`
   - 原因：點數系統通常不需要小數點，使用整數更簡潔
   - 驗證：使用 `MinValueValidator(0)` 確保不為負數

2. **資料表命名**：`user_points`
   - 符合 Django 命名慣例
   - 清楚表達與 User 的關聯

3. **模型位置**：放在 `apps/users/models/` 而非 `apps/points/`
   - 原因：與 User 是 OneToOne 關係，邏輯上更緊密
   - Signal 處理更方便，無需跨 app
   - 未來 `apps/points/` 可專注於交易記錄（PointTransaction）

## 二、自動化初始化

### Signal 實作

**位置**：`apps/users/signals.py`

**功能**：當 User 建立時，自動建立對應的 UserPoints 紀錄

**實作方式**：
```python
@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.get_or_create(
            user=instance,
            defaults={
                "balance": 0,
                "is_locked": False,
            }
        )
```

**注意事項**：
- 使用 `get_or_create` 避免重複建立
- 只在 `created=True` 時觸發（避免更新時重複觸發）

### Apps 設定

**位置**：`apps/users/apps.py`

在 `ready()` 方法中載入 signals：
```python
def ready(self):
    """載入 signals"""
    import apps.users.signals  # noqa
```

## 三、模型方法

### lock() 與 unlock()

提供便利方法用於鎖定/解鎖錢包：

```python
user_points.lock()   # 鎖定錢包
user_points.unlock() # 解鎖錢包
```

## 四、資料庫 Migration

### 執行步驟

```bash
# 建立 migration
python manage.py makemigrations users

# 執行 migration
python manage.py migrate
```

### 檢查資料表

進入 Django shell 檢查：

```python
from apps.users.models import User, UserPoints

# 檢查資料表是否存在
UserPoints._meta.db_table  # 應顯示 'user_points'

# 檢查欄位
UserPoints._meta.get_fields()
```

## 五、測試計劃（待實作）

### 單元測試項目

1. **Signal 自動建立測試**
   - [ ] 建立 User 後，UserPoints 是否自動建立
   - [ ] UserPoints 的 balance 是否為 0
   - [ ] UserPoints 的 is_locked 是否為 False

2. **欄位驗證測試**
   - [ ] balance 是否不允許負數
   - [ ] balance 預設值是否為 0

3. **關聯測試**
   - [ ] User 與 UserPoints 是否為 OneToOne 關係
   - [ ] 刪除 User 時，UserPoints 是否一併刪除（CASCADE）

4. **方法測試**
   - [ ] lock() 方法是否正確設定 is_locked = True
   - [ ] unlock() 方法是否正確設定 is_locked = False

### 測試檔案位置

建議建立：`apps/users/tests/test_userpoints.py`

## 六、使用範例

### 建立使用者並檢查點數

```python
from apps.users.models import User, UserPoints

# 建立使用者
user = User.objects.create_user(
    username="test_user",
    email="test@example.com",
    password="password123"
)

# 檢查點數是否自動建立
user_points = user.points  # 透過 related_name 存取
print(user_points.balance)  # 應顯示 0
print(user_points.is_locked)  # 應顯示 False
```

### 鎖定/解鎖錢包

```python
# 鎖定錢包
user_points.lock()
print(user_points.is_locked)  # 應顯示 True

# 解鎖錢包
user_points.unlock()
print(user_points.is_locked)  # 應顯示 False
```

## 七、後續開發項目

- [ ] 點數儲值 API
- [ ] 點數扣除邏輯（兌換商品時）
- [ ] 點數交易記錄（PointTransaction）
- [ ] 錢包鎖定/解鎖 API（管理員功能）

---

**最後更新**：Day 2 實作完成

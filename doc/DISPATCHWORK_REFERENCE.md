# Dispatchwork 專案設計參考 - 可複用組件統整

## 一、User 模型設計

### 核心特點
- **繼承方式**: `UserUser` 繼承自 `AbstractUser` 和 `ReadOnlyModel`
- **定義位置**: `apps/mainProjectORM/models.py`
- **設定方式**: 在 `settings/base.py` 中設定 `AUTH_USER_MODEL = "mainProjectORM.UserUser"`
- **資料表**: `user_user` (managed=False，表示由外部資料庫管理)

### 擴充欄位
```python
# 主要擴充欄位
- auth_type: 認證類型
- display_name: 顯示名稱
- location: 位置
- is_admin: 是否為管理員
- emp_no: 員工編號
- is_head: 是否為主管
- head_level: 主管層級
- telephone, extension, cellphone: 聯絡方式
- icon: 頭像
- ldap_dn: LDAP 識別
- department: 部門 (ForeignKey)
- domain: 網域/公司別 (ForeignKey)
```

### 適用場景
- 多租戶系統（透過 domain 區分）
- 部門管理（透過 department）
- 角色權限管理（is_superuser, is_admin, is_domain_admin）

---

## 二、BaseModel 基礎模型

### 設計理念
所有業務模型繼承 `BaseModel`，自動記錄操作者與時間戳記。

### 核心欄位
```python
class BaseModel(models.Model):
    created_at = DateTimeField(auto_now_add=True)      # 創建時間
    created_by = ForeignKey(AUTH_USER_MODEL)          # 創建者
    updated_at = DateTimeField(auto_now=True)         # 修改時間
    updated_by = ForeignKey(AUTH_USER_MODEL)          # 修改者
    domain = ForeignKey(DomainPermsDomain)            # 網域/公司別
```

### 自動化機制
- **save() 方法覆寫**: 自動從 `CurrentUserMiddleware` 取得當前用戶
- **創建時**: 自動設定 `created_by` 和 `domain`
- **更新時**: 自動更新 `updated_by`

### 使用範例
```python
from core.models.base_model import BaseModel

class ProductModel(BaseModel):
    name = models.CharField(max_length=100)
    # 自動擁有 created_at, created_by, updated_at, updated_by, domain
```

### 適用場景
- 需要審計追蹤的資料表
- 多租戶系統（透過 domain 過濾）
- 需要記錄操作者的業務邏輯

---

## 三、認證與中間件設計

### CurrentUserMiddleware
**功能**: 從 JWT token 中解析用戶資訊，並提供線程本地儲存。

### 核心機制
```python
# 支援的 Token 格式
- "token <token_string>"
- "Basic <token_string>"
- 直接 token 字串

# JWT 解析
- 使用 settings.SECRET_KEY 解密
- 從 payload 取得 user_id
- 透過線程本地變數儲存當前用戶
```

### 使用方式
```python
from config.middlewares import CurrentUserMiddleware

# 在任何地方取得當前用戶
current_user = CurrentUserMiddleware.get_current_user()
```

### 適用場景
- JWT 認證系統
- 需要全域存取當前用戶的場景
- BaseModel 自動記錄操作者

---

## 四、權限系統設計

### 自定義 Permission Classes
位置: `utils/permissions.py`

#### 1. SuperuserReadWritablePermission
- **讀取**: 所有認證用戶
- **寫入**: 僅 superuser

#### 2. DomainManagerPermission
- **讀取**: 所有認證用戶
- **寫入**: superuser 或 domain_admin

#### 3. UserManagerPermission
- **讀取**: 所有認證用戶
- **寫入**: 
  - superuser / domain_admin: 全部
  - admin: 自己 domain 下的用戶
  - user: 僅自己

#### 4. DomainPermission
- **讀取**: 所有認證用戶
- **寫入**: 一般用戶（superuser 和 domain_admin 僅讀取）

### 使用範例
```python
from utils.permissions import DomainPermission

class ProductViewSet(ModelViewSet):
    permission_classes = [DomainPermission]
```

### 適用場景
- 多租戶權限控制
- 角色基礎存取控制 (RBAC)
- 資料隔離需求

---

## 五、View 基礎類設計

### 擴展的 View 類別
位置: `utils/views/base.py`

#### 類別階層
```python
APIView (基礎)
  └─ GenericAPIView (加入 ordering_fields = "__all__")
      └─ GenericViewSet
          └─ ModelViewSet (支援 extra_kwargs_on_save)
```

### 核心功能
- **ordering_fields**: 預設支援所有欄位排序
- **extra_kwargs_on_save**: 在 create/update 時可傳入額外參數

### 使用範例
```python
from utils.views import ModelViewSet

class ProductViewSet(ModelViewSet):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    
    def perform_create(self, serializer):
        # extra_kwargs_on_save 會自動傳入
        return serializer.save(**self.extra_kwargs_on_save)
```

---

## 六、分頁系統設計

### DemoPageNumberPagination
位置: `utils/pagination.py`

### 特色功能
- **可選分頁**: 若 URL 無 `page` 參數，返回全部資料
- **自訂格式**: 模仿 Rapid7 官方分頁回應格式

### 回應格式
```json
{
  "page": {
    "size": 10,
    "totalPages": 5,
    "totalResources": 50
  },
  "results": [...]
}
```

### 設定方式
```python
# settings/drf.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.DemoPageNumberPagination"
}
```

---

## 七、異常處理系統

### 自定義異常類別
位置: `utils/exceptions.py`

### 標準化異常處理器
位置: `utils/custom_exception_handler.py`

### 回應格式
```json
{
  "type": "validation_error",
  "errors": [...原始錯誤...],
  "details": "錯誤詳情, field1, field2",
  "dialog": true/false
}
```

### 功能特點
- **錯誤聚合**: 根據 (code, detail) 聚合相同錯誤
- **對話框控制**: 根據錯誤類型決定是否顯示對話框
- **友好訊息**: 生成易讀的錯誤詳情字串

### 使用範例
```python
from utils.exceptions import DomainStillUsedError

if domain_in_use:
    raise DomainStillUsedError()
```

---

## 八、專案結構設計

### 目錄組織
```
apps/
  ├── mainProjectORM/     # User 模型與核心 ORM
  ├── <app_name>/         # 業務應用
  │   ├── models/         # 模型（可拆分多檔案）
  │   ├── serializers/    # 序列化器
  │   ├── views/          # 視圖
  │   ├── filters/        # 過濾器
  │   └── permissions/    # 應用特定權限
core/
  ├── models/             # 核心模型（BaseModel）
  └── ...
config/
  ├── settings/           # 設定檔分離
  │   ├── base.py
  │   ├── development.py
  │   └── production.py
  └── middlewares.py      # 中間件
utils/                    # 共用工具
```

### 設定檔分離
- **base.py**: 基礎設定
- **development.py**: 開發環境
- **production.py**: 生產環境
- **drf.py**: DRF 相關設定
- **db.py**: 資料庫設定

---

## 九、可複用於點數系統的組件

### 1. BaseModel
✅ **適用**: 所有業務模型（Product, Order, PointTransaction）
- 自動記錄創建者、修改者
- 支援審計追蹤

### 2. CurrentUserMiddleware
✅ **適用**: JWT 認證機制
- 可沿用現有 JWT 解析邏輯
- 或改為使用 djangorestframework-simplejwt

### 3. 權限系統
⚠️ **部分適用**: 
- 可參考設計理念，但需簡化為 MEMBER / MERCHANT 角色
- 移除 domain 相關邏輯（除非需要多租戶）

### 4. 分頁系統
✅ **適用**: 商品列表、訂單列表等
- 可直接使用 DemoPageNumberPagination

### 5. 異常處理
✅ **適用**: 統一錯誤回應格式
- 可沿用異常處理器設計

### 6. View 基礎類
✅ **適用**: 所有 ViewSet
- 可沿用 ModelViewSet 設計

---

## 十、需要調整的部分

### 1. User 模型
- **移除**: domain, department, LDAP 等複雜欄位
- **保留**: 基礎欄位（username, email, is_active 等）
- **新增**: role 欄位（MEMBER / MERCHANT）

### 2. BaseModel
- **移除**: domain 欄位（除非需要多租戶）
- **保留**: created_by, updated_by, created_at, updated_at

### 3. 權限系統
- **簡化**: 設計 MemberPermission, MerchantPermission
- **移除**: Domain 相關權限邏輯

### 4. 認證機制
- **選項 A**: 沿用現有 JWT 設計
- **選項 B**: 使用 djangorestframework-simplejwt（更標準）

---

## 十一、建議的採用策略

### 直接採用
1. ✅ BaseModel（移除 domain）
2. ✅ 分頁系統
3. ✅ 異常處理系統
4. ✅ View 基礎類
5. ✅ 專案結構組織

### 參考設計
1. ⚠️ User 模型（簡化後採用）
2. ⚠️ 權限系統（簡化後採用）
3. ⚠️ CurrentUserMiddleware（可改用 simplejwt）

### 不適用
1. ❌ Domain 多租戶邏輯
2. ❌ Department 部門管理
3. ❌ LDAP 整合

---

## 十二、實作建議

### 第一步：建立基礎架構
1. 複製 BaseModel（移除 domain）
2. 設定 AUTH_USER_MODEL
3. 建立簡化版 User 模型（含 role 欄位）

### 第二步：認證系統
1. 選擇 JWT 方案（沿用或 simplejwt）
2. 實作登入/註冊 API
3. 設定權限類別

### 第三步：業務模型
1. 所有模型繼承 BaseModel
2. 實作 Product, Order, PointAccount 等模型
3. 建立對應的 ViewSet

### 第四步：優化與測試
1. 併發控制（select_for_update）
2. 綠界支付整合
3. API 測試


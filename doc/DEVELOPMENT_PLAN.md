# 7 天開發進度規劃表 (Day 2 - Day 7)

## 專案目標

完成「點數兌換贈品系統」的 MVP（最簡可行產品），包含店家商品管理、會員點數儲值與兌換功能。

---

## 第一階段：JWT 驗證整合 (Day 2)

**目標**：建立完整的認證機制，為後續業務 API 提供安全基礎。

### JWT 驗證整合

#### 登入 API
- [x] 實作登入 API
  - [x] 使用者帳號密碼驗證
  - [x] 取得 Access Token
  - [x] 實作 Refresh Token 機制
  - [x] 整合 `rest_framework_simplejwt` 的 TokenObtainPairView

#### 權限掛載
- [x] 將所有業務 API 掛載 `IsAuthenticated` 權限
  - [x] 檢查 DRF 權限設定（已在 `config/settings/drf.py` 設定）
  - [x] 確保未登入使用者無法存取業務 API
  - [x] 測試權限控制是否正常運作
  - [x] 驗證 JWT Token 驗證流程

---

## 第二階段：核心業務邏輯與 API 實作 (Day 3-4)

**目標**：完成店家上架與會員兌換的「最簡可行產品 (MVP)」路徑。

### 店家商品管理 API (Products App)

#### 實作項目
- [x] 商品的 CRUD（建立、讀取、更新、刪除）
  - [x] 建立商品 API
  - [x] 查詢商品列表 API
  - [x] 查詢單一商品 API
  - [x] 更新商品 API
  - [x] 刪除商品 API（軟刪除）

#### 權限控制
- [x] 確保 A 店家不能修改 B 店家的商品
  - [x] 使用 `role` 判斷使用者身分
  - [x] 實作權限檢查邏輯（IsProductOwner 權限類別）
  - [x] 商品與店家的關聯設計
  - [x] 在 ViewSet 中加入權限驗證（使用 get_permissions() 動態設定）

### 點數與兌換邏輯 (Points App)

#### 儲值點數 API
- [x] 實作「儲值點數」API
  - [x] 初期使用簡易 POST 模擬金額輸入
  - [x] 手動增加 points 餘額
  - [x] 記錄儲值交易紀錄（PointTransaction）

#### 兌換商品 API
- [x] 實作「兌換商品」API
  - [x] 餘額檢查邏輯
  - [x] 點數扣除邏輯
  - [x] 生成兌換序號（格式：EX + YYYYMMDD + 6位隨機碼）
  - [x] 記錄兌換交易紀錄（PointExchange 和 PointTransaction）

#### 資料庫事務 (Transaction)
- [x] 確保扣點與生成紀錄在同一事務中完成
  - [x] 使用 Django 的 `transaction.atomic()` 裝飾器
  - [x] 避免資料不一致問題
  - [x] 處理異常回滾機制
  - [x] 使用 `select_for_update()` 悲觀鎖防止併發問題

---

## 第三階段：API 文件化與錯誤處理 (Day 5)

**目標**：讓 API 具備生產環境的穩定度與易讀性。

### API 文件化 (Swagger)

#### drf-spectacular 整合
- [x] 整合 drf-spectacular（已在設定檔中配置）
- [x] 為所有 API 添加 OpenAPI 註解
  - [x] 登入 API 文件化（使用 djangorestframework-simplejwt 內建文件）
  - [x] 商品 API 文件化（ProductViewSet 已添加 @extend_schema）
  - [x] 點數 API 文件化（PointDepositView, PointTransactionViewSet 已添加）
  - [x] 兌換 API 文件化（PointExchangeView 已添加）
  - [x] 用戶個人資料 API 文件化（MeView 已添加）
- [x] 設定 API 文件端點（`/api/docs/` 與 `/api/redoc/`）
- [x] 確保面試官打開網址即可看到清楚的 API 規格

### 錯誤處理

#### 統一回傳格式
- [x] 實作統一的錯誤回應格式（已在 `utils/custom_exception_handler.py` 中實作）
- [x] 驗證所有 API 錯誤回應格式一致性
  - [x] 格式範例：`{"type": "validation_error", "errors": [...], "details": "...", "dialog": false}`
  - [x] 整合 `drf-standardized-errors` 或自訂異常處理器
  - [x] 展現開發標準與一致性

---

## 第四階段：品質控管與交付準備 (Day 6-7)

**目標**：確保程式碼整潔，無重大 Bug。

### 單元測試 (Unit Test)

#### 測試案例撰寫
- [x] 針對「點數扣除邏輯」撰寫測試案例
  - [x] 餘額剛好的情境（test_member_can_exchange_product）
  - [x] 餘額不足的情境（test_insufficient_balance）
  - [x] 商品不存在的情境（test_inactive_product, test_insufficient_stock）
  - [x] 其他邊界條件測試（併發測試、權限測試等）
  - [x] 認證測試（test_auth.py）
  - [x] 商品權限測試（test_products_permissions.py）
  - [x] 點數儲值測試（test_point_deposit.py）
  - [x] 點數兌換測試（test_point_exchange.py）

#### 測試覆蓋率
- [x] 確保核心業務邏輯有足夠的測試覆蓋
- [x] 執行測試並確認所有測試通過

### CI 與規範檢查

#### 程式碼格式化
- [ ] 執行 Black 格式化
  - [ ] 確保代碼符合 PEP8
  - [ ] 統一程式碼風格

#### 程式碼品質檢查
- [ ] 執行 Linter 檢查（如：flake8, pylint）
- [ ] 修正所有警告與錯誤

### 撰寫優質 README

#### 文件內容
- [ ] 專案簡介與目標
- [ ] 如何啟動（Docker-compose）
  - [ ] 環境變數設定說明
  - [ ] 啟動步驟
- [ ] 如何執行測試
  - [ ] 測試命令
  - [ ] 測試覆蓋率查看方式
- [ ] API 文件連結
  - [ ] Swagger UI 連結
  - [ ] ReDoc 連結
- [ ] 架構設計決策
  - [ ] 為何 User 與 Points 分開或合併
  - [ ] 其他重要的設計決策說明

---

## 開發注意事項

### 資料庫設計
- 確保 User、Product、Point、Order 等模型之間的關聯正確
- 考慮未來擴充性，避免過度設計

### 安全性考量
- 所有 API 都需要 JWT 驗證
- 敏感操作（如扣點）需要額外的權限檢查
- 避免 SQL Injection、XSS 等安全漏洞

### 效能考量
- 資料庫查詢優化（使用 `select_related`、`prefetch_related`）
- 避免 N+1 查詢問題
- 考慮快取機制（如需要）

### 程式碼品質
- 遵循 DRY（Don't Repeat Yourself）原則
- 適當的函數與類別命名
- 添加必要的註解與文件字串

---

## 進度追蹤

### Day 2 檢查點
- [x] JWT 登入 API 完成
- [x] Refresh Token 機制實作完成
- [x] 所有業務 API 權限掛載完成
- [x] 權限控制測試通過

### Day 3 檢查點
- [x] 商品 CRUD API 完成（已實作）
- [x] 商品權限控制實作完成（A 店家不能修改 B 店家的商品）
- [x] 儲值點數 API 完成

### Day 4 檢查點
- [x] 兌換商品 API 完成
- [x] 資料庫事務機制實作完成
- [x] 點數扣除邏輯測試通過

### Day 5 檢查點
- [x] API 文件化完成（為所有 API 添加 OpenAPI 註解）
- [x] 錯誤處理統一格式驗證完成

### Day 6 檢查點
- [x] 單元測試撰寫完成
- [ ] 程式碼格式化完成（待執行 Black）

### Day 7 檢查點
- [ ] README 文件完成
- [ ] 所有功能測試通過
- [ ] 專案交付準備完成

---

## 風險與應對

### 可能遇到的問題
1. **時間不足**：優先完成核心功能，次要功能可簡化
2. **技術難題**：預留時間查閱文件或尋求協助
3. **測試不完整**：至少確保核心業務邏輯有測試覆蓋

### 應對策略
- 每日檢視進度，適時調整優先順序
- 遇到問題及時記錄，避免重複踩坑
- 保持程式碼簡潔，避免過度優化

---

**最後更新**：Day 2 調整開發計畫，將 JWT 登入提前至第一階段，核心業務邏輯移至第二階段

**已完成項目**：
- Day 1: User 模型實作與環境設定
- Day 2: UserPoints 模型實作、Product 模型與 CRUD API 實作、JWT 認證整合
- Day 3: 商品權限控制實作、點數儲值 API 實作
- Day 4: 點數兌換 API 實作、資料庫事務機制、併發控制
- Day 5: API 文件化（drf-spectacular）、錯誤處理統一格式
- Day 6: 單元測試撰寫（認證、商品權限、點數儲值、點數兌換）
- 額外完成：用戶個人資料查詢 API（GET /api/users/me/）

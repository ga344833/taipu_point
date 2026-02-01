# PointExchange ViewSet 實作總結

## 實作內容

建立 `PointExchangeViewSet` 提供兌換紀錄的查詢與核銷功能，解決原本只有建立功能而無法查詢的問題。

## 功能實作

**API 端點**：
- `GET /api/points/exchanges/` - 查詢兌換紀錄列表
- `GET /api/points/exchanges/{id}/` - 查詢單一兌換紀錄
- `PATCH /api/points/exchanges/{id}/` - 核銷兌換紀錄
- `GET /api/points/exchanges/lookup-by-code/?code=EX...` - 根據交換序號查詢

**權限控制**：
- MEMBER：僅能查看自己的兌換紀錄
- STORE：僅能查看自己商品的兌換紀錄，可以核銷自己商品的兌換紀錄
- ADMIN：可以查看所有兌換紀錄，可以核銷任何兌換紀錄

## 技術要點

1. 查詢優化：使用 `select_related()` 避免 N+1 查詢
2. 權限設計：新增 `IsStoreOrAdmin` 權限類別
3. 狀態驗證：核銷時僅允許 PENDING → VERIFIED
4. 篩選功能：支援根據 `status` 和 `product` 篩選

## 相關檔案

- `apps/points/views/point_exchange_viewset.py`
- `apps/points/serializers/point_exchange_list_serializer.py`
- `core/permissions.py` - 新增 `IsStoreOrAdmin`

---

**實作日期**：2026-01-24

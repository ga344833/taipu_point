# Bug 修正：商品創建時 store 欄位必填問題

## 問題描述

創建商品時，API 要求 `store` 欄位必填，但理論上應由後端自動帶入當前登入的店家。

## 修正內容

### 1. Serializer 修正
- 將 `store` 欄位設為 `read_only=True`
- 更新 `help_text` 說明「後端自動代入，無需提供」

### 2. Model 說明更新
- 更新 `store` 欄位的 `help_text`，說明後端會自動代入

## 修正檔案

- `apps/products/serializers/product_serializer.py`
- `apps/products/models/product_model.py`

## 修正日期

2026-01-26

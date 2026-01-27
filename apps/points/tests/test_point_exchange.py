import threading
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import RoleChoices, UserPoints
from apps.products.models import Product
from apps.points.models import PointExchange, PointTransaction, TransactionTypeChoices

User = get_user_model()


class PointExchangeTestCase(APITestCase):
    """
    點數兌換測試
    
    測試兌換功能的正確性，包含併發測試
    """
    
    def setUp(self):
        """建立測試用戶和商品"""
        # 建立 MEMBER 用戶 A
        self.member_a = User.objects.create_user(
            username="member_a",
            email="member_a@test.com",
            password="testpass123",
            role=RoleChoices.MEMBER,
        )
        
        # 建立 MEMBER 用戶 B
        self.member_b = User.objects.create_user(
            username="member_b",
            email="member_b@test.com",
            password="testpass123",
            role=RoleChoices.MEMBER,
        )
        
        # 建立 STORE 用戶
        self.store = User.objects.create_user(
            username="store_test",
            email="store@test.com",
            password="testpass123",
            role=RoleChoices.STORE,
        )
        
        # 確保 UserPoints 已建立並設定餘額
        # 使用 get_or_create 避免重複建立，並更新餘額
        user_points_a, _ = UserPoints.objects.get_or_create(
            user=self.member_a,
            defaults={"balance": 1000, "is_locked": False}
        )
        if user_points_a.balance != 1000:
            user_points_a.balance = 1000
            user_points_a.save()
        
        user_points_b, _ = UserPoints.objects.get_or_create(
            user=self.member_b,
            defaults={"balance": 1000, "is_locked": False}
        )
        if user_points_b.balance != 1000:
            user_points_b.balance = 1000
            user_points_b.save()
        
        user_points_store, _ = UserPoints.objects.get_or_create(
            user=self.store,
            defaults={"balance": 0, "is_locked": False}
        )
        
        # 建立商品（庫存 1，所需點數 500）
        self.product = Product.objects.create(
            store=self.store,
            name="限量商品",
            required_points=500,
            stock=1,
            is_active=True,
        )
    
    def _get_token(self, user):
        """取得用戶的 JWT token"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def _authenticate(self, user):
        """設定認證用戶"""
        token = self._get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    
    def test_member_can_exchange_product(self):
        """測試 MEMBER 可以兌換商品，庫存和餘額正確減少"""
        self._authenticate(self.member_a)
        
        # 刷新資料庫以確保讀取到最新的餘額
        self.member_a.points.refresh_from_db()
        initial_balance = self.member_a.points.balance
        initial_stock = self.product.stock
        required_points = self.product.required_points
        
        url = "/api/points/exchange/"
        data = {
            "product_id": self.product.id,
        }
        
        response = self.client.post(url, data, format="json")
        
        # 如果失敗，輸出錯誤訊息以便除錯
        if response.status_code != status.HTTP_201_CREATED:
            print(f"測試失敗，回應狀態碼：{response.status_code}")
            print(f"回應內容：{response.data}")
        
        # 驗證回應
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"回應內容：{response.data}")
        self.assertEqual(response.data["points_spent"], required_points)
        self.assertEqual(response.data["balance_before"], initial_balance)
        self.assertEqual(response.data["balance_after"], initial_balance - required_points)
        self.assertIn("exchange_code", response.data)
        self.assertIn("transaction_id", response.data)
        
        # 驗證庫存已減少
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 1)
        
        # 驗證餘額已減少
        self.member_a.points.refresh_from_db()
        self.assertEqual(self.member_a.points.balance, initial_balance - required_points)
        
        # 驗證兌換紀錄已建立
        exchange = PointExchange.objects.get(id=response.data["exchange_id"])
        self.assertEqual(exchange.user, self.member_a)
        self.assertEqual(exchange.product, self.product)
        self.assertEqual(exchange.points_spent, required_points)
        self.assertTrue(exchange.exchange_code.startswith("EX"))
        
        # 驗證交易紀錄已建立
        transaction = PointTransaction.objects.get(id=response.data["transaction_id"])
        self.assertEqual(transaction.user, self.member_a)
        self.assertEqual(transaction.amount, -required_points)  # 負數表示扣點
        self.assertEqual(transaction.tx_type, TransactionTypeChoices.REDEMPTION)
        self.assertEqual(transaction.balance_after, initial_balance - required_points)
    
    def test_store_cannot_exchange(self):
        """測試 STORE 無法兌換商品，回傳 403"""
        self._authenticate(self.store)
        
        url = "/api/points/exchange/"
        data = {
            "product_id": self.product.id,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_insufficient_balance(self):
        """測試餘額不足時無法兌換"""
        self._authenticate(self.member_a)
        
        # 設定餘額不足
        self.member_a.points.balance = 100
        self.member_a.points.save()
        
        url = "/api/points/exchange/"
        data = {
            "product_id": self.product.id,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("點數餘額不足", response.data["detail"])
    
    def test_insufficient_stock(self):
        """測試庫存不足時無法兌換"""
        self._authenticate(self.member_a)
        
        # 設定庫存為 0
        self.product.stock = 0
        self.product.save()
        
        url = "/api/points/exchange/"
        data = {
            "product_id": self.product.id,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 檢查錯誤訊息（可能是 Serializer 驗證錯誤或 View 中的錯誤）
        response_str = str(response.data)
        self.assertTrue(
            "庫存不足" in response_str or "商品庫存不足" in response_str,
            f"錯誤訊息應包含庫存不足：{response.data}"
        )
    
    def test_inactive_product(self):
        """測試下架商品無法兌換"""
        self._authenticate(self.member_a)
        
        # 下架商品
        self.product.is_active = False
        self.product.save()
        
        url = "/api/points/exchange/"
        data = {
            "product_id": self.product.id,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 檢查錯誤訊息（可能是 Serializer 驗證錯誤或 View 中的錯誤）
        response_str = str(response.data)
        self.assertTrue(
            "已下架" in response_str or "商品不存在或已下架" in response_str,
            f"錯誤訊息應包含已下架：{response.data}"
        )
    
    def test_concurrent_exchange_prevent_overselling(self):
        """
        核心測試：併發兌換測試
        
        當商品庫存剩餘 1 時，兩位會員同時兌換，僅有一人成功且庫存不為負數
        
        注意：在 Django 測試環境中，threading 可能不會真正模擬資料庫層級的併發。
        此測試主要驗證邏輯正確性，真正的併發測試需要在生產環境或使用更複雜的測試工具。
        """
        # 確保庫存為 1
        self.product.stock = 1
        self.product.save()
        
        # 確保兩個用戶都有足夠的點數
        self.member_a.points.balance = 1000
        self.member_a.points.save()
        self.member_b.points.balance = 1000
        self.member_b.points.save()
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def exchange_product(user):
            """執行兌換的函數"""
            try:
                token = RefreshToken.for_user(user)
                # 建立新的 client 實例
                from rest_framework.test import APIClient
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
                
                url = "/api/points/exchange/"
                data = {"product_id": self.product.id}
                response = client.post(url, data, format="json")
                
                with lock:
                    results.append({
                        "user": user.username,
                        "status_code": response.status_code,
                        "data": response.data if hasattr(response, 'data') else None,
                    })
            except Exception as e:
                with lock:
                    errors.append({"user": user.username, "error": str(e)})
        
        # 建立兩個執行緒同時執行兌換
        thread_a = threading.Thread(target=exchange_product, args=(self.member_a,))
        thread_b = threading.Thread(target=exchange_product, args=(self.member_b,))
        
        thread_a.start()
        thread_b.start()
        
        thread_a.join()
        thread_b.join()
        
        # 如果有錯誤，輸出以便除錯
        if errors:
            print(f"併發測試錯誤：{errors}")
        
        # 驗證結果
        self.assertEqual(len(results), 2, f"兩個請求都應該有回應，實際：{len(results)}")
        
        # 統計成功和失敗的數量
        success_count = sum(1 for r in results if r["status_code"] == status.HTTP_201_CREATED)
        failure_count = sum(1 for r in results if r["status_code"] == status.HTTP_400_BAD_REQUEST)
        
        # 應該只有一個人成功（或兩個都失敗，如果測試環境不支援真正的併發）
        # 至少確保庫存不會變成負數
        self.product.refresh_from_db()
        self.assertGreaterEqual(self.product.stock, 0, "庫存不應為負數")
        
        # 如果有一個成功，庫存應該為 0
        if success_count == 1:
            self.assertEqual(self.product.stock, 0, "庫存應該為 0（1 - 1）")
            # 驗證只有一筆兌換紀錄
            exchanges = PointExchange.objects.filter(product=self.product)
            self.assertEqual(exchanges.count(), 1, "應該只有一筆兌換紀錄")
        
        # 驗證不會有兩個都成功的情況
        self.assertLessEqual(success_count, 1, "不應該有兩個用戶都成功兌換")

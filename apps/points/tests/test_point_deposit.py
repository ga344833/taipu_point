from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import RoleChoices, UserPoints
from apps.points.models import PointTransaction, TransactionTypeChoices

User = get_user_model()


class PointDepositTestCase(APITestCase):
    """
    點數儲值測試
    
    測試儲值功能的正確性，包含餘額更新和交易紀錄建立
    """
    
    def setUp(self):
        """建立測試用戶"""
        # 建立 MEMBER 用戶
        self.member = User.objects.create_user(
            username="member_test",
            email="member@test.com",
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
        
        # 確保 UserPoints 已建立（Signal 會自動建立）
        if not hasattr(self.member, 'points'):
            UserPoints.objects.create(user=self.member, balance=0)
        if not hasattr(self.store, 'points'):
            UserPoints.objects.create(user=self.store, balance=0)
    
    def _get_token(self, user):
        """取得用戶的 JWT token"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def _authenticate(self, user):
        """設定認證用戶"""
        token = self._get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    
    def test_member_can_deposit(self):
        """測試 MEMBER 可以儲值，餘額正確增加，且建立交易紀錄"""
        self._authenticate(self.member)
        
        initial_balance = self.member.points.balance
        deposit_amount = 1000
        
        url = "/api/points/deposit/"
        data = {
            "amount": deposit_amount,
        }
        
        response = self.client.post(url, data, format="json")
        
        # 驗證回應
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], deposit_amount)
        self.assertEqual(response.data["balance_before"], initial_balance)
        self.assertEqual(response.data["balance_after"], initial_balance + deposit_amount)
        self.assertIn("transaction_id", response.data)
        
        # 驗證餘額已更新
        self.member.points.refresh_from_db()
        self.assertEqual(self.member.points.balance, initial_balance + deposit_amount)
        
        # 驗證交易紀錄已建立
        transaction = PointTransaction.objects.get(id=response.data["transaction_id"])
        self.assertEqual(transaction.user, self.member)
        self.assertEqual(transaction.amount, deposit_amount)
        self.assertEqual(transaction.tx_type, TransactionTypeChoices.DEPOSIT)
        self.assertTrue(transaction.is_success)
        self.assertEqual(transaction.balance_after, initial_balance + deposit_amount)
    
    def test_store_cannot_deposit(self):
        """測試 STORE 無法儲值，回傳 403"""
        self._authenticate(self.store)
        
        url = "/api/points/deposit/"
        data = {
            "amount": 1000,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
    
    def test_anonymous_cannot_deposit(self):
        """測試未登入用戶無法儲值，回傳 401"""
        url = "/api/points/deposit/"
        data = {
            "amount": 1000,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_deposit_amount_must_be_positive(self):
        """測試儲值金額必須大於 0"""
        self._authenticate(self.member)
        
        url = "/api/points/deposit/"
        data = {
            "amount": 0,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_deposit_with_memo(self):
        """測試儲值時可以加入備註"""
        self._authenticate(self.member)
        
        initial_balance = self.member.points.balance
        deposit_amount = 500
        memo = "測試儲值備註"
        
        url = "/api/points/deposit/"
        data = {
            "amount": deposit_amount,
            "memo": memo,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 驗證備註已記錄
        transaction = PointTransaction.objects.get(id=response.data["transaction_id"])
        self.assertEqual(transaction.memo, memo)
    
    def test_multiple_deposits(self):
        """測試多次儲值，餘額累積正確"""
        self._authenticate(self.member)
        
        initial_balance = self.member.points.balance
        
        # 第一次儲值
        url = "/api/points/deposit/"
        response1 = self.client.post(url, {"amount": 500}, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # 第二次儲值
        response2 = self.client.post(url, {"amount": 300}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # 驗證最終餘額
        self.member.points.refresh_from_db()
        self.assertEqual(
            self.member.points.balance,
            initial_balance + 500 + 300
        )
        
        # 驗證有兩筆交易紀錄
        transactions = PointTransaction.objects.filter(user=self.member)
        self.assertEqual(transactions.count(), 2)

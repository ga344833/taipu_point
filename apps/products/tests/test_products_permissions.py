from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import RoleChoices
from apps.products.models import Product

User = get_user_model()


class ProductPermissionsTestCase(APITestCase):
    """
    商品權限測試
    
    測試不同角色對商品 API 的存取權限
    """
    
    def setUp(self):
        """建立測試用戶和商品"""
        # 建立 MEMBER 用戶
        self.member = User.objects.create_user(
            username="member_test",
            email="member@test.com",
            password="testpass123",
            role=RoleChoices.MEMBER,
        )
        
        # 建立 STORE A 用戶
        self.store_a = User.objects.create_user(
            username="store_a",
            email="store_a@test.com",
            password="testpass123",
            role=RoleChoices.STORE,
        )
        
        # 建立 STORE B 用戶
        self.store_b = User.objects.create_user(
            username="store_b",
            email="store_b@test.com",
            password="testpass123",
            role=RoleChoices.STORE,
        )
        
        # 建立 ADMIN 用戶
        self.admin = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role=RoleChoices.ADMIN,
        )
        
        # 建立 STORE A 的商品
        self.product_store_a = Product.objects.create(
            store=self.store_a,
            name="Store A Product",
            required_points=100,
            stock=50,
            is_active=True,
        )
        
        # 建立 STORE B 的商品
        self.product_store_b = Product.objects.create(
            store=self.store_b,
            name="Store B Product",
            required_points=200,
            stock=30,
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
    
    def test_anonymous_can_list_products(self):
        """測試匿名用戶可以查詢商品列表"""
        url = "/api/products/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 如果沒有 page 參數，分頁器會返回所有資料（list）
        # 如果有 page 參數，會返回分頁格式（dict with "results"）
        if isinstance(response.data, list):
            self.assertGreaterEqual(len(response.data), 2)
        else:
            self.assertGreaterEqual(len(response.data["results"]), 2)
    
    def test_anonymous_can_retrieve_product(self):
        """測試匿名用戶可以查詢單一商品"""
        url = f"/api/products/{self.product_store_a.id}/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Store A Product")
    
    def test_member_cannot_create_product(self):
        """測試 MEMBER 無法建立商品，回傳 403"""
        self._authenticate(self.member)
        
        url = "/api/products/"
        data = {
            "name": "Member Product",
            "required_points": 50,
            "stock": 10,
            "is_active": True,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_store_can_create_product(self):
        """測試 STORE 可以建立商品，回傳 201，store 自動帶入"""
        self._authenticate(self.store_a)
        
        url = "/api/products/"
        data = {
            "name": "New Store A Product",
            "required_points": 150,
            "stock": 20,
            "is_active": True,
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Store A Product")
        # 驗證 store 自動帶入
        self.assertEqual(response.data["store"], self.store_a.id)
    
    def test_store_a_cannot_update_store_b_product(self):
        """測試 STORE A 無法修改 STORE B 的商品，回傳 403"""
        self._authenticate(self.store_a)
        
        url = f"/api/products/{self.product_store_b.id}/"
        data = {
            "name": "Hacked Product",
        }
        
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_store_a_can_update_own_product(self):
        """測試 STORE A 可以修改自己的商品，回傳 200"""
        self._authenticate(self.store_a)
        
        url = f"/api/products/{self.product_store_a.id}/"
        data = {
            "name": "Updated Store A Product",
        }
        
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Store A Product")
    
    def test_admin_can_delete_any_product(self):
        """測試 ADMIN 可以刪除任何店家的商品，回傳 204（軟刪除）"""
        self._authenticate(self.admin)
        
        url = f"/api/products/{self.product_store_a.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 驗證商品已軟刪除（is_active = False）
        product = Product.objects.get(id=self.product_store_a.id)
        self.assertFalse(product.is_active)

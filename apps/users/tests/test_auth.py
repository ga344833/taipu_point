from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import RoleChoices

User = get_user_model()


class AuthTestCase(APITestCase):
    """
    認證測試
    
    測試登入、Token 取得等功能
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
        
        # 建立 ADMIN 用戶
        self.admin = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role=RoleChoices.ADMIN,
        )
    
    def test_login_success(self):
        """測試登入成功，回傳 200 並取得 access token"""
        url = "/api/auth/token/"
        data = {
            "username": "member_test",
            "password": "testpass123",
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIsInstance(response.data["access"], str)
        self.assertIsInstance(response.data["refresh"], str)
    
    def test_login_with_wrong_password(self):
        """測試錯誤密碼登入失敗"""
        url = "/api/auth/token/"
        data = {
            "username": "member_test",
            "password": "wrongpassword",
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_nonexistent_user(self):
        """測試不存在的用戶登入失敗"""
        url = "/api/auth/token/"
        data = {
            "username": "nonexistent",
            "password": "testpass123",
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """測試 Token 刷新功能"""
        # 先登入取得 token
        login_url = "/api/auth/token/"
        login_data = {
            "username": "member_test",
            "password": "testpass123",
        }
        login_response = self.client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]
        
        # 使用 refresh token 取得新的 access token
        refresh_url = "/api/auth/token/refresh/"
        refresh_data = {
            "refresh": refresh_token,
        }
        
        response = self.client.post(refresh_url, refresh_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

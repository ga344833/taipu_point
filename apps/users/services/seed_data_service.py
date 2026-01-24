"""
預設資料建立服務

用於建立測試環境所需的預設帳號（管理者、商家、一般會員）。
"""

from django.contrib.auth import get_user_model
from apps.users.models import RoleChoices, UserPoints

User = get_user_model()


class SeedDataService:
    """預設資料建立服務類別"""

    # 預設帳號配置
    DEFAULT_ACCOUNTS = [
        {
            "username": "admin",
            "email": "admin@gmail.com",
            "password": "admin12345!",
            "role": RoleChoices.ADMIN,
            "is_superuser": True,
            "is_staff": True,
        },
        {
            "username": "teststore",
            "email": "teststore@gmail.com",
            "password": "store123!",
            "role": RoleChoices.STORE,
            "is_superuser": False,
            "is_staff": False,
        },
        {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "user123!",
            "role": RoleChoices.MEMBER,
            "is_superuser": False,
            "is_staff": False,
        },
    ]

    @classmethod
    def create_default_accounts(cls):
        """
        建立預設測試帳號
        
        Returns:
            dict: 包含建立結果的字典
                - created: 成功建立的帳號列表
                - skipped: 已存在而跳過的帳號列表
                - errors: 建立失敗的帳號列表（含錯誤訊息）
        """
        result = {
            "created": [],
            "skipped": [],
            "errors": [],
        }

        for account_config in cls.DEFAULT_ACCOUNTS:
            username = account_config["username"]
            
            # 檢查帳號是否已存在
            if User.objects.filter(username=username).exists():
                result["skipped"].append({
                    "username": username,
                    "reason": "帳號已存在",
                })
                continue

            try:
                # 建立帳號
                if account_config.get("is_superuser"):
                    # 使用 create_superuser 建立管理員
                    user = User.objects.create_superuser(
                        username=account_config["username"],
                        email=account_config["email"],
                        password=account_config["password"],
                        role=account_config["role"],
                    )
                else:
                    # 使用 create_user 建立一般使用者
                    user = User.objects.create_user(
                        username=account_config["username"],
                        email=account_config["email"],
                        password=account_config["password"],
                        role=account_config["role"],
                    )

                # 驗證 UserPoints 是否自動建立（Signal 應該會自動觸發）
                # 由於 Signal 是同步執行，create_user 返回後應該已經建立
                user_points, created = UserPoints.objects.get_or_create(
                    user=user,
                    defaults={
                        "balance": 0,
                        "is_locked": False,
                    }
                )

                result["created"].append({
                    "username": username,
                    "role": account_config["role"],
                    "email": account_config["email"],
                    "userpoints_created": not created,  # created=False 表示已存在（Signal 觸發）
                })

            except Exception as e:
                result["errors"].append({
                    "username": username,
                    "error": str(e),
                })

        return result

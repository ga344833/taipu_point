"""
建立預設測試帳號的 Django 管理指令

使用方式：
    python manage.py seed_data

此指令會建立以下預設帳號：
- admin / admin12345! (ADMIN)
- teststore / store123! (STORE)
- testuser / user123! (MEMBER)

如果帳號已存在，則會跳過建立。
"""

from django.core.management.base import BaseCommand
from apps.users.services.seed_data_service import SeedDataService


class Command(BaseCommand):
    help = "建立預設測試帳號（管理者、商家、一般會員）"

    def handle(self, *args, **options):
        """執行預設資料建立"""
        self.stdout.write(self.style.SUCCESS("開始建立預設測試帳號..."))

        # 呼叫服務層建立帳號
        result = SeedDataService.create_default_accounts()

        # 輸出結果
        if result["created"]:
            self.stdout.write(
                self.style.SUCCESS(f"\n成功建立 {len(result['created'])} 個帳號：")
            )
            for account in result["created"]:
                self.stdout.write(
                    f"  ✓ {account['username']} ({account['role']}) - {account['email']}"
                )
                if not account["userpoints_created"]:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    警告：UserPoints 未自動建立，已手動建立"
                        )
                    )

        if result["skipped"]:
            self.stdout.write(
                self.style.WARNING(f"\n跳過 {len(result['skipped'])} 個已存在的帳號：")
            )
            for account in result["skipped"]:
                self.stdout.write(
                    f"  ⊘ {account['username']} - {account['reason']}"
                )

        if result["errors"]:
            self.stdout.write(
                self.style.ERROR(f"\n建立失敗 {len(result['errors'])} 個帳號：")
            )
            for error in result["errors"]:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {error['username']} - {error['error']}")
                )

        # 總結
        total = len(result["created"]) + len(result["skipped"]) + len(result["errors"])
        if total > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n完成！總共處理 {total} 個帳號："
                    f"成功 {len(result['created'])} 個，"
                    f"跳過 {len(result['skipped'])} 個，"
                    f"失敗 {len(result['errors'])} 個"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("沒有需要建立的帳號"))

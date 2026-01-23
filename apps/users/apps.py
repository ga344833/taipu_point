from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "用戶管理"
    
    def ready(self):
        """載入 signals"""
        import apps.users.signals  # noqa



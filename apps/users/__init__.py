# 不要在 __init__.py 中導入模型，避免 AppRegistryNotReady 錯誤
# 需要時請直接從 apps.users.models 導入：
# from apps.users.models import User, RoleChoices

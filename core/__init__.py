# Core module
# 
# 注意：不在 __init__.py 中直接導入 permissions，避免 Django 初始化時的循環導入問題
# 使用時請直接從 core.permissions 導入：
#   from core.permissions import IsStore, IsAdmin, IsProductOwner

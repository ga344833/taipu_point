from rest_framework import permissions
from apps.users.models import RoleChoices


class IsStore(permissions.BasePermission):
    """
    僅允許 role=STORE 的用戶操作
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == RoleChoices.STORE


class IsAdmin(permissions.BasePermission):
    """
    僅允許 role=ADMIN 的用戶操作
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == RoleChoices.ADMIN


class IsProductOwner(permissions.BasePermission):
    """
    僅允許商品所屬店家進行修改
    
    用於商品更新、刪除等操作，確保只有商品擁有者可以修改自己的商品。
    管理者可以操作任何商品。
    """
    
    def has_object_permission(self, request, view, obj):
        # 讀取操作允許所有人
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 未登入用戶不允許修改
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 管理者可以操作任何商品
        if request.user.role == RoleChoices.ADMIN:
            return True
        
        # 檢查是否為商品擁有者
        return obj.store == request.user

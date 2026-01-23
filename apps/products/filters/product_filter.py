import django_filters
from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    """
    商品篩選器
    
    提供商品列表的篩選功能。
    """
    
    store = django_filters.NumberFilter(
        field_name="store",
        help_text="依店家 ID 篩選",
    )
    
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        help_text="依上架狀態篩選",
    )
    
    required_points_min = django_filters.NumberFilter(
        field_name="required_points",
        lookup_expr="gte",
        help_text="最低兌換點數",
    )
    
    required_points_max = django_filters.NumberFilter(
        field_name="required_points",
        lookup_expr="lte",
        help_text="最高兌換點數",
    )
    
    class Meta:
        model = Product
        fields = ["store", "is_active"]

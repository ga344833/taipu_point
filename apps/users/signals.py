from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserPoints


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    """
    當 User 建立時，自動建立對應的 UserPoints 紀錄
    
    使用 get_or_create 避免重複建立，確保每個 User 都有唯一的點數錢包。
    """
    if created:
        UserPoints.objects.get_or_create(
            user=instance,
            defaults={
                "balance": 0,
                "is_locked": False,
            }
        )

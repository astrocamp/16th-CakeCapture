from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import *


@receiver(post_save, sender=User)
def create_user_chatroom(sender, instance, created, **kwargs):

    if created:
        group = ChatGroup.objects.create(
            group_name=f"{instance.username}-service",
        )

        User = get_user_model()
        admin_user = User.objects.get(username="admin")
        welcome_message = "歡迎來到 Cake Capture，這邊贈予您首次註冊的 50 元折價券，折購代碼為 5XCAMP。"

        GroupMessage.objects.create(
            group=group,
            author=admin_user,
            body=welcome_message,
        )

        ChatGroupMember.objects.create(group=group, user=instance)
        ChatGroupMember.objects.create(group=group, user=admin_user)

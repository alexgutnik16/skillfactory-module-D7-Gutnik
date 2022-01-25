from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Post
from .tasks import news_post_email


@receiver(m2m_changed, sender=Post.post_category.through)
def notify_subscribers(sender, instance, **kwargs):
    news_post_email(instance)

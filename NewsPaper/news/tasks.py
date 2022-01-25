from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Post


@shared_task
def news_post_email(instance):
    text = instance.text[:50] + '...'
    for category in instance.post_category.all():
        for user in category.subscribers.all():
            send_mail(
                subject=f'Привет, {user.username}, новый пост в категории {category.category_name}!',
                message=text,
                from_email='alexvgutnik@yandex.ru',
                recipient_list=[user.email],
                )


@shared_task
def send_weekly_mails():
    latest_posts = []
    latest_posts_categories = []

    d = datetime.now().strftime("%d.%m.%Y")
    now = datetime.strptime(d, "%d.%m.%Y")

    for post in Post.objects.all():
        p = post.creation_date.strftime("%d.%m.%Y")
        post_created = datetime.strptime(p, "%d.%m.%Y")
        if (now-post_created).days <= 7:
            latest_posts.append(post)
            for cat in post.post_category.all():
                if cat not in latest_posts_categories:
                    latest_posts_categories.append(cat)

    week_ago = now.date() - timedelta(days=7)

    for category in latest_posts_categories:
        for user in category.subscribers.all():
            send_mail(
                subject=f'Привет, {user.username}, все посты за неделю в категории {category.category_name}!',
                message=f'http://127.0.0.1:8000/news/search/?creation_date__gt={week_ago}&heading__icontains=&author__author_user__username__icontains=&post_category__category_name__icontains={category.category_name}',
                from_email='alexvgutnik@yandex.ru',
                recipient_list=[user.email],
                )

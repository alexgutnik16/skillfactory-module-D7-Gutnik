import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail
from news.models import Post
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


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


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_mails,
            trigger=CronTrigger(day_of_week="mon", hour="12", minute="00"),
            id="send_weekly_mails",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_mails'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="21", minute="14"
            ),

            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

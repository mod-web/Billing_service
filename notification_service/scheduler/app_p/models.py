import uuid
from django.db import models
from django_celery_beat.models import PeriodicTask
from django.utils.translation import gettext_lazy as _


class NotificationSendStatus(models.TextChoices):
    PENDING = 'pending', _('pending')
    PROCESSING = 'processing', _('processing')
    DONE = 'done', _('done')


class UUIDMixin(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NotificationType(models.TextChoices):
    EMAIL = "email", _('email')
    SMS = "sms", _('sms')
    PUSH = "push", _('push')


class NotificationTemplate(models.TextChoices):
    GREETINGS = '1', '1'
    NEW_EDISODE = '2', '2'
    LIKES = '3', '3'
    NEWS = '4', '4'


class Group(models.TextChoices):
    GUEST = 'GUEST', _('GUEST')
    SUBSCRIBER = 'SUBSCRIBER', _('SUBSCRIBER')
    PRIVELEGED = 'PRIVELEGED', _('PRIVELEGED')


class Notification(UUIDMixin, PeriodicTask):

    template_id = models.CharField(
        "template",
        choices=NotificationTemplate.choices,
        default=NotificationTemplate.GREETINGS,
    )
    group_id = models.CharField("group", choices=Group.choices, default=Group.GUEST)
    type_sender = models.CharField("type_sender", choices=NotificationType.choices, default=NotificationType.EMAIL,
                                   max_length=10)
    title = models.TextField('title', max_length=256)
    send_status = models.CharField('Send status', max_length=50, choices=NotificationSendStatus.choices,
                                   default=NotificationSendStatus.PENDING)
    time_from = models.TimeField("Time from")
    time_to = models.TimeField("Time to")
    date_to_send = models.DateField("Date to send")

    class Meta:
        db_table = 'notifications"."notifications'
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'

    def __str__(self):
        return self.name

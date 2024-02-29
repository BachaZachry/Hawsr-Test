import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class NOTIFICATION_STATUS(models.IntegerChoices):
    PENDING = 1, "Pending"
    SCHEDULED = 2, "Scheduled"
    IN_PROGRESS = 3, "In Progress"
    SENT = 4, "Sent"
    RECEIVED = 5, "Received"
    FAILED = 6, "Failed"
    DELAYED = 7, "Delayed"


class NOTIFICATION_TYPE(models.IntegerChoices):
    ANNOUNCEMENT = 1, "Announcement"
    REMINDER = 2, "Reminder"
    ADVERTISMENT = 3, "Advertisment"
    NOTIFICATION = 4, "Notification"
    WARNING = 5, "Warning"


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["created"]


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    phone_regex = RegexValidator(
        regex=r"^\+\d{9,25}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 25 digits allowed.",
    )
    phone = models.CharField(max_length=25, blank=True, validators=[phone_regex])
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.phone if self.phone else self.email


class NotificationTemplates(BaseModel):
    message_type = models.IntegerField(
        choices=NOTIFICATION_TYPE.choices, default=NOTIFICATION_TYPE.ANNOUNCEMENT
    )
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=255)
    file = models.FileField(upload_to="notification_files")

    def __str__(self):
        return f"{self.subject}"


class Notification(BaseModel):
    message_type = models.IntegerField(
        choices=NOTIFICATION_TYPE.choices,
        default=NOTIFICATION_TYPE.ANNOUNCEMENT,
        db_index=True,
    )
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=255)
    send_date = models.DateTimeField(default=timezone.now, db_index=True)
    file = models.FileField(upload_to="notification_files")

    def __str__(self):
        return f"{self.subject}"


class UserNotification(BaseModel):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=NOTIFICATION_STATUS.choices,
        default=NOTIFICATION_STATUS.PENDING,
        db_index=True,
    )

    def __str__(self):
        return f"{self.notification}: {self.user}"

    class Meta:
        unique_together = ("user", "notification")

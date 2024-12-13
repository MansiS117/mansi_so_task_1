from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import TimeStampedModel

from .managers import CustomManager


# Create your models here.
class User(AbstractUser, TimeStampedModel):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomManager()

    def __str__(self):
        return self.email


PRIORITY_CHOICES = [
    ("high", "High"),
    ("low", "Low"),
    ("medium", "Medium"),
]


STATUS_CHOICES = [
    ("inprogress", "Inprogress"),
    ("completed", "Completed"),
]


class Task(TimeStampedModel):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_task",
    )
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    assigned_at = models.DateField(auto_now_add=True)
    priority = models.CharField(
        max_length=50, choices=PRIORITY_CHOICES, default="high"
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="inprogress"
    )

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    content = models.TextField()
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

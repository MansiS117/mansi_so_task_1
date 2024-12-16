from django.conf import settings
from django.core.mail import send_mail


def send_task_email(task):
    assignee = task.assigned_by
    subject = f"New Task Assigned: {task.title}"
    message = (
        f"You have been assigned a new task: {task.title} with {task.priority} priority"
        f"The task should be submitted by {task.due_date}"

    )
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [assignee.email],
        fail_silently=False,
    )


def task_update_email(task):
    subject = "Task Status Update"
    message = f"The task {task} is {task.status}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [task.assigned_by.email]
    send_mail(subject, message, email_from, recipient_list)

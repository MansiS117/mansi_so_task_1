from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from .forms import CommentForm, MyTaskForm, RegistrationForm, TaskForm
from .models import Comment, Task, User

# Create your views here.


class RegistrationView(View):
    template_name = "register.html"

    def get(self, request):
        form = RegistrationForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # prevents saving user to database
            user = form.save(commit=False)
            # fetches password and confirm_password from cleaned_data dictionary
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()
            messages.success(request, "Registration Successful")
            return redirect("home")
        messages.error(request, "Registration Failed")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect("home")

        messages.error(request, "Invalid login credentials")
        return render(request, self.template_name)


class LogoutView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        logout(request)
        messages.success(request, "You are logged out")
        return redirect("home")


class TaskListView(View):
    template_name = "index.html"

    def get(self, request):
        if request.user.is_authenticated:
            tasks = Task.objects.filter(assigned_by=request.user)
            context = {"tasks": tasks}
            return render(request, self.template_name, context)
        messages.error(request, "You need to log in first")
        return render(request, self.template_name)


class TaskCreateView(LoginRequiredMixin, View):
    template_name = "create_task.html"
    login_url = "/login/"

    def get(self, request):
        form = TaskForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = TaskForm(request.POST)
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        assigned_to = request.POST.get("assigned_to")
        priority = request.POST.get("priority")

        if form.is_valid():
            task = form.save(commit=False)
            assigned_by = request.user
            assigned_to = User.objects.get(id=assigned_to)

            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                assigned_to=assigned_to,
                assigned_by=assigned_by,
                priority=priority,
            )
            task.save()
            subject = "New Task Assigned"
            message = f"""Task: {title}, Description: {description}, Assigned By: {assigned_by}, Priority: {priority}, Due Date: {due_date}, """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [assigned_to.email]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Task created sucessfully")
            return redirect("home")
        messages.error(request, "Try again")
        return render(request, self.template_name, {"form": form})


class TaskEditView(LoginRequiredMixin, View):
    template_name = "create_task.html"
    login_url = "/login/"

    def get(self, request, task_id):
        task = Task.objects.get(id=task_id)
        form = TaskForm(instance=task)
        return render(request, self.template_name, {"form": form})

    def post(self, request, task_id):
        task = Task.objects.get(id=task_id)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("home")
        messages.error(request, "Try again")
        return render(request, self.template_name, {"form": form})


class TaskDeleteView(LoginRequiredMixin, View):
    template_name = "index.html"
    login_url = "/login/"

    def post(self, request, task_id):
        task = Task.objects.get(id=task_id)
        if task:
            task.delete()
            messages.success(request, "Task deleted successfully")
        else:
            messages.error(request, "item does not exist")
        return redirect("home")


class MyTaskView(View):
    template_name = "my_task.html"

    def get(self, request):
        if request.user.is_authenticated:
            tasks = Task.objects.filter(assigned_to=request.user)
            context = {"tasks": tasks}
            return render(request, self.template_name, context)
        messages.error(request, "You need to log in ")
        return redirect("login")


class UpdateMyTaskView(View):
    template_name = "update_mytask.html"

    def get(self, request, task_id):
        if request.user.is_authenticated:
            task = Task.objects.get(id=task_id)
            if task:
                form = MyTaskForm(instance=task)
                title = task.title
                return render(
                    request, self.template_name, {"form": form, "title": title}
                )
            messages.error(request, "Task not found")
            return redirect("home")
        messages.error(request, "You need to login")
        return redirect("home")

    def post(self, request, task_id):
        if request.user.is_authenticated:
            task = Task.objects.get(id=task_id)
            if task:
                form = MyTaskForm(request.POST, instance=task)
                if form.is_valid():
                    task.status = request.POST.get("status")
                    if task.status == "completed":
                        task.complete = True
                    else:
                        task.complete = False
                    task.save()
                    subject = "Task Status Update"
                    message = f"The task {task} is {task.status}"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [task.assigned_by.email]
                    send_mail(subject, message, email_from, recipient_list)
                    return redirect("my_task")
            messages.error(request, "Task not found")

        messages.error(request, "You need to login")
        return redirect("home")


class TaskDetailView(LoginRequiredMixin, View):
    template_name = "task_detail.html"
    login_url = "/login/"

    def get(self, request, task_id):
        task = Task.objects.get(id=task_id)
        comments = Comment.objects.filter(task=task)
        form = CommentForm()
        context = {"task": task, "comments": comments, "form": form}
        return render(request, self.template_name, context)

    def post(self, request, task_id):
        task = Task.objects.get(id=task_id)
        form = CommentForm(request.POST)

        if form.is_valid():
            content = form.save(commit=False)
            content.commented_by = request.user
            content.task = task
            content.save()
            return redirect("home")
        comments = Comment.objects.filter(task=task)
        context = {"task": task, "comments": comments, "form": form}
        return render(request, self.template_name, context)


class SearchView(LoginRequiredMixin, View):
    template_name = "all_task.html"
    login_url = "/login/"

    def get(self, request):
        keyword = request.GET.get("keyword", "")

        if keyword:
            task_by_status = Task.objects.filter(Q(status__icontains=keyword))
            if task_by_status.exists():
                tasks = task_by_status
            else:
                task_by_assignee = Task.objects.filter(
                    assigned_by__first_name__icontains=keyword
                )

                if task_by_assignee.exists():
                    tasks = task_by_assignee

                else:
                    tasks = Task.objects.filter(due_date__icontains=keyword)

        context = {"tasks": tasks, "keyword": keyword}
        return render(request, self.template_name, context)


class AllTaskView(LoginRequiredMixin, View):
    login_url = "/login/"
    template_name = "all_task.html"

    def get(self, request):
        tasks = Task.objects.all()
        return render(request, self.template_name, {"tasks": tasks})

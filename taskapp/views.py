from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from .forms import CommentForm, MyTaskForm, RegistrationForm, TaskForm
from .models import Comment, Task, User
from .utils import send_task_email, task_update_email


class RegistrationView(View):
    """
    A view for handling user registration. It handles both GET and POST request """

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
    """
    A view for handling user Login. It handles both GET and POST request """

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
    """
    A view for handling user logout """

    login_url = "/login/"

    def get(self, request):
        logout(request)
        messages.success(request, "You are logged out")
        return redirect("home")


class TaskListView(LoginRequiredMixin, View):
    """
    A view for rendering all the task that is assigned by the authenticated user """

    login_url = "/login/"
    template_name = "index.html"

    def get(self, request):
        tasks = Task.objects.filter(assigned_by=request.user)
        context = {"tasks": tasks}
        return render(request, self.template_name, context)


class TaskCreateView(LoginRequiredMixin, View):
    """
    A view for creating a new task """

    template_name = "create_task.html"
    login_url = "/login/"

    def get(self, request):
        form = TaskForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = TaskForm(request.POST)
        assigned_to = request.POST.get("assigned_to")

        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.assigned_to = User.objects.filter(id=assigned_to).first()
            task.save()
            send_task_email(task)
            messages.success(request, "Task created sucessfully")
            return redirect("home")
        messages.error(request, "Try again")
        return render(request, self.template_name, {"form": form})


class TaskEditView(LoginRequiredMixin, View):
    """
    A view for updating a task """

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
    """
    A view for deleting task """

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


class MyTaskView(LoginRequiredMixin, View):
    """
    A view that renders the task that are assigned to the requested user """

    login_url = "/login/"
    template_name = "my_task.html"

    def get(self, request):
        completed_task = (
            Task.objects.filter(assigned_to=request.user)
            .filter(complete=True)
            .order_by("id")
        )
        current_task = Task.objects.filter(
            Q(assigned_to=request.user) & Q(complete=False)
        ).first()
        if current_task:
            incomplete_task = (
                Task.objects.filter(
                    Q(assigned_to=request.user) & Q(complete=False)
                )
                .exclude(id=current_task.id)
                .order_by("id")
            )
        else:
            incomplete_task = Task.objects.filter(
                Q(assigned_to=request.user) & Q(complete=False)
            ).order_by("id")
        context = {
            "completed_task": completed_task,
            "incomplete_task": incomplete_task,
            "current_task": current_task,
        }
        return render(request, self.template_name, context)


class UpdateMyTaskView(LoginRequiredMixin, View):
    """
    A view where the requested user can change the status of the task assigned to them """

    login_url = "/login/"
    template_name = "update_mytask.html"

    def get(self, request, task_id):
        task = Task.objects.filter(id=task_id).first()
        if task:
            form = MyTaskForm(instance=task)
            title = task.title
            return render(
                request, self.template_name, {"form": form, "title": title}
            )
        messages.error(request, "Task not found")
        return redirect("home")

    def post(self, request, task_id):
        task = Task.objects.filter(id=task_id).first()
        previous_task = Task.objects.filter(
            Q(id__lt=task.id) & Q(assigned_to=request.user)
        ).last()
        if not previous_task or previous_task.complete:
            form = MyTaskForm(request.POST, instance=task)
            if form.is_valid():
                task.status = request.POST.get("status")
                if task.status == "completed":
                    task.complete = True
                else:
                    task.complete = False
                task.save()
                task_update_email(task)
                return redirect("my_task")

        messages.error(
            request,
            f"You cannot update this task until the previous task '{previous_task.title}' is completed",
        )
        return render(request, self.template_name)


class TaskDetailView(LoginRequiredMixin, View):
    """
    A view that renders detailed information about the task """

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
    """
    A view that renders task based on the search, the search could be done by status, due date or the task assignee """

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
    """
    A view that renders all the tasks """

    login_url = "/login/"
    template_name = "all_task.html"

    def get(self, request):
        tasks = Task.objects.all()
        return render(request, self.template_name, {"tasks": tasks})

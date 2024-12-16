from django.urls import path

from .views import (
    AllTaskView,
    LoginView,
    LogoutView,
    MyTaskView,
    RegistrationView,
    SearchView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskEditView,
    TaskListView,
    UpdateMyTaskView,
)

urlpatterns = [
    path("", TaskListView.as_view(), name="home"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/", TaskCreateView.as_view(), name="create_task"),
    path("edit/<int:task_id>/", TaskEditView.as_view(), name="edit_task"),
    path("delete/<int:task_id>/", TaskDeleteView.as_view(), name="delete_task"),
    path("mytask/", MyTaskView.as_view(), name="my_task"),
    path("updatetask/<int:task_id>", UpdateMyTaskView.as_view(), name="update_mytask"),
    path("detail/<int:task_id>", TaskDetailView.as_view(), name="task_detail"),
    path("search/", SearchView.as_view(), name="search"),
    path("tasks", AllTaskView.as_view(), name="all_task"),
]

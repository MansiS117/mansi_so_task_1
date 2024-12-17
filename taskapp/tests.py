from django.test import Client, TestCase
from django.urls import reverse

from .models import Comment, Task, User


class TestCreateTask(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.url = reverse("create_task")

    def test_task_create_get(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "create_task.html")

    def test_task_create_get_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_task_creation(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        task = {
            "title": "task1",
            "description": "This is task 1",
            "assigned_to": self.user2.id,
            "assigned_by": self.user.id,
            "due_date": "2024-12-24",
            "priority": "high",
        }
        response = self.client.post(self.url, task)
        self.assertRedirects(response, reverse("home"))

    def test_create_task_invalid_form(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.post(reverse("create_task"), {})
        self.assertContains(response, "Try again")


class TestEditTask(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.task = Task.objects.create(
            title="test task",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
        )
        self.url = reverse("edit_task", args=[self.task.id])

    def test_edit_task_get(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "create_task.html")

    def test_edit_task_get_unauthenicated(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_edit_task(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        data = {
            "title": "Updated title",
            "description": "Updated task",
            "due_date": "2024-12-25",
            "assigned_to": self.user2.id,
            "assigned_by": self.user.id,
            "priority": "high",
        }
        response = self.client.post(self.url, data)
        self.task.refresh_from_db()
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.task.title, "Updated title")


class TestDeleteTask(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.task = Task.objects.create(
            title="test task",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
        )
        self.url = reverse("delete_task", args=[self.task.id])

    def test_delete_task(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.post(self.url)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
        self.assertRedirects(response, reverse("home"))


class TestMyTaskView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.url = reverse("my_task")

    def test_my_task_authenticated(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_task.html")

    def test_my_task_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)


class TestUpdateMyTaskView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.task = Task.objects.create(
            title="test task",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
        )
        self.url = reverse("update_mytask", args=[self.task.id])

    def test_update_task_status_get(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "update_mytask.html")

    def test_update_task_status(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.post(self.url, {"status": "completed"})
        self.task.refresh_from_db()
        self.assertRedirects(response, reverse("my_task"))
        self.assertTrue(self.task.complete)


class TestTaskDetailView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.task = Task.objects.create(
            title="test task",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
        )
        self.url = reverse("task_detail", args=[self.task.id])

    def test_view_task_detail(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "task_detail.html")
        self.assertEqual(Comment.objects.filter(id=self.task.id).count(), 0)

    def test_post_view_task_detail(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.post(self.url, {"content": "This is a comment"})
        self.assertEqual(Comment.objects.filter(task=self.task.id).count(), 1)
        self.assertRedirects(response, reverse("home"))


class TestSearchView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com",
            password="12345",
            first_name="test user",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.user3 = User.objects.create_user(
            email="testuser3@gmail.com", password="1234"
        )
        self.task1 = Task.objects.create(
            title="test task 1",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
            status="In progress",
        )
        self.task2 = Task.objects.create(
            title="test task 2",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-26",
            status="Completed",
        )
        self.task3 = Task.objects.create(
            title="test task 3",
            description="this is test task",
            assigned_to=self.user3,
            assigned_by=self.user2,
            due_date="2024-12-28",
            status="Completed",
        )
        self.url = reverse("search")

    def test_search_status(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url, {"keyword": "In progress"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test task")
        self.assertNotContains(response, "test task 2")

    def test_search_assigned_by(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url, {"keyword": "test user"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test task")
        self.assertNotContains(response, "test task 3")

    def test_search_due_date(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url, {"keyword": "2024-12-28"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test task 3")
        self.assertNotContains(response, "test task 1")
        self.assertNotContains(response, "test task 2")


class TestAllTaskView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="12345"
        )
        self.user2 = User.objects.create_user(
            email="testuser2@gmail.com", password="1234"
        )
        self.task = Task.objects.create(
            title="test task",
            description="this is test task",
            assigned_to=self.user2,
            assigned_by=self.user,
            due_date="2024-12-24",
        )
        self.url = reverse("all_task")

    def test_all_task_authenticated(self):
        self.client.login(email="testuser@gmail.com", password="12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test task")

    def test_all_task_unauthenticated(self):

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

from django import forms

from .models import Comment, Task, User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter Password"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password")

    # applying placeholder for all the fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs[
            "placeholder"
        ] = "Enter First Name"  # applying the text in the placeholder
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), empty_label="Select who to assign the task"
    )

    class Meta:
        model = Task
        fields = ("title", "description", "due_date", "assigned_to", "priority")


class MyTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("status",)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

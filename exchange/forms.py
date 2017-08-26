from django import forms
from models import Task


class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['type', 'post_link', 'price', 'max_count', 'description']
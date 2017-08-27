from django import forms
from models import Task


class AddTaskForm(forms.ModelForm):
    type
    class Meta:
        model = Task
        fields = ['type', 'post_link', 'price', 'max_count', 'description']
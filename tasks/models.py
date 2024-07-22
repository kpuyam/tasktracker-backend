from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in-progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
        ('not_started', 'Not Started'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.description

class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('task_creator', 'Task Creator'),
        ('read_only', 'Read Only'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    users = models.ManyToManyField(User, related_name='roles')
    # project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    
    # def __str__(self):
    #     users = ", ".join([user.username for user in self.users.all()])
    #     return f"{users} - {self.get_name_display()} in {self.project.name}"

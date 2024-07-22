from django.contrib.auth.models import User
from django.db import models

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
        ('accepted', 'Accepted'),
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

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='read_only')
    user = models.ForeignKey(User, related_name='role', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        # Remove any existing roles for this user
        Role.objects.filter(user=self.user).delete()
        super().save(*args, **kwargs)

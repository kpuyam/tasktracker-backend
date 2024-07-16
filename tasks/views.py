from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Task, Role
from .serializers import ProjectSerializer, TaskSerializer, RoleSerializer

# Create your views here.

@api_view(['POST'])
def find_projects(request):
    projects = Project.objects.filter(name = request.data['name'])
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['project__id']
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            return self.queryset.filter(project__id=project_id)
        return self.queryset

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

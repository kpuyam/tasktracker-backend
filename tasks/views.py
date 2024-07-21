from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, Role, Task
from .serializers import (
    ProjectSerializer,
    RoleSerializer,
    TaskSerializer,
    UserSerializer,
)

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

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
        status = self.request.query_params.get('status', None)
        print(status)
        if status is not None:
            if status == 'not_completed':
                return self.queryset.exclude(status='completed')
            else:
                return self.queryset.filter(status=status)
        print(self.queryset)
        return self.queryset

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        print("Hellloo sign up")
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password,first_name=first_name,last_name=last_name,email=email)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

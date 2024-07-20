from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Project, Task, Role
from .serializers import ProjectSerializer, TaskSerializer, RoleSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
# Create your views here.


@api_view(['GET'])
def get_users_by_project(request, project_id):
    try:
        # Get the project by ID
        project = Project.objects.get(pk=project_id)

        # Get the project owner
        project_owner = project.owner
        
        # Get all roles for the project
        roles = Role.objects.filter(project=project)

        # Get all users associated with these roles
        users = User.objects.filter(roles__in=roles).distinct()

        # Serialize the project owner and users
        project_owner_serializer = UserSerializer(project_owner)
        users_serializer = UserSerializer(users, many=True)
        
        print("Project Owner Data:", project_owner_serializer.data)
        print("Users Data:", users_serializer.data)

        # Prepare the response data
        response_data = {
            'project': ProjectSerializer(project).data,
            'project_owner': project_owner_serializer.data,
            'users': users_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
        
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle any unexpected errors
        print(f"Unexpected error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            return self.queryset.filter(project__id=project_id)
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

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password,first_name=first_name,last_name=last_name,email=email)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

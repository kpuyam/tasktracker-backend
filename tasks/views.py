from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
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
def get_users_by_project(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        project_owner=project.owner
        # Fetch all tasks related to the project
        tasks = Task.objects.filter(project=project)

        # Extract unique owners (User instances) from the tasks
        task_owners_ids = tasks.values_list('owner', flat=True).distinct()
        task_owners = User.objects.filter(pk__in=task_owners_ids)  # Fetch User instances

        # Serialize the user instances
        users_serializer = UserSerializer(instance=task_owners, many=True)
        project_owner_serializer = UserSerializer(project_owner)

        response_data = {
            'project': ProjectSerializer(project).data,
            'project_owner': project_owner_serializer.data,  # Assuming you want the username of the project owner
            'users': users_serializer.data  # Serialized data of users who are owners of tasks in this project
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_tasks_by_project(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)

        # Fetch all tasks related to the project
        tasks = Task.objects.filter(project=project)

        # Serialize each task instance individually
        serialized_tasks = TaskSerializer(tasks, many=True).data

        response_data = {
            'tasks': serialized_tasks,
        }
        # print(serialized_tasks)
        return Response(response_data, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
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
    filter_backends = [filters.OrderingFilter]  # Add any additional filters you need

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        user_roles = Role.objects.filter(user_id=user_id).values_list('role', flat=True)
        queryset = Project.objects.all()
        if 'admin' in user_roles:
            queryset = Project.objects.all()
        elif 'read_only' in user_roles:
            task_projects = Task.objects.filter(owner=user_id).values_list('project_id', flat=True)
            queryset = Project.objects.filter(id__in=task_projects)

        elif 'task_creator' in user_roles:
            queryset = Project.objects.filter(owner=user_id)
        elif user_id:
            return Project.objects.none()

        return queryset

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        user_roles = Role.objects.filter(user_id=user_id).values_list('role', flat=True)
        project_id = self.request.query_params.get('project')
        queryset = Task.objects.all()
        if 'admin' in user_roles:
            queryset = Task.objects.all()
        elif 'read_only' in user_roles:
            queryset = Task.objects.filter(owner=user_id)
        elif 'task_creator' in user_roles:
            project_ids = Project.objects.filter(owner=user_id).values_list('id', flat=True)
            queryset = Task.objects.filter(project_id__in=project_ids)
        elif user_id:
            return Task.objects.none()
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset

# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer

#     filter_backends = [filters.OrderingFilter]

#     def get_queryset(self):
#         user_id = self.request.query_params.get('user_id')
#         user_roles = Role.objects.filter(user_id=user_id).values_list('role', flat=True)

#         if 'admin' in user_roles:
#             queryset = Task.objects.all()
#         elif 'read_only' in user_roles:
#             task_projects = Task.objects.filter(owner=user_id).values_list('project_id', flat=True)
#             queryset = Project.objects.filter(id__in=task_projects)
#         else:
#             queryset = Project.objects.filter(owner=user_id)

#     def get_queryset(self):
#         queryset = Task.objects.all()
#         project_id = self.request.query_params.get('project')
#         if project_id:
#             queryset = queryset.filter(project_id=project_id)
#         return queryset


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    def get_queryset(self):
        queryset = Role.objects.all()
        user_id = self.request.query_params.get('userid', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

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

    def get_queryset(self):
        queryset = User.objects.all()

        # Filter users based on role if 'role' parameter is provided in query params
        role_param = self.request.query_params.get('role')
        if role_param == "no_role":
            # Fetch users who have no roles assigned
            queryset = queryset.filter(role__isnull=True)

        elif role_param:
            # Fetch users with the specified role
            queryset = queryset.filter(role__role=role_param)

        return queryset

@api_view(['POST'])
def update_user_role(request):
    data = request.data  # Use request.data for JSON data
    print(data)  # Check if data is received correctly

    selectedRoleId = data.get('selectedRoleId')
    selectedUserId = data.get('selectedUserId')
    roles= ['','admin','task_creator','read_only']
    print(selectedRoleId, " chenna ", selectedUserId)
    try:

        user = User.objects.get(id=selectedUserId)
        role = roles[selectedRoleId]
        # Remove any existing roles for this user
        Role.objects.filter(user=user).delete()

        # Create a new Role object for the user with the selected role
        new_role = Role(user=user, role=role)
        new_role.save()

        return JsonResponse({'success': 'User role updated successfully.'})

    except User.DoesNotExist:
        return JsonResponse({'error': 'User with the specified ID does not exist.'}, status=400)
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role with the specified ID does not exist.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Failed to update user role. Error: {str(e)}'}, status=500)

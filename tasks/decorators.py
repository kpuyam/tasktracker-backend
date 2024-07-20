from functools import wraps
from django.http import HttpResponseForbidden

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_roles = user_roles.objects.filter(user=request.user).values_list('role', flat=True)
            if any(role in allowed_roles for role in user_roles):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return _wrapped_view
    return decorator

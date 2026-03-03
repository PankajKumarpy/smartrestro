from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles: str):
    """
    Decorator for function-based views.
    Usage: @role_required("MANAGER", "CASHIER")
    """

    def decorator(view_func):
        @login_required
        def _wrapped(request, *args, **kwargs):
            user_role = getattr(request.user, "role", None)
            if request.user.is_superuser or (user_role in roles):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this page.")

        return _wrapped

    return decorator


class RoleRequiredMixin:
    """
    Mixin for class-based views.
    Set required_roles = ("MANAGER", ...) on the view.
    """

    required_roles: Iterable[str] = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, "role", None)
        if request.user.is_superuser or (user_role in set(self.required_roles)):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You do not have permission to access this page.")


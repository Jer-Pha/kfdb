from functools import wraps

from django.http import HttpResponseForbidden
from django.conf import settings


def require_allowed_origin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if (
            not settings.DEBUG
            and request.headers.get("Origin")
            not in settings.CORS_ALLOWED_ORIGINS
        ):
            return HttpResponseForbidden("Forbidden")
        return view_func(request, *args, **kwargs)

    return wrapper

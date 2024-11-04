from django.conf import settings
from django.dispatch import receiver
from corsheaders.signals import check_request_enabled


@receiver(check_request_enabled)
def cors_allow_all_origins(sender, request, **kwargs):
    """Restricts access to /api/news/ endpoints based on allowed origins."""
    if (
        request.path.startswith(f"/api/news/")
        and request.headers.get("Origin") not in settings.CORS_ALLOWED_ORIGINS
    ):
        return False

    return None  # Default CORS

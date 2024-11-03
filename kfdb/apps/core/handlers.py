from django.dispatch import receiver
from corsheaders.signals import check_request_enabled


@receiver(check_request_enabled)
def cors_allow_all_origins(sender, request, **kwargs):
    """Checks if the request URL matches the unrestricted endpoints
    and lets the default CORS middleware handle the request if not.
    """
    #
    if request.path.startswith("/api/") and not any(
        request.path.startswith(f"/api/{prefix}/")
        for prefix in ["docs", "schema", "news"]
    ):
        return True  # Allow all origins for unrestricted endpoints
    return None  # Default CORS

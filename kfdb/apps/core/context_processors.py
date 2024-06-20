from django.conf import settings


def global_context(request):
    # Set theme
    theme_cookie = request.get_signed_cookie(
        key="kfdb_theme",
        salt=settings.KFDB_COOKIE_SALT,
        max_age=31536000,
        default=None,
    )

    print(theme_cookie)

    if theme_cookie:
        theme = theme_cookie
    else:
        theme = "light"

    context = {
        "theme": theme,
    }

    return context

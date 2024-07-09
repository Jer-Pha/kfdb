"""URL configuration for KFDB channels."""

from django.urls import path
from django.views.generic import TemplateView

from .views import ChannelPageView

urlpatterns = [
    path(
        "channels/",
        TemplateView.as_view(template_name="channels/channels-home.html"),
        name="channels_home",
    ),
    path(
        "channels/<slug:channel>/",
        ChannelPageView.as_view(),
        name="channel_page",
    ),
]

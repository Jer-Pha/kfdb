from re import sub

from django.views.generic import TemplateView

from .models import ChannelEdit, HostEdit, ShowEdit, VideoEdit
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video


class BaseEditView(TemplateView):
    """Base view for edit submissions."""

    http_method_names = ["get", "post"]
    template_name = ""

    def get(self, request, *args, **kwargs):
        """Build response for GET requests."""
        context = self.get_context_data(**kwargs)
        self.template_name = (
            "edits/partials/edit-"
            + request.path.split("/")[-1]
            + "-modal.html"
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Build response for POST requests.

        ``post_object()`` is defined by child View.
        """
        self.template_name = "edits/partials/submit-edit.html"
        try:
            obj = self.post_object()
            obj.topic = request.POST.get("topic", None)
            obj.description = sub(
                " +", " ", request.POST.get("description", "").strip()
            )
            obj.username = sub(
                " +", " ", request.POST.get("username", "").strip()
            )
            obj.save()

            context = {"message": "Thank you for your suggestion!"}
            code = 201
        except:
            context = {
                "message": (
                    "Oops, something went wrong! Please try again in a"
                    " few minutes. If you continue to receive this message,"
                    " please reach out to our support team."
                )
            }
            code = 202
        response = self.render_to_response(context)
        response.status_code = code
        return response

    def get_context_data(self, **kwargs):
        """Build context for GET requests.

        ``get_object()`` is defined by child View.
        """
        context = super().get_context_data(**kwargs)
        context["obj"] = self.get_object()
        return context


class EditChannelView(BaseEditView):
    """View for Channel edit submissions."""

    def get_object(self):
        """Used by ``BaseEditView.get_context_data()``."""
        return Channel.objects.values_list("id", "name").get(
            id=self.request.GET.get("channel", "")
        )

    def post_object(self):
        """Used by ``BaseEditView.post()``."""
        return ChannelEdit(
            channel=Channel.objects.get(id=self.request.POST.get("id", None))
        )


class EditHostView(BaseEditView):
    """View for Host edit submissions."""

    def get_object(self):
        """Used by ``BaseEditView.get_context_data()``."""
        return Host.objects.values_list("id", "name").get(
            id=self.request.GET.get("host", "")
        )

    def post_object(self):
        """Used by ``BaseEditView.post()``."""
        return HostEdit(
            host=Host.objects.get(id=self.request.POST.get("id", None))
        )


class EditShowView(BaseEditView):
    """View for Show edit submissions."""

    def get_object(self):
        """Used by ``BaseEditView.get_context_data()``."""
        return Show.objects.values_list("id", "name").get(
            id=self.request.GET.get("show", "")
        )

    def post_object(self):
        """Used by ``BaseEditView.post()``."""
        return ShowEdit(
            show=Show.objects.get(id=self.request.POST.get("id", None))
        )


class EditVideoView(BaseEditView):
    """View for Video edit submissions."""

    def get_object(self):
        """Used by ``BaseEditView.get_context_data()``."""
        return Video.objects.values_list("id", "title").get(
            id=self.request.GET.get("video", "")
        )

    def post_object(self):
        """Used by ``BaseEditView.post()``."""
        return VideoEdit(
            video=Video.objects.get(id=self.request.POST.get("id", None))
        )

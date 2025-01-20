from django.contrib.auth.mixins import AccessMixin


class InternOnlyMixin(AccessMixin):
    """Verify that the current user is an intern"""

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_intern):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

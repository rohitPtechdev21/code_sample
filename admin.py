from functools import update_wrapper
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import path
from . import models


@admin.register(models.SubscriptionSelection)
class SubscriptionSelectionAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "subscription",
        "created_at",


    )
    readonly_fields = (
        "client",
        "status",
        "subscription",
        "text",
        "created_at",
    )
    
    ordering = ("-created_at",)

    actions = None
    
    inlines = [
        UserPlatform
    ]


    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    change_form_template = "admin/create_contract_changeform.html"

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        model_name = self.model._meta.model_name
        custom_urls = [
            path(
                r"create_contract/<uuid:user>",
                wrap(self.create_contract),
                name="subscription_selection_{}_create_contract".format(model_name),
            ),
            path(
                r"send_emails",
                wrap(self.send_emails),
                name="subscription_selection_{}_send_emails".format(model_name),
            ),
        ]

        return urls + custom_urls

    @method_decorator(staff_member_required)
    def send_emails(self, request):
        vetted_users = request.GET.getlist('vetted_users[]')
        platform_users = request.GET.getlist('platform_users[]')
        subject = "Ready to work on a package?"
        sp = SubscriptionSelection.objects.get(uuid=request.GET.get('uuid')).subscription
        sp_title = sp.title
        package_url = s.subscription_LINK.format(sp.uuid)
        for user in vetted_users:
            user = UserProfile.objects.get(uuid=user)
            user.send_email(template_name='User Matching Packages',
                vars={
                    'USER_FIRST_NAME': user.first_name,
                    'USER_PACKAGE_URL': user.package_url,
                }, 
                subject=subject
            )

        for user in platform_users:
            user = UserProfile.objects.get(uuid=user)
            user.send_email(template_name='User Matching Packages',
                vars={
                    'USER_FIRST_NAME': user.first_name,
                    'USER_PACKAGE_URL': package_url,
                },
                subject=subject
            )

        response = Response({}, status=status.HTTP_200_OK)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}

        return response

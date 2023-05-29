from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.conf import settings


class SubscriptionSavedListCreateView(generics.ListCreateAPIView):
    permission_classes = [UserPermission | IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return SubscriptionSaved.objects.none()

        user = user.fetch()
        return SubscriptionSaved.objects.filter(user=user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SubscriptionSavedDetailSerializer
        else:
            return SubscriptionSavedSerializer

    def perform_create(self, serializer):
        user = self.request.user.fetch()
        serializer.save(user=user)
    

subscription_saved_list_create_view = (
    SubscriptionSavedListCreateView().as_view()
)

class SavedPlan(generics.ListAPIView):
    permission_classes = [UserPermission | IsAuthenticated]
    serializer_class = SubscriptionSavedDetailSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return SubscriptionSaved.objects.none()

        user = user.fetch()
        return SubscriptionSaved.objects.filter(user=user)

subscription_saved_list_create_view = (
    SavedPlan().as_view()
)


class SubscriptionFeaturedListView(generics.ListAPIView):
    permission_classes = [UserPermission, IsAuthenticated]
    serializer_class = SubscriptionSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return Subscription.objects.none()

        user = self.request.user.fetch()

        return get_rows_common_skills(
            qs=Subscription.objects,
            user=user,
            offset=settings.PACKAGES_NUM_ROWS,
            qs_filter=dict(is_published=True),
        )


subscription_featured_view = SubscriptionFeaturedListView.as_view()


class SubscriptionSupplyCreateAPIView(generics.CreateAPIView):
    permission_classes = [BasicPermission, IsAuthenticated]
    serializer_class = SubscriptioSupplySerializer

    def perform_create(self, serializer):
        subscription = get_object_or_404(
            Subscription, pk=self.kwargs.get("pk"), is_teaser=False
        )

        user = self.request.user.fetch()
        user_free = user.get_user_profile()

        if FreeSubscription.objects.filter(
            subscription=subscription, user_free=user_free,
        ).exists():
            raise ConflictValidationError(
                "This Freelancer was already matched "
                "with this Standard Package"
            )

        instance = serializer.save(
            subscription=subscription, user_free=user_free,
        )
        MAIL_ADDRESS = settings.ADMIN_GENERAL_EMAIL
        if settings.APP_HOST.find('staging') != -1:
            MAIL_ADDRESS = settings.ADMIN_STAGING_EMAIL
        User.admin_user(email=MAIL_ADDRESS).send_email(
            template_name="User wants to supply a Subscription",
            vars={
                "NAME": user_free.firstname_lastname,
                "SUBSCRIPTION_NAME": subscription.title,
                "TEXT": instance.text,
                "PROFILE_LINK": settings.PROFILE_LINK.format(
                    str(user_free.uuid)
                ),
            },
            subject=None,
        )


subscription_supply_create_view = (
    SubscriptionSupplyCreateAPIView().as_view()
)

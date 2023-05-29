from django.urls import path
from .views import (
    subscription_featured_view,
    subscription_saved_list_create_view,
    subscription_supply_create_view,
    subscription_saved_list_create_view
)

app_name = "subscriptions"


urlpatterns = [
    path(
        "/saved",
        subscription_saved_list_create_view,
        name="saved_list_create_view",
    ),
    path(
        "/saved-planner",
        subscription_saved_list_create_view,
        name="plan_saved_list_create_view",
    ),
    path("/featured", subscription_featured_view, name="featured"),
    path(
        "/<uuid:pk>/supply",
        subscription_supply_create_view,
        name="supply_create_view",
    ),
]   
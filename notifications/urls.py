from django.urls import path, re_path

from .views import (
    CreateListNotificationTemplatesAPIView,
    CreateNotificationAPIView,
    CustomizeNotificationAPIView,
    RetrieveUpdateNotificationTemplatesAPIView,
    RetrieveUserNotificationsAPIView,
)

urlpatterns = [
    path(
        "notification-templates/",
        CreateListNotificationTemplatesAPIView.as_view(),
        name="create-list-ntemplate",
    ),
    re_path(
        r"^notification-templates/(?P<pk>[0-9a-f-]+)/$",
        RetrieveUpdateNotificationTemplatesAPIView.as_view(),
        name="retrieve-update-ntemplate",
    ),
    path(
        "notification/create/",
        CreateNotificationAPIView.as_view(),
        name="create-notification",
    ),
    re_path(
        r"^notification/(?P<pk>[0-9a-f-]+)/$",
        CustomizeNotificationAPIView.as_view(),
        name="customize-notification",
    ),
    path(
        "notification/",
        RetrieveUserNotificationsAPIView.as_view(),
        name="user-notifications",
    ),
]

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.response import Response

from .models import Notification, NotificationTemplates, User, UserNotification
from .permissions import IsAdmin
from .serializers import (
    NotificationRetrievalSerializer,
    NotificationSerializer,
    NotificationTemplatesSerializer,
    UserNotificationsSerializer,
)


class CreateListNotificationTemplatesAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = NotificationTemplatesSerializer
    queryset = NotificationTemplates.objects.exclude(is_deleted=False)


class RetrieveUpdateNotificationTemplatesAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = NotificationTemplatesSerializer
    queryset = NotificationTemplates.objects.exclude(is_deleted=False)


class CreateNotificationAPIView(generics.GenericAPIView):
    permission_classes = [IsAdmin]
    serializer_class = NotificationSerializer

    @extend_schema(
        summary="Create Notification and send/schedule it to users.",
        description="API View that lets admins create notification with the option of using \
                     notification templates, these notifications are then sent/scheduled to be sent \
                     to users specified in the call.",
        responses={
            201: inline_serializer(
                name="create-notification-response",
                fields={
                    "notification": NotificationSerializer(),
                    "non_existent_users": serializers.ListField(
                        child=serializers.UUIDField()
                    ),
                },
            ),
            404: OpenApiResponse(description="Notification template does not exist."),
            400: OpenApiResponse(description="Invalid input."),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_template_id = serializer.validated_data.pop(
            "notification_template", None
        )
        # Concerning passing some or all users that don't exist, usage will depend on the case
        # In case we want to send the notification to those who exist and ignore the others than this is the code for it
        # In case we want to cancel, than we would need this code to be put in a db (with transaction.atomic())
        users = serializer.validated_data.pop("users")
        notification_status = serializer.validated_data.pop("status", None)

        if notification_template_id:
            try:
                notification_template = NotificationTemplates.objects.get(
                    id=notification_template_id
                )
                # Use the notification template fields
                serializer.validated_data["subject"] = notification_template.subject
                serializer.validated_data["file"] = notification_template.file
                serializer.validated_data["content"] = notification_template.content
                serializer.validated_data["message_type"] = (
                    notification_template.message_type
                )
                notification = Notification.objects.create(**serializer.validated_data)
            except NotificationTemplates.DoesNotExist:
                return Response(
                    {"error": "Notification template does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            notification = Notification.objects.create(**serializer.validated_data)

        # List of users that don't exist
        non_existent_users = []

        # Send notification to users
        if notification_status:
            for user in users:
                # Check if the user exists
                if User.objects.filter(id=user).exists():
                    UserNotification.objects.create(
                        notification=notification,
                        user_id=user,
                        status=notification_status,
                    )
                else:
                    non_existent_users.append(user)
        else:
            for user in users:
                if User.objects.filter(id=user).exists():
                    UserNotification.objects.create(
                        notification=notification, user_id=user
                    )
                else:
                    non_existent_users.append(user)

        return Response(
            {
                "notification": NotificationSerializer(notification).data,
                "non_existent_users": non_existent_users,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomizeNotificationAPIView(generics.GenericAPIView):
    serializer_class = NotificationRetrievalSerializer
    permission_classes = [IsAdmin]
    queryset = Notification.objects.all()

    @extend_schema(
        summary="Customize Notification.",
        description="API View that lets admins customize notifications",
        responses={
            201: NotificationRetrievalSerializer,
            404: OpenApiResponse(description="Notification doesn't exist."),
            400: OpenApiResponse(description="Invalid input."),
        },
    )
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification doesn't exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveUserNotificationsAPIView(generics.ListAPIView):
    serializer_class = UserNotificationsSerializer
    permission_classes = [IsAdmin]
    queryset = UserNotification.objects.exclude(is_deleted=True)

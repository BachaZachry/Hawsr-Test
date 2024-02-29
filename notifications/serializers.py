from rest_framework import serializers

from .models import (
    NOTIFICATION_STATUS,
    NOTIFICATION_TYPE,
    Notification,
    NotificationTemplates,
    UserNotification,
)


class NotificationTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplates
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["message_type"] = dict(NOTIFICATION_TYPE.choices)[
            representation["message_type"]
        ]

        return representation


class NotificationSerializer(serializers.ModelSerializer):
    notification_template = serializers.UUIDField(
        allow_null=True,
        required=False,
        write_only=True,
    )
    users = serializers.ListField(
        child=serializers.UUIDField(), required=True, write_only=True
    )
    status = serializers.ChoiceField(
        choices=NOTIFICATION_STATUS.choices,
        required=False,
        write_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["created"]
        extra_kwargs = {
            "notification_template": {"write_only": True},
            "subject": {"required": False},
            "content": {"required": False},
            "file": {"required": False},
            "message_type": {"required": False},
        }

    def validate(self, data):
        data_keys = data.keys()
        notification_template = data.get("notification_template")

        # If no template is provided, the other fields will become required
        if not notification_template:
            if "subject" not in data_keys:
                raise serializers.ValidationError("Missing subject field.")
            if "content" not in data_keys:
                raise serializers.ValidationError("Missing content field.")
            if "message_type" not in data_keys:
                raise serializers.ValidationError("Missing message_type field.")
            if "file" not in data_keys:
                raise serializers.ValidationError("Missing file field.")

        # If the status is scheduled, send_date has to be present
        if "status" in data_keys:
            if data["status"] == 2 and "send_date" not in data_keys:
                raise serializers.ValidationError(
                    "send_date is required when scheduling a notification."
                )

        return data


class NotificationRetrievalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["message_type"] = dict(NOTIFICATION_TYPE.choices)[
            representation["message_type"]
        ]

        return representation


class UserNotificationsSerializer(serializers.ModelSerializer):
    notifications = NotificationSerializer(source="notification")

    class Meta:
        model = UserNotification
        exclude = ["notification"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = str(instance.user)

        return representation

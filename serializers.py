from django.conf import settings
from rest_framework import serializers
from .models import (
    Subscription,
    Common,
    Freesubscription,
)


class FreesubscriptionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Freesubscription
        fields = "__all__"

    def get_title(self, obj):
        if obj.created_from_sp:
            return obj.created_from_sp.title
        elif obj.title:
            return obj.title
        else:
            return ""

    def get_url(self, obj):
        if 'is_logged_in' in self.context and self.context['is_logged_in']:
            if obj.created_from_sp:
                return f'https://{settings.APP_HOST}/packages/standard/{obj.created_for.uuid}'
            elif obj.url:
                return obj.url
            else:
                return ""
        else:
            if obj.created_from_sp:
                return f'https://{settings.APP_HOST}/public/standard-package/{obj.created_for.title.replace(" ", "-")}'
            elif obj.url:
                return obj.url
            else:
                return ""
            

class CustomField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Freesubscription):
            return FreesubscriptionSerializer(value).data
        if isinstance(value, SubscriptionUser):
            return SubscriptionUserSerializer(value).data
        if isinstance(value, Timeline):
            return TimelineSerializer(value).data
        if isinstance(value, Freesubscription):
            return RelatedPackageSerializer(value).data
        if isinstance(value, SubscriptionCategory):
            return SubscriptionCategorySerializer(value).data

        raise ValueError("Unexpected type of object {}".format(value))


class FreesubscriptionSerializer(serializers.ModelSerializer):
    timelines = CustomField(many=True, read_only=True)

    class Meta:
        model = Freesubscription
        fields = "__all__"


class FreesubscriptionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freesubscription
        fields = (
            "uuid",
            "title",
            "content",
            "lower_amount",
            "icon",
        )

class FreesubscriptionSavedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freesubscription
        fields = (
            "uuid",
            "lower_amount",
            "upper_amount",
        )

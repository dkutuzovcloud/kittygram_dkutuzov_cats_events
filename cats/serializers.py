from rest_framework import serializers
from django.utils import timezone

from .models import Cat, Event, EventRegistration


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    cat = CatSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'user', 'cat', 'status', 'registered_at']


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    registrations_count = serializers.SerializerMethodField()
    remaining_slots = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date_time', 'location',
            'max_participants', 'owner', 'created_at',
            'registrations_count', 'remaining_slots',
        ]
        read_only_fields = ['owner', 'created_at']

    def get_registrations_count(self, obj):
        return obj.registrations.count()

    def get_remaining_slots(self, obj):
        return max(0, obj.max_participants - obj.registrations.count())


class EventCreateSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        fields = [
            'title', 'description', 'date_time', 'location', 'max_participants',
        ]

    def validate_date_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Дата должна быть в будущем')
        return value


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['cat']

    def validate(self, data):
        event = self.context['event']
        user = self.context['request'].user

        # нельзя дважды записаться
        if event.registrations.filter(user=user).exists():
            raise serializers.ValidationError(
                {'non_field_errors': ['Вы уже зарегистрированы на это событие.']}
            )

        # нельзя переполнить лимит
        if event.registrations.count() >= event.max_participants:
            raise serializers.ValidationError(
                {'non_field_errors': ['Места закончились.']}
            )

        return data

    def create(self, validated_data):
        return EventRegistration.objects.create(
            event=self.context['event'],
            user=self.context['request'].user,
            **validated_data
        )
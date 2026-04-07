from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from .models import Cat, Event, EventRegistration
from .serializers import (
    CatSerializer,
    EventSerializer,
    EventCreateSerializer,
    EventRegistrationSerializer,
    EventRegistrationCreateSerializer,
)


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('owner').prefetch_related('registrations')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        event = self.get_object()
        registrations = event.registrations.select_related('user', 'cat').all()
        page = self.paginate_queryset(registrations)
        if page is not None:
            serializer = EventRegistrationSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        event = self.get_object()
        serializer = EventRegistrationCreateSerializer(
            data=request.data,
            context={'request': request, 'event': event},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Регистрация успешно оформлена.'},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        event = self.get_object()
        registration = event.registrations.filter(user=request.user).first()
        if not registration:
            return Response(
                {'detail': 'Вы не зарегистрированы на это событие.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        registration.delete()
        return Response({'message': 'Вы отменили участие в событии.'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        events = self.filter_queryset(self.get_queryset()).filter(owner=request.user)
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk')
        if event_id:
            return EventRegistration.objects.filter(event__id=event_id).select_related('user', 'cat')
        return EventRegistration.objects.none()
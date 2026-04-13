from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Cat, Event, EventRegistration
from .serializers import (
    CatSerializer,
    EventSerializer,
    EventCreateSerializer,
    EventRegistrationSerializer,
    EventRegistrationCreateSerializer,
)
from .permissions import IsOwnerOrReadOnly


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
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        event = self.get_object()

        # Только владелец может смотреть участников
        if event.owner != request.user:
            return Response(
                {'detail': 'Только владелец может смотреть участников.'},
                status=status.HTTP_403_FORBIDDEN
            )

        registrations = event.registrations.select_related('user', 'cat').all()
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
        return Response({'message': 'Вы отменили участие.'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        events = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
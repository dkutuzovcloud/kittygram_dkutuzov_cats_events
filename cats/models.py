from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    birth_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.PositiveIntegerField(default=20)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.date_time <= timezone.now():
            raise ValidationError('Дата события должна быть в будущем')
        if self.max_participants < 1:
            raise ValidationError('Минимум 1 место')
        super().clean()


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждено'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    cat = models.ForeignKey(
        Cat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f'{self.user.username} — {self.event.title}'
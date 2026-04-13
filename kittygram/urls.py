from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cats import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'cats', views.CatViewSet)
router.register(r'events', views.EventViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Kittygram API",
        default_version='v1',
        description="Документация API кото-ивентов",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # JWT
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    # 📄 ДОКУМЕНТАЦИЯ
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
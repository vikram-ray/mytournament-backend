from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/tournaments/', include('apps.tournaments.urls')),
    path('api/game/', include('apps.game.urls')),
    path('api/gamemode/', include('apps.gamemode.urls')),
    path('api/participant/', include('apps.participant.urls')),
    path('api/platform/', include('apps.platform.urls')),
    path('api/utils/', include('apps.utils.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
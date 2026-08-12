from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from users.views import register, user_login, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # All API endpoints live under /api/

    # Core pages (served via Django templates)
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('challenges/', TemplateView.as_view(template_name='challenges.html'), name='challenges'),
    path('rewards/', TemplateView.as_view(template_name='rewards.html'), name='rewards'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),

    # Authentication
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('admin-panel/', include('admin_panel.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

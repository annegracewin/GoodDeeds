from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # ← Changed from 'api.urls' to 'core.urls'
    path('', TemplateView.as_view(template_name='dashboard.html'), name='home'),
]
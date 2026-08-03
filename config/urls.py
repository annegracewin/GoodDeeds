from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

# Import your custom auth views (if you made them)
# If not, you can use the default LoginView/LogoutView
from users.views import register, user_login, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),          # includes all API endpoints
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('login/', user_login, name='login'),   # or use LoginView.as_view()
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
]
from baton.autodiscover import admin
from django.urls import path, include
from core import views as core_views
#from .router import router

urlpatterns = [
    # path('rest-auth/login/', core_views.CustomLoginView.as_view(),name = 'custom-login'),
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),

    # Apps
    path('core/', include('core.urls')),

    # Authentication
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('', include('django.contrib.auth.urls')),
]

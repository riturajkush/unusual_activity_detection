from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name='home'
urlpatterns = [
    path('test2/', views.index,name='index'),
    path('test2/login',views.logins,name='login'),
    path('test2/logout',views.logouts,name='logout'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)

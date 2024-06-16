from django.contrib import admin
from django.urls import path, include
from setup.tasks import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.inscricao.urls')),
]

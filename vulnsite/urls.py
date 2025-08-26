"""
URL configuration for vulnsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from main import views
from django.views.static import serve
from django.conf import settings
import os


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/profile', views.profile_api, name='profile_api'),
    path('blog/', views.blog, name='blog'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('upload/', views.upload, name='upload'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('files/', views.files_index, name='files_index'),
    # 👇 وصول مباشر لأي ملف داخل uploads/ (تعريض عام مقصود)
    re_path(r'^files/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'uploads')}),

]

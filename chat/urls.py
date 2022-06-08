# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
    path('create_post/qalesan/', views.create_post, name='create_post'),
    path('post_list/views/', views.post_list, name='post_list'),
]
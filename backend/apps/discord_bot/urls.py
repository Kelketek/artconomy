from django.urls import path

from apps.discord_bot import views

app_name = 'lib'

urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('config/', views.config, name='config')
]

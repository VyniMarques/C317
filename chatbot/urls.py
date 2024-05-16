from django.urls import path
from . import views

urlpatterns = [
    path('conversar/', views.conversar),
    path('process-message/', views.process_message),
    path('login/', views.login)
]



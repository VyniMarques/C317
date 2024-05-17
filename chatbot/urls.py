from django.urls import path
from . import views

urlpatterns = [
    path('conversar/', views.conversar, name='conversar'),
    path('process-message/', views.process_message),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro')
]



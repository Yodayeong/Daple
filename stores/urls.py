from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('create', views.create, name='create'),
]

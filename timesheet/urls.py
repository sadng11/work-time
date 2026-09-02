from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report, name='report'),
    path('factor/<str:start>/<str:end>/<str:project>', views.factor, name='factor'),
]
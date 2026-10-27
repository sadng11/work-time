from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report, name='report'),
    path('factor/<str:start>/<str:end>/<str:project>', views.factor, name='factor'),
    path('entry/<int:entry_id>/edit/', views.edit_time_entry, name='edit_time_entry'),
    path('entry/<int:entry_id>/delete/', views.delete_time_entry, name='delete_time_entry'),
]
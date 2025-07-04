from . import views
from django.urls import path

urlpatterns = [
    path('', views.upload_and_sign, name='upload_and_sign'),
]
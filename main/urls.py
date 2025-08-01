# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # This will be the root URL of your site
    path('', views.portfolio_view, name='portfolio'),
]
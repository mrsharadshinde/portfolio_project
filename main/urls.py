# main/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # This will be the root URL of your site
    path('', views.portfolio_view, name='portfolio'),
    path('chatbot-response/', views.ai_chatBot, name='chatbot_response'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
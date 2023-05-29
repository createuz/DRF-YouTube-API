from django.urls import path
from . import views

urlpatterns = [
    path('video/<str:video_id>', views.get_video),
    path('channel/<str:channel_id>', views.get_channel),
]

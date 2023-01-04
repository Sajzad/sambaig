from django.urls import path, include
from . import views


app_name = "twilio_sms"

urlpatterns = [
    
    path('incoming', views.twilio_incoming_view, name='twilio_reply'),
    path('dlr', views.twilio_status_view, name='twilio_status'),

]
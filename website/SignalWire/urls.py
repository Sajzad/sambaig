from django.urls import path, include
from . import views


app_name = "signalwire"

urlpatterns = [
    
    path('fax/incoming', views.signalwire_fax_incoming_view, name='signal_fax_incoming'),
    path('sms/incoming', views.signalwire_sms_incoming_view, name='signal_sms_incoming'),
]
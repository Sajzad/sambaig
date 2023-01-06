from django.urls import path, include
from . import views


app_name = "telnyx_sms"

urlpatterns = [
    path('incoming', views.telnyx_incoming_view, name='telnyx_incoming'),
    path('fax/incoming', views.telnyx_fax_incoming_view, name='telnyx_fax_incoming'),
    path('dlr', views.telnyx_dlr_view, name='telnyx_dlr'),
    path('cronjob', views.telnyx_cronjob_view, name='telnyx_cronjob'),

]
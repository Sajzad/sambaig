from django.urls import path, include
from . import views


app_name = "facebook"

urlpatterns = [
    
    path('leads', views.facebook_ads_view, name='fb_ads'),
    path('leads/<form_id>/', views.form_details_view, name='leads'),
    path('leads/<form_id>/<lead_id>/', views.lead_edit_view),
    path('incoming', views.facebook_ads_incoming_view, name='fb_ads_incoming'),
]
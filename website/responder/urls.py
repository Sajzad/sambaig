from django.urls import path
from . import views


app_name = "responder"

urlpatterns = [
    
    path('undelivered', views.undel_messages_view, name='undelivered-messages'),
    path('gallery/<int:cam_id>/', views.gallery_view, name='gallery'),
    path('cronjob/', views.cronjob_view, name='cronjob'),
    path('cron/bulk', views.cronjob_bulk_view, name='cronjob_bulk'),
    path('response/edit/<int:cam_id>/<int:resp_id>/', views.response_edit_view, name='response-edit'),
    path('leads/<int:id>', views.lead_view, name='leads'),
    path('leads/conversations/<str:dnis>', views.chat_details, name='conversations'),
    path('conversations/', views.side_conversations_view, name='side-conversations'),
    path('pineapple/incoming', views.pineapple_response, name='pineapple-response'),
    path('pineapple/dlr', views.pineapple_dlr, name='pineapple-dlr'),
    path('undelivered/<int:cam_id>/', views.undelivered_view, name='undelivered'),
    path('delivered/<int:cam_id>/', views.delivered_view, name='delivered'),
    path('registration/', views.registration_view, name='registration'),
    path('test/<slug:slug>', views.test_view, name='test'),
    path('autoresponders/', views.auto_responders_view, name='auto-responders'),
    path('autoresponders/<int:resp_id>/', views.auto_responders_edit_view, name='auto-responders'),
    path('keywords/', views.keywords_view, name='keywords'),
    path('keywords/<int:keyword_id>/', views.edit_keyword_view, name='edit_keyword'),
    path('bulk-sms/', views.import_view, name='bulk-sms'),
    path('primary-number/', views.pn_view, name='primary_number'),

]

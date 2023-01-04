from django.urls import path, include
from . import views


app_name = "base"

urlpatterns = [
    
    path('', views.home_view, name='home'),
    path('staff', views.staff_view, name='staff'),
    path('gateways/', views.gateway_view, name='gateways'),
    path('gateway/<gateway_id>/', views.edit_gateway_view, name='edit_gateway'),
    path('settings/', views.settings_view, name='settings'),
    path('accounts/signin/', views.ClientSigninView.as_view(), name='signin'),
    path('accounts/signup/', views.ClientSignupView.as_view(), name='signup'),
    path('home/admin/', views.admin_view, name='super_admin'),
    path('home/admin/edit/<admin_id>/', views.edit_admin_view, name='edit-user'),
    path('home/access/', views.access_view, name='access'),
    path('home/admin/create-role/', views.create_role_view, name='create-role'),
    path('home/admin/create-role-subadmin/', views.create_role_subadmin, name='create-role-subadmin'),
    path('home/admin/create-user/', views.create_user_view, name='create-user'),
    path('home/admin/member/', views.add_member_view, name='member'),
    path('support/', views.support_view, name='support'),
    path('home/support/<int:id>/', views.support_detail_view, name='support'),
    path('home/support/', views.admin_support_view, name='admin_support'),
    path('home/support/chat/<str:args>', views.support_chat, name='support_ticket'),
    path('home/report/', views.admin_report_view, name='report'),
    path('home/number/', views.ani_view, name='ani'),
    path('home/number/<ani_id>/<admin_id>/', views.edit_ani_view, name='edit_ani'),

    # shortened Url
    path('<str:short_url>', views.visit_real_url, name='visit_real_url'),
    path('shortened-url/', views.shortened_url, name='shortened_url')

]
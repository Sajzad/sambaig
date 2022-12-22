from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('way_to_superadmin/', admin.site.urls),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('', include('base.urls')),
    path('campaigns/', include('responder.urls')),
    path('telnyx/', include('telnyx_sms.urls')),
    path('signalwire/', include('SignalWire.urls')),
    path('facebook/', include('facebook.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns


admin.site.site_header = "SMS Responder"
admin.site.site_title = "Square Reach"
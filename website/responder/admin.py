from django.contrib import admin
from .models import *

# Register your models here.

class InOutSmsAdmin(admin.ModelAdmin):
    list_display = ['ani', 'name', 'type', 'gateway', 'error', 'message_id', 'reply', 'sent', 'dnis','del_status',\
    'is_lead', 'check_keyword', 'to_reply','is_wait','is_bulk']
    search_fields = ['dnis', 'sent', 'reply', 'ani__ani']

class NumberUploadAdmin(admin.ModelAdmin):
    list_display = ['form', 'admin']
    search_fields = ['form', 'admin']

class GatewayAdmin(admin.ModelAdmin):
    list_display = ['gateway','price', 'mms_price']

class AdminAdmin(admin.ModelAdmin):
    list_display = ['admin','balance']

class ErrorAdmin(admin.ModelAdmin):
    list_display = ['view','error', 'reason', 'timestamp']

class AniAmin(admin.ModelAdmin):
	list_display = ['ani','gateway', 'admin',]

class AutoresponseAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin', 'contact', 'contact_id', 'response', 'is_active']

admin.site.register(Admin, AdminAdmin)
admin.site.register(NumberUpload, NumberUploadAdmin)
admin.site.register(InOutSms, InOutSmsAdmin)
admin.site.register(Ani, AniAmin)
admin.site.register(Spam)
admin.site.register(Gateway, GatewayAdmin)
admin.site.register(AddGateway)
admin.site.register(DefaultMessage)
admin.site.register(Error, ErrorAdmin)
admin.site.register(AssignContact)
admin.site.register(PrimaryNumber)
admin.site.register(AssignedAni)
admin.site.register(Image)
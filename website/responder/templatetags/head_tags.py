from django import template
from django.db.models import Q
from .. models import InOutSms
from base.models import Support, Notification, DefaultNotification
from django.contrib.sites.models import Site



register = template.Library()


@register.simple_tag
def undelivered_messages(**kwargs):
    user = kwargs['user']
    return InOutSms.objects.filter(admin__admin=user, sent__isnull=False).exclude(del_status='delivered').count()

@register.simple_tag
def unseen_msgs(**kwargs):
    user = kwargs['user']
    return InOutSms.objects.filter(is_seen=False, sent__isnull=False, admin__admin=user).exclude(del_status='delivered').count()

@register.simple_tag
def support_count():
    return Support.objects.count()

@register.simple_tag
def site_name():
    return Site.objects.all()[0].name

@register.filter()
def phone_number(number):
    if number:
        lenght = len(number)
        if "+1" in number:    
            first = number[2:5]
            second = number[5:8]
            third = number[8:lenght+1]
            return '+1 ' + '(' + first + ')' + ' ' + second + '-' + third
        elif number[0] == "1":
            first = number[1:4]
            second = number[4:7]
            third = number[7:lenght+1]
            return '1 ' + '(' + first + ')' + ' ' + second + '-' + third
        else:
            first = number[0:3]
            second = number[3:6]
            third = number[6:lenght+1]
            return '(' + first + ')' + ' ' + second + '-' + third
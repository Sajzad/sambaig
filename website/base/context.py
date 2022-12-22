from responder.models import (
    Ani,
    PrimaryNumber,
    AssignedAni, 
    InOutSms)

from facebook.models import AdForm


def notifications(request):
    default_message = ""
    notifications = ""
    nots_count = 1
    balance = 0.0
    anis = ""
    user_anis = ''
    lead_list = ''
    pn = ''
    

    try:
        if request.user.is_superuser:
            anis = Ani.objects.all()
            pn = PrimaryNumber.objects.all()[0]
        else:
            user_anis = AssignedAni.objects.filter(admin__admin=request.user)

    except:
        pass
    try:
        lead_list = AdForm.objects.all()
    except:
        pass

    context = {
        "pn": pn,
        "lead_list":lead_list,
        "anis":anis,
        "user_anis":user_anis,
        "default":default_message,
        "nots_count":nots_count,
        "messages":notifications
    }
    return context

def unread_count(request):
    unread_count = 0
    if request.user.is_superuser:
        try:
            ani_id = PrimaryNumber.objects.all()[0].ani_id
            unread_count = InOutSms.objects.filter(ani_id=ani_id, to_reply=True).count()
        except:
            pass
    else:
        try:
            ani_objs = AssignedAni.objects.filter(admin__admin=request.user)
            if ani_objs:
                ani_id = ani_objs[0].ani_id
                unread_count = InOutSms.objects.filter(ani_id=ani_id, to_reply=True).count()
        except:
            pass
    
    context = {
        'unread_count':unread_count
    }
    return context
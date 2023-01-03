import json
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


from responder.models import(
    Admin,
    Spam,
    InOutSms,
    Ani,
    Gateway,
)


@csrf_exempt
def signalwire_sms_incoming_view(request):
    print("incoming")
    cam_obj = None
    is_spam = False
    sms_obj = ""

    try:
        print("post",request.POST)
    except:
        pass
    # try:
    #     print("json",json.loads(request.loads))
    # except:
    #     pass
    if request.method == "POST":
        ani = request.POST["To"]
        msg_id = request.POST["SmsSid"]
        dnis = request.POST["From"]
        message = request.POST["Body"]
        try:
            ani_objs = Ani.objects.filter(ani__contains=ani)
            ani_id = ani_objs[0].id
            admin = ani_objs[0].admin.admin
            cam_id = ani_objs[0].campaign_id
        except Exception as e:
            print(e)
            
        if Campaign.objects.filter(id=cam_id, is_active=True).exists():
            admin_obj = get_object_or_404(Admin, admin__username=admin)
            sms_obj = InOutSms.objects.filter(dnis=dnis)
            cam_obj = get_object_or_404(Campaign, id=cam_id)    
            try:
                spams = []
                spam_objs = Spam.objects.values('spam')
                for item in spam_objs:
                    spams.append(item['spam'])
            except Exception as e:
                print(e)
                pass
            for item in spams:
                if item in message:
                    is_spam = True
            if not is_spam:
                try:
                    # to check new lead
                    check_duplicate = False
                    check_duplicate = sms_obj.filter(dnis=dnis, is_lead=True).exists()
                except Exception as e:
                    print(e)
                if sms_obj.filter(to_reply=True).exists():
                    to_reply = False
                else:
                    to_reply = True
                gate_obj = get_object_or_404(Gateway, gateway__contains="Signalwire")

                if check_duplicate:
                    InOutSms.objects.create(gateway=gate_obj, admin = admin_obj, campaign=cam_obj, \
                    order=0, to_reply=to_reply, dnis=dnis, reply= message, message_id=msg_id, ani_id=ani_id)
                else:
                    InOutSms.objects.create(gateway=gate_obj,admin = admin_obj,campaign=cam_obj, to_reply=\
                    to_reply, dnis=dnis, reply= message, message_id=msg_id, ani_id=ani_id, is_lead=True, order=0)
            else:
                pass
                
    return HttpResponse(status=200)


@csrf_exempt
def signalwire_fax_incoming_view(request):
    print("fax incoming")
    cam_obj = None
    is_spam = False
    sms_obj = ""

    try:
        print("post",request.POST)
    except:
        pass

    if request.method == "POST":
        ani = request.POST["To"]
        msg_id = request.POST["FaxSid"]
        dnis = request.POST["From"]
        fax = request.POST["MediaUrl"]
        print('faxes', fax)

        ani_objs = Ani.objects.filter(ani__contains=ani.strip())
        if ani_objs:
            ani_obj = ani_objs.first()
            ani_id = ani_obj.id
            admin_id = ani_obj.admin_id
        else:
            return HttpResponse(status=404)

        # check whether new lead
        new_dnis = dnis.strip().replace('+', '')
        sms_objs = InOutSms.objects.filter(ani_id=ani_id, dnis__contains=new_dnis)

        if sms_objs.exists():
            check_duplicate = True
        else:
            if new_dnis[0] == "1":
                sms_objs = InOutSms.objects.filter(ani_id=ani_id,dnis__contains=new_dnis[1:])
                if sms_objs.exists():
                    check_duplicate = True
                else:
                    check_duplicate = False
            else:
                check_duplicate = False

        signalwire_obj = get_object_or_404(Gateway, gateway__contains="Signalwire")

        # Updating to_reply to catch unanswered contact
        if InOutSms.objects.filter(ani_id=ani_id,dnis__contains = new_dnis, to_reply=True).exists():
            to_reply = False
        else:
            to_reply = True

        print("final") 
        sms_obj = InOutSms.objects.create(
            gateway = signalwire_obj,
            type='fax',
            admin_id = admin_id, 
            dnis = dnis, 
            gif_url = fax,
            message_id = msg_id, 
            ani_id = ani_id,
            check_keyword = False,
            to_reply = to_reply,
            is_incoming = True)

        if not check_duplicate:
            sms_obj.is_lead = True
            sms_obj.save()

        InOutSms.objects.filter(
            ani_id = ani_id,
            dnis__contains = dnis.replace("+", ""), 
            is_lead=True).update(
                is_seen = False,
                is_wait = True,
                has_incoming = True
            )
                    
    return HttpResponse(status=200)


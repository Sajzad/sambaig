import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from responder.models import(
	Campaign,
	Admin,
	Spam,
	InOutSms,
	Ani,
)


@csrf_exempt
def twilio_incoming_view(request):

	cam_obj = None
	is_spam = False
	sms_obj = ""
	print('twilio', request.POST)
	if request.method == "POST":	

		message= request.POST['Body']
		msg_id = request.POST['SmsMessageSid']
		ani = request.POST['To'].replace("+", '')
		dnis = request.POST['From']
		print(message, ani, dnis)
		try:
			ani_objs = Ani.objects.filter(ani__contains=ani.strip())
			admin = ani_objs[0].admin.admin
			cam_id = ani_objs[0].campaign_id
		except Exception as e:
			print(e)

		if Campaign.objects.filter(id=cam_id, is_active=True).exists():
			admin_obj = get_object_or_404(Admin, admin__username=admin)
			sms_obj = InOutSms.objects.filter(campaign_id=cam_id)
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
					check_duplicate = sms_obj.filter(dnis__contains=dnis, is_lead=True).exists()
				except Exception as e:
					print(e)
				if sms_obj.filter(to_reply=True).exists():
					to_reply = False
				else:
					to_reply = True
				pineapple_obj = get_object_or_404(Gateway, gateway__contains="Twilio")
				if check_duplicate:
					# for the first sms order will be 0 instead 1
					InOutSms.objects.create(gateway=pineapple_obj, admin = admin_obj, campaign=cam_obj, to_reply=\
					to_reply, dnis=dnis, reply= message, message_id=msg_id, ani=ani, order=0)
				else:
					InOutSms.objects.create(gateway=pineapple_obj,admin = admin_obj,campaign=cam_obj, to_reply=to_reply, \
					dnis=dnis, reply= message, message_id=msg_id, ani=ani, is_lead=True, order=0)

	
	return HttpResponse(status=200)

@csrf_exempt
def twilio_status_view(request):
	try:
		print("post: ",request.POST)
	except Exception as e:
		print(e)	
	try:
		print("json: ",json.loads(request.body))
	except Exception as e:
		print(e)
	
	return JsonResponse(status=200)

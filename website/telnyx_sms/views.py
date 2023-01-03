import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from responder.tasker import error_handler


from facebook.models import (
	FacebookLead)

from responder.models import(
	InOutSms,
	Ani,
	Gateway)


@csrf_exempt
def telnyx_fax_incoming_view(request):
	print(f"telnyx incoming")
	status = ""	
	body = json.loads(request.body)
	print(body)

	if body['data']['payload']['direction'] == "outbound":
		error = ""
		msg_id = body['data']['payload']['fax_id']
		status = body['data']['payload']['status']
		# cost = body['data']['payload']['cost']['amount']
		dnis = body['data']['payload']['to']
		ani = body["data"]["payload"]["from"]

		ani_objs = Ani.objects.filter(ani__contains=ani.strip())
		ani_id = ani_objs.first().id
		
		if status == "failed":
			try:
				if body['data']['payload']['failure_reason']:
					error = ""
					code = ""
					try:
						error = body['data']['payload']['failure_reason']
					except:
						pass

					InOutSms.objects.filter(message_id__contains = msg_id).update(
						error = error, del_status = "undelivered")
			except Exception as e:
				print(e)
			return HttpResponse(status=200)

		elif status == "delivered":
			try:
				InOutSms.objects.filter(message_id__contains = msg_id).update(
					del_status = 'delivered', dlr = body, code = None)
			except Exception as e:
				print(e)
				error_handler(
					error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
					view = "telnyx_incoming_view", 
					reason = 'anything'
				)
			return HttpResponse(status=200)
			
	if body['data']['payload']['direction'] == "inbound":
		
		msg_id = body["data"]["payload"]["fax_id"]
		ani = body["data"]["payload"]["to"]
		print("incoming ani", ani)
		dnis = body["data"]["payload"]["from"]

		# to deactivate drip response
		new_dnis = dnis.replace("+","")

		try:
			gif_url = body["data"]["payload"]["media_url"]
		except Exception as e:
			print(e)
			gif_url = None

		ani_objs = Ani.objects.filter(ani__contains=ani.strip())

		if ani_objs.exists():
			ani_id = ani_objs.first().id
			admin_id = ani_objs.first().admin_id
		else:
			return HttpResponse(status=404)
		
		# if the fax is already received
		received_fax = InOutSms.objects.filter(message_id=msg_id, ani_id=ani_id)
		if received_fax.exists():
			fax = received_fax.first()
			fax.gif_url = gif_url
			fax.save()

			return HttpResponse(status=200)

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

		telnyx_obj = get_object_or_404(Gateway, gateway__contains="Telnyx")

		# Updating to_reply to catch unanswered contact
		if InOutSms.objects.filter(ani_id=ani_id,dnis__contains = new_dnis, to_reply=True).exists():
			to_reply = False
		else:
			to_reply = True
		
		sms_obj = InOutSms.objects.create(
			gateway = telnyx_obj,
			type='fax',
			admin_id = admin_id, 
			dnis = dnis, 
			gif_url = gif_url, 
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
		print(("done"))
					
	return HttpResponse(status=200)


@csrf_exempt
def telnyx_incoming_view(request):

	status = ""	

	body = json.loads(request.body)
	# print(body)

	if body['data']['payload']['direction'] == "outbound":
		error = ""
		msg_id = body['data']['payload']['id']
		status = body['data']['payload']['to'][0]['status']
		cost = body['data']['payload']['cost']['amount']
		dnis = body['data']['payload']['to'][0]['phone_number']
		ani = body["data"]["payload"]["from"]["phone_number"]

		ani_objs = Ani.objects.filter(ani__contains=ani.strip())
		ani_id = ani_objs[0].id
		
		if not status == "delivered":
			if body['data']['payload']['errors']:
				error = ""
				code = ""
				try:
					error = body['data']['payload']['errors'][0]['title']
					code = body['data']['payload']['errors'][0]['code']
				except:
					pass

				InOutSms.objects.filter(message_id__contains = msg_id).update(

						error = error,
						code = code,
						del_status = status
					)

		elif status == "delivered":
			try:
				InOutSms.objects.filter(message_id__contains = msg_id).update(
						del_status = 'delivered',
						dlr = body
					)
			except Exception as e:
				print(e)
				error_handler(
					error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
					view = "telnyx_incoming_view", 
					reason = 'anything'
				)
			
	if body['data']['payload']['direction'] == "inbound":
		
		message= body["data"]["payload"]["text"]
		msg_id = body["data"]["id"]
		ani = body["data"]["payload"]["to"][0]["phone_number"][1:]
		dnis = body["data"]["payload"]["from"]["phone_number"]

		# to deactivate drip response
		new_dnis = dnis.replace("+","")
		fb_objs = FacebookLead.objects.filter(phone__contains=new_dnis)
		if fb_objs:
			fb_objs.update(to_reply=False)
		else:
			if new_dnis[0] == "1":
				fb_objs = FacebookLead.objects.filter(phone__contains=new_dnis[1:])
				if fb_objs:
					fb_objs.update(to_reply=False)

		try:
			gif_url = body["data"]["payload"]["media"][0]["url"]
		except:
			gif_url = ''

		if 'stop' in message.lower():
			FacebookLead.objects.filter(phone__contains=dnis).delete()

		ani_objs = Ani.objects.filter(ani__contains=ani.strip())
		ani_id = ani_objs[0].id
		admin_id = ani_objs[0].admin_id

		# check whether new lead
		new_dnis = dnis.strip().replace('+', '')
		sms_objs = InOutSms.objects.filter(ani_id=ani_id,dnis__contains=new_dnis)
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

		telnyx_obj = get_object_or_404(Gateway, gateway__contains="Telnyx")

		# Updating to_reply to catch unanswered contact
		if InOutSms.objects.filter(ani_id=ani_id,dnis__contains = new_dnis, to_reply=True).exists():
			to_reply = False
		else:
			to_reply = True
			
		sms_obj = InOutSms.objects.create(
			gateway = telnyx_obj, 
			admin_id = admin_id, 
			dnis = dnis, 
			reply = message, 
			gif_url = gif_url, 
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


@csrf_exempt
def telnyx_dlr_view(request):
	
	return HttpResponse("telnyx dlr")

def telnyx_cronjob_view(request):
	sequence_response()
	return HttpResponse("telnyx cronjob")
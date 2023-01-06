import requests
import time
import os
import requests
import telnyx
import datetime
import traceback

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from twilio.rest import Client
from signalwire.rest import Client as signalwire_client

from django.shortcuts import redirect, get_object_or_404

from django.contrib.sites.models import Site
from django.conf import settings

from .models import *
from base.models import CronTest
import logging


logger = logging.getLogger("error_logger")


def error_handler(error, view, reason):
	if not Error.objects.filter(error=error, view=view).exists():
		Error.objects.create(error=error, view=view, reason=reason)

def get_dnis(dnis):
	dnis = dnis.strip()
	if "+1" not in dnis[0:2]:
		dnis = dnis.replace("+","")
		if dnis[0] == '1':
			dnis = '+' + dnis.strip()
		else:
			dnis = '+1' + dnis.strip()

	return dnis

def send_fax(auth, gateway, ani, dnis, message, urls):
	try:
		error = None
		code = None
		fax_id = None
		status = None

		if "telnyx" in gateway.lower():
			try:
				TELNYX_FAX_URL = "https://api.telnyx.com/v2/faxes"
				TELNYX_API_KEY = auth['tel_api'].strip()
			
				headers = {
					'Authorization': f"Bearer {TELNYX_API_KEY}"
				}

				data = {
					"media_url": urls[0],
					"connection_id": os.getenv("TELNYX_CONNECTION_ID"),
					"to": dnis,
					"from": ani,
				}

				res = requests.post('https://api.telnyx.com/v2/faxes', headers=headers, data=data)

				fax_id = res.json()['data']['id']
				
				if fax_id:
					code = 200
					status = "pending"
			except Exception as e:
				logger.error(str(e))

		elif "signalwire" in gateway.lower():
			try:
				client = signalwire_client(
					os.getenv("SIGNALWIRE_PROJECT_ID"),
					os.getenv("SIGNALWIRE_TOKEN"),
					signalwire_space_url = os.getenv("SIGNALWIRE_SPACE_URL"))

				fax = client.fax.faxes.create(
					from_=ani,
					to=dnis,
					media_url=urls[0])
				fax_id = fax.sid
			except Exception as e:
				print(e)
				logger.error(str(e))
	except Exception as err:
		print('fax sender error: ', traceback.format_exc())
		logger.error(str(e))
	return fax_id, error, code, status

def send_sms(auth, gateway, ani, dnis, message):
	msg_id = ""
	error = ""
	code = 0
	response = ""
	dnis = get_dnis(dnis)
	gateway = gateway.lower()

	if "pineapple" in gateway:
		user = auth["user"].strip()
		pwd = auth["password"].strip()
		# url string can't be broken, Broken line interrupts message encoding
		url = "http://163.172.233.88:8001/api?command=submit&ani={}&dnis={}&username={}&password={}&message={}&longMessageMode=cut&dataCoding=0".format(ani.strip(), dnis.strip(), user, pwd, message)
		r = requests.post(url)
		code = r.status_code
		try:
			msg_id = r.json().get('message_id')
		except:
			try:
				error = r.text.strip()
			except:
				pass

	elif "telnyx" in gateway.lower():
		telnyx.api_key = auth['tel_api'].strip()
		try:
			r = telnyx.Message.create(
			    from_ = ani,
			    to = dnis,
			    text = message,
			)
		except Exception as e:
			try:
				response = e.json_body['errors'][0]
				code = response['code']
				error = response['title'] + ". " + response["detail"]
			except:
				code = ''
				error = ''
		try:
			msg_id = r['id']
			print(msg_id)
		except:
			pass

	return [msg_id, error, code]

def send_mms(auth, gateway, ani, dnis, message, urls):
	msg_id = ""
	error = ""
	code = 0
	response = ""

	dnis = get_dnis(dnis)

	if gateway.lower() == "telnyx":

		telnyx.api_key = auth['tel_api'].strip()
		
		try:
			r = telnyx.Message.create(
			    from_ = ani,
			    to = dnis,
			    text = message,
			    media_urls = urls,
			)
		except Exception as e:
			response = e.json_body['errors'][0]
			code = response['code']
			error = response['title'] + ". " + response["detail"]
		try:
			msg_id = r['id']
			print(msg_id)
		except:
			pass

	return [msg_id,error,code]
	
def text_converter(text, fb_id):

	if fb_id:
		if "%%first_name%%" in text:
			f_name = FacebookLead.objects.get(id=fb_id).first_name
			if f_name:
				text = text.replace("%%first_name%%", f_name)
			else:
				text = text.replace("%%first_name%%", '')

		if "%%last_name%%" in text:
			l_name = FacebookLead.objects.get(id=fb_id).last_name
			if l_name:
				text = text.replace("%%first_name%%", l_name)
			else:
				text = text.replace("%%first_name%%", '')

		if "%%full_name%%" in text:
			full_name = FacebookLead.objects.get(id=fb_id).full_name
			if full_name:
				text = text.replace("%%full_name%%", full_name)
			else:
				text = text.replace("%%full_name%%", '')

		if "%%email%%" in text:
			email = FacebookLead.objects.get(id=fb_id).email
			if email:
				text = text.replace("%%full_name%%", email)
			else:
				text = text.replace("%%full_name%%", '')
	
	return text

def send_schedule_sms(scheduled_sms):
	msg_id = ""
	error = ""
	code = ""

	for item in scheduled_sms:

		scheduled_at = item.scheduled_at		
		time_now = timezone.now()

		if time_now >= scheduled_at:
			ani_id = item.ani_id
			ani = item.ani.ani
			dnis = item.dnis
			image_id = item.image_id
			msg = item.sent

			dnis = get_dnis(dnis)

			try:
				ani_obj = Ani.objects.get(id=ani_id)
				gateway_id = ani_obj.gateway_id
				gateway = str(ani_obj.gateway.gateway)
				auth = AddGateway.objects.filter(id=gateway_id).values()[0]
			except Exception as e:
				print(e)
			if item.image_id or item.gif_url:
				is_mms = True
				urls = []
				if item.image_id:
					url = Image.objects.filter(id=item.image_id)[0].image.url
					site = Site.objects.all()[0].domain
					url = site + url
					urls.append(url)
				if item.gif_url:
					urls.append(gif_url)

				r = send_mms(auth, gateway, ani, dnis, msg, urls)
			else:
				r = send_sms(auth, gateway, ani, dnis, msg)
			try:
				msg_id = r[0]
				if len(msg_id)<1:
					del_status = 'undelivered'
				else:
					del_status = ""
				error = r[1]
				code = r[2]
			except Exception as e:
				print(e)

			InOutSms.objects.filter(id=item.id).update(

					message_id = msg_id,
					error = error,
					code = code,
					del_status = del_status,
					is_scheduled = False,
				)
		else:
			continue
			
	worker.objects.filter(scheduled_sms=True).update(scheduled_sms=False)

def send_bulk(sms_objs):
	print('send bulk')
	if not Spam.objects.filter(spam='cron').exists():
		Spam.objects.create(spam='cron')
	time.sleep(.2)
	try:
		for item in sms_objs:
			error = ''
			code = ''
			del_status = ""
			msg_id = ""

			dnis = item.dnis
			ani = item.ani.ani
			print(ani)
			message = item.sent
			
			dnis = get_dnis(dnis)

			# print(item.gateway)
			gateway = item.gateway.gateway

			auth = AddGateway.objects.filter(gateway__gateway__contains=gateway).values()[0]
			urls = []
			if item.image_id or item.gif_url:
				if item.image_id:
					url = Image.objects.filter(id=item.image_id)[0].image.url
					site = Site.objects.all()[0].domain
					url = site + url
					urls.append(url)
				if item.gif_url:
					gif_url = item.gif_url
					if gif_url:
						urls.append(gif_url)

				r = send_mms(auth, gateway, ani, dnis, message, urls)
			else:
				r = send_sms(auth, gateway, ani, dnis, message)
			# print(r)
			try:
				msg_id = r[0]
				if len(msg_id)<1:
					del_status = "undelivered"
			except:
				pass
			try:
				error = r[1]
				code = r[2]
			except Exception as e:
				print(e)
				pass

			InOutSms.objects.filter(id=item.id).update(
				is_bulk=False,
				del_status = del_status,
				message_id = msg_id,
				error = error,
				code = code
			)
	except Exception as e:
		error_handler(
			error = str(e) + ", " + type(e).__name__ + ", line : " + \
				str(e.__traceback__.tb_lineno), 
			view = "func-send_bulk-tasker.py", 
			reason = "anything")

	worker.objects.update(is_bulk=False)


def send_bulk_sms(request, updated_request):
	"""
		params:
			requuest: to catch user
			updated_request: Manupulated request object to invoke img_id to catch new img
	"""
	print("bulk")
	time.sleep(.2)
	image = None
	is_mms = False
	msg_id = ""
	error = ""
	image_id = ""
	code = ""

	try:
		message = updated_request.get('message')
		unsubscribed_msg = updated_request.get('unsubscribed_msg')
		
		if unsubscribed_msg:
			message = message + '\n' + unsubscribed_msg

		bulk_name = updated_request.get('name')
		ani = updated_request.get('ani')
		gif_url = updated_request.get('gif_url')
		image_id = updated_request.get('image_id')
		contact_id = updated_request.get('form_id')
		leads = FacebookLead.objects.filter(contact_id = contact_id)

		if image_id:
			is_mms = True

		# check whether from primary number 4
		if request.user.is_superuser:
			pn = PrimaryNumber.objects.all()
			if pn:
				ani_id = pn[0].ani_id
				ani_objs = Ani.objects.filter(id=ani_id)
			else:
				ani_objs = Ani.objects.filter(admin__admin=request.user)
		else:
			ani_objs = Ani.objects.filter(admin__admin=request.user)

		admin_id = ani_objs[0].admin_id
		ani_id = ani_objs[0].id
		gateway_id = ani_objs[0].gateway.gateway_id

		bulk_obj = BulkSms.objects.create(
			name = bulk_name,
			ani_id = ani_id,
			message = message,
			contact_id = contact_id,
			image_id = image_id,
			gif_url = gif_url
		)
		bulk_sms_id = bulk_obj.id

		for item in leads:
			print(item.phone)
			msg = text_converter(message, item.id)
			dnis = item.phone

			dnis = get_dnis(dnis)

			if InOutSms.objects.filter(ani_id=ani_id,dnis__contains=dnis).exists():
				is_lead = False
			else:
				is_lead = True

			InOutSms.objects.create(
				admin_id = admin_id,
				contact_id = contact_id,
				bulk_sms_id = bulk_sms_id,
				gateway_id = gateway_id,
				ani_id = ani_id,
				image_id = image_id,
				gif_url = gif_url, 
				dnis = dnis,
				sent = msg, 
				message_id = msg_id, 
				is_mms = is_mms,
				is_bulk = True,
				is_lead = is_lead, 
			)

	except Exception as e:
		print(e)
		error_handler(
			error=str(e) + ", " + type(e).__name__ + ", line : " + \
				str(e.__traceback__.tb_lineno), 
			view="func-send_bulk_sms-tasker.py", 
			reason="anything")


def is_weekday(resp_obj):
	weekday = timezone.now().weekday()
	day = calendar.day_name[weekday]
	is_fri = False
	is_sat = False
	is_sun = False	
	is_mon = False	
	is_tue = False	
	is_wed = False	
	is_thu = False

	weekdays = ""
	if resp_obj.is_fri:
		weekdays = weekdays+" " + "Friday"
	if resp_obj.is_sat:
		weekdays = weekdays+" " + "Saturday"	
	if resp_obj.is_sun:
		weekdays = weekdays+" " + "Sunday"	
	if resp_obj.is_mon:
		weekdays = weekdays+" " + "Monday"	
	if resp_obj.is_tue:
		weekdays = weekdays+" " + "Tuesday"	
	if resp_obj.is_wed:
		weekdays = weekdays+" " + "Wednesday"	
	if resp_obj.is_thu:
		weekdays = weekdays+" " + "Thursday"	

	if day in weekdays:
		return True
	else:
		return False

# send autoresponded response
def send_first_sms(new_leads):

	print("new leads")
	try:
		for item in new_leads:
			is_mms = False
			fb_id = item.id
			dnis = str(item.phone)
			dnis = get_dnis(dnis)
			contact_id = item.contact_id
			
			print('contact_id',contact_id)

			# assigned drips
			resp_objs = Autoresponse.objects.filter(contact_id = contact_id, is_active=True)
			if not resp_objs:
				worker.objects.filter(new_leads=True).update(new_leads=False)

			if resp_objs:
				sms_objs = InOutSms.objects.filter(dnis__contains=dnis.replace("+",""))
				for resp_obj in resp_objs:

					print('response name: ',resp_obj.name)
					ani_id = resp_obj.ani_id
					try:
						response_exists = sms_objs.filter(
							ani_id = ani_id,
							autoresponse_id = resp_obj.id).exists()
					except:
						response_exists = False
						
					if not response_exists:

						ani = resp_obj.ani.ani.strip()
						add_gateway_id = resp_obj.ani.gateway_id
						gateway = str(resp_obj.ani.gateway.gateway)
						autoresponse_id = resp_obj.id

						delay_days = resp_obj.delay_days
						delay_hours = resp_obj.delay_hours
						delay_mins = resp_obj.delay_mins

						print("delay",delay_mins, delay_days, delay_hours)

						r_time = item.timestamp
						ex_time = r_time + timedelta(days=delay_days,hours=delay_hours, \
							minutes=delay_mins, seconds=0)
						time_now = timezone.now()

						# Check Time Between
						first_time = resp_obj.first_time
						last_time = resp_obj.last_time

						# Check send to this day
						if resp_obj.everyday:
							weekday = True
						else:
							weekday = is_weekday(resp_obj)

						if first_time and last_time:
							current_time = datetime.now().time()
							if str(first_time) < str(current_time) < str(last_time):
								time_between = True
							else:
								time_between = False
						else:
							time_between = True

						print("checking time.........")
						if time_now >= ex_time and time_between and weekday:
							print('yesssssss, Time is over!')

							link = ""
							msg_id = ""
							error = ""
							code = None
							del_status = ''
							is_mms = False
							image_id = ''
							gif_url = ''

							# msg to be sent and it should be sequence 1
							next_message = resp_obj.response
							admin = resp_obj.admin.admin
							admin_id = resp_obj.admin_id

							message = text_converter(next_message, fb_id)

							# print('converted message',message)
							# Find the gateway
							try:
								auth = AddGateway.objects.filter(id=add_gateway_id).values()[0]
							except Exception as e:
								print(e)
							if resp_obj.image_id or resp_obj.gif_url:
								print("yesssssssss")
								is_mms = True
								urls = []
								if resp_obj.image_id:
									print('url')
									image_id = resp_obj.image_id
									url = Image.objects.filter(id=image_id)[0].image.url
									print(url)
									site = Site.objects.all()[0].domain
									url = site + url
									print(url)
									urls.append(url)
								if resp_obj.gif_url:
									gif_url = resp_obj.gif_url
									print(gif_url)
									urls.append(gif_url)

								r = send_mms(auth, gateway, ani, dnis, message, urls)
							else:
								r = send_sms(auth, gateway, ani, dnis, message)
								is_mms = False
								gif_url = None
							msg_id = r[0]
							if len(msg_id)<1:
								del_status = "undelivered"

							try:
								error = r[1]
								code = r[2]
							except:
								pass

							if InOutSms.objects.filter(
								ani_id = ani_id,
								dnis__contains = dnis.strip(), 
								is_lead=True).exists():
								
								is_lead = False
							else:
								is_lead = True
							if len(msg_id)>1:
								try:
									InOutSms.objects.create(
										admin_id = admin_id,
										check_keyword = True,
										autoresponse_id = autoresponse_id,
										contact_id = contact_id,
										ani_id = ani_id,
										image_id = image_id,
										gif_url = gif_url, 
										dnis = dnis.strip(),
										sent = message, 
										message_id = msg_id, 
										del_status = del_status,
										is_mms = is_mms,
										is_lead = is_lead, 
										code = code)
								except Exception as e:
									print(e)
							else:
								# if msg_id doesn't return, delivery status will be shown undelivered
								# print("yesssss")
								InOutSms.objects.create(
									admin_id = admin_id,
									check_keyword = True,
									autoresponse_id = autoresponse_id,
									contact_id = contact_id, 
									ani_id = ani_id,
									image_id = image_id,
									gif_url = gif_url,
									dnis = dnis.strip(),
									sent = message, 
									error = error, 
									message_id = msg_id,
									del_status = 'undelivered',
									is_mms = is_mms,
									is_lead = is_lead, 
									code=code)
							break

	except Exception as e:
		error_handler(
			error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
			view="tasker-send_first_sms", 
			reason='anything')	

	worker.objects.filter(new_leads=True).update(new_leads=False)


def keyword_response(incoming_sms):
	print("keyword_response")
	# print(incoming_sms)
	is_seen = False

	try:
		for item in incoming_sms:
			reply = item.reply
			keyword_id = item.id
			dnis = item.dnis
			
			dnis = get_dnis(dnis)

			if reply:
				is_seen = False
				ani_id = item.ani_id
				admin_id = item.admin_id
				admin = item.admin.admin
				reply = item.reply

				contacts = list(AdForm.objects.values("id"))
				contact_ids = []

				for item in contacts:
					contact_ids.append(item.get("id"))

				keywords = LogicResponse.objects.filter(contact_id__in = contact_ids)
				if keywords:
					keyword_exists = False
					for keyword in keywords:
						if keyword.keywords.strip().lower() == reply.strip().lower():
							contact_id = keyword.contact_id
							if not FacebookLead.objects.filter(contact_id=contact_id, phone__contains=dnis).exists():
								FacebookLead.objects.create(

										contact_id = contact_id,
										phone = dnis,
										to_reply = True,
									)
							keyword_exists = True
							break
						else:
							continue
				else:
					InOutSms.objects.filter(dnis__contains=dnis.replace("+","")).update(
							check_keyword=True, 
							is_seen=is_seen
						)
					continue
				if keyword_exists:
					image_id = None
					gif_url = ''
					is_mms = False
					msg_id = ""
					error = ''
					code = ''
					del_status = ''

					# Find the gateway
					ani_obj = Ani.objects.filter(admin_id=admin_id)[0]
					ani_id = ani_obj.id
					ani = ani_obj.ani
					add_gateway_id = ani_obj.gateway_id
					gateway = str(ani_obj.gateway.gateway)
					auth = AddGateway.objects.filter(id=add_gateway_id).values()[0]


					msg = text_converter(keyword.reply, fb_id=None)
					if keyword.image_id or keyword.gif_url:
						is_mms = True
						urls = []
						if keyword.image_id:
							image_id = keyword.image_id
							url = Image.objects.get(id=image_id).image.url
							site = Site.objects.all()[0].domain
							url = site + url
							urls.append(url)
						if keyword.gif_url:
							gif_url = keyword.gif_url
							urls.append(gif_url)
						r = send_mms(auth, gateway, ani, dnis, msg, urls)
					else:
						r = send_sms(auth, gateway, ani, dnis, msg)
					is_seen = True
					msg_id = r[0]

					try:
						error = r[1]
						code = r[2]
					except:
						pass

					if InOutSms.objects.filter(
						ani_id = ani_id,
						dnis__contains = dnis.replace("+", ""), 
						is_lead=True).exists():
						
						is_lead = False
					else:
						is_lead = True
					if len(msg_id)>1:
						try:
							InOutSms.objects.create(
								admin_id = admin_id,
								contact_id = contact_id,
								ani_id = ani_id,
								image_id = image_id,
								gif_url = gif_url, 
								dnis = dnis,
								sent = msg, 
								message_id = msg_id, 
								del_status = del_status,
								is_mms = is_mms,
								is_lead = is_lead, 
								code = code)
						except Exception as e:
							print(e)
					else:
						# if msg_id doesn't return, delivery status will be shown undelivered
						InOutSms.objects.create(
							admin_id = admin_id,
							contact_id = contact_id, 
							ani_id = ani_id,
							image_id = image_id,
							gif_url = gif_url,
							dnis = dnis,
							sent = msg, 
							error = error, 
							message_id = msg_id,
							del_status = 'undelivered',
							is_mms = is_mms,
							is_lead = is_lead, 
							code=code)
				
				else:
					assign_objs = AssignContact.objects.filter(
						admin_id = admin_id, 
						contact__form_name = "untitled")
					if assign_objs.exists():
						contact_id = AssignContact.objects.filter(admin_id=admin_id)[0].contact_id
						if not FacebookLead.objects.filter(contact_id=contact_id, phone__contains=dnis).exists():
							FacebookLead.objects.create(

									contact_id = contact_id,
									phone = dnis,
									to_reply = True,
								)						
					else:
						contact_id = AdForm.objects.create(form_name="untitled").id
						AssignContact.objects.create(admin_id=admin_id, contact_id=contact_id)
						if not FacebookLead.objects.filter(contact_id=contact_id, phone__contains=dnis).exists():
							FacebookLead.objects.create(

									contact_id = contact_id,
									phone = dnis,
									to_reply = True,
								)
							
			InOutSms.objects.filter(dnis__contains=dnis.replace("+","")).update(
					check_keyword=True, 
					is_seen=is_seen)
	except Exception as e:

		error_handler(
			error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
			view = "tasker-keyword_response", 
			reason='anything')
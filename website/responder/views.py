import os, re, random, json, datetime
from datetime import timedelta
from django.utils import timezone
from time import sleep
import csv
import threading

from .tasker import *
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, When, Case, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from .models import *

from .serializers import *

User = get_user_model()


@login_required
def pn_view(request):
	if request.method == "POST":
		data = json.loads(request.body)
		check = data.get("check")
		if check == "add_primary_number":
			if data.get("ani_id") == "admin":
				PrimaryNumber.objects.all().delete()
			else:
				PrimaryNumber.objects.all().delete()
				PrimaryNumber.objects.create(
						ani_id = data.get("ani_id")
					)
			json_data = {

			}
		return JsonResponse(data = json_data, status=200)
	else:
		json_data = {
	
			}
		return JsonResponse(data = json_data, status=400)

@login_required
def keywords_view(request):

	pages = ""
	logics = ""
	logic_obj = ""
	alert = ""
	error = ''
	images = ''
	contacts = ''

	if request.method == "POST":
		check = request.POST['check']
		admin_id = get_object_or_404(Admin, admin__username=request.user.username).id

		if check == 'logic':
			try:
				image = request.FILES['image']
			except:
				image = None
			new_list = request.POST.get("new_list")
			if new_list:
				contact_id = AdForm.objects.create(form_name=new_list).id
			else:
				contact_id = request.POST.get("contact_id")
			keys = request.POST.get('keys')
			gif_url = request.POST.get('gif_url')
			response = request.POST.get('response')
			unsubscribed_msg = request.POST.get('unsubscribed_msg')
	
			if unsubscribed_msg:
				response = response + '\n' + unsubscribed_msg
			image_id = request.POST.get("image_id")

			if image:
				count = Image.objects.count()
				try:
					img_name = "name{}".format(count+1)
					image_obj = Image.objects.create(name = img_name, image=image)
					image_id = image_obj.id
				except Exception as e:
					print("image", e)
			pn = PrimaryNumber.objects.all()
			if pn:
				ani_id = pn[0].ani_id

			LogicResponse.objects.create(
				admin_id = admin_id, 
				ani_id = ani_id, 
				contact_id = contact_id, 
				keywords = keys,
				image_id = image_id,
				gif_url = gif_url, 
				reply = response)

		elif check == 'delete':
			logic_ids = request.POST.getlist('logic')
			LogicResponse.objects.filter(id__in=logic_ids).delete()
			alert = "Deleted Succesfully"
	else:
		if request.method == "POST":
			error = "Permission Denied"
	try:
		if request.user.is_superuser:
			contacts = AdForm.objects.all()
		else:
			contacts = AssignContact.objects.filter(admin__admin=request.user)
	except:
		pass
	try:
		if request.user.is_superuser:
			images = Image.objects.all()
		else:
			images = Image.objects.filter(admin__admin=request.user)
	except:
		pass

	pn = PrimaryNumber.objects.all()
	try:
		if request.user.is_superuser:
			if pn:
				ani_id = pn[0].ani_id
				logics = LogicResponse.objects.filter(ani_id=ani_id)
				print(logics.values())
			else:
				logics = LogicResponse.objects.all()
		else:
			ani_id = None
			ani_objs = AssignedAni.objects.filter(admin__admin=request.user)
			if ani_objs:
				ani_id = ani_objs[0].ani_id
			logics = LogicResponse.objects.filter(ani_id=ani_id).order_by("-id")
	except:
		pass
	try:
		if logics:
			page = request.GET.get('page', 1)
			paginator = Paginator(logics, 10)
			try:
				pages = paginator.page(page)
			except PageNotAnInteger:
			    pages = paginator.page(1)
			except EmptyPage:
			    pages = paginator.page(paginator.num_pages)
	except Exception as e:
		print(e)
		pass
	context = {
		"pages":pages,
		"images": images,
		"contacts":contacts,
		"alert":alert,
		"error": error,
	}
	return render(request, 'sidemenu/keyword.html', context)

@login_required
def edit_keyword_view(request, keyword_id):

	if request.user.is_superuser:
		images = Image.objects.all()
	else:
		images = Image.objects.filter(admin__admin=request.user)
	if request.method == "POST":
		try:
			image = request.FILES['image']
		except:
			image = None
		keywords = request.POST.get("keywords")
		reply = request.POST.get("reply")
		contact_id = request.POST.get("contact_id")
		image_id = request.POST.get("image_id")
		gif_url = request.POST.get("gif_url")

		if image:
			count = Image.objects.count()
			try:
				img_name = "name{}".format(count+1)
				image_obj = Image.objects.create(name = img_name, image=image)
				image_id = image_obj.id
			except Exception as e:
				print("image", e)

		LogicResponse.objects.filter(id = keyword_id).update(
			
			keywords = keywords,
			contact_id = contact_id,
			image_id = image_id,
			gif_url = gif_url, 
			reply = reply)

		return redirect(reverse('responder:keywords'))

	logic_obj = LogicResponse.objects.get(id=keyword_id)
	contact_id = logic_obj.contact_id
	if request.user.is_superuser:
		contacts = AdForm.objects.exclude(id=contact_id)
	else:
		contacts = AssignContact.objects.filter(admin__admin=request.user).exclude(contact_id=contact_id)

	context = {
		"images": images,
		"keyword": logic_obj,
		"contacts": contacts
	}
	return render(request, 'sidemenu/edit_keyword.html', context)

@login_required
def auto_responders_view(request):

	if request.is_ajax():
		data = json.loads(request.body)
		check = data.get("check")

		if check == "response_details":
			resp_id = data.get('resp_id')
			resp_details = Autoresponse.objects.get(id = resp_id)
			serializer = AutoresponseSerializer(instance=resp_details)
			json_data = {
				'resp_details': serializer.data
			}
			return JsonResponse(data=json_data, status=200)

		elif check == "response_delete":
			resp_id = data.get("resp_id")
			Autoresponse.objects.filter(id=resp_id).delete()
			sms_objs = InOutSms.objects.filter(autoresponse_id=resp_id)
			if sms_objs:
				sms_objs.delete()

			json_data = {

			}
			return JsonResponse(data=json_data, status=200)

		elif check == "pause_response":
			resp_id = data.get("resp_id")
			is_active = data.get("is_active")

			if is_active:
				is_active = False
			else:
				is_active = True

			Autoresponse.objects.filter(id=resp_id).update(is_active=is_active)

			json_data = {

			}
			return JsonResponse(data=json_data, status=200)

		elif check == "create_title":
			title = data.get("title")

			admin_obj = get_object_or_404(Admin, admin=request.user)

			QuickResponseTitle.objects.create(
					admin = admin_obj,
					title = title
				)

			if request.user.is_superuser:
				titles = QuickResponseTitle.objects.all()
			else:
				titles = QuickResponseTitle.objects.filter(admin=request.user)

			if titles:
				titles = list(titles.values())

			json_data = {
				"titles":titles
			}
			return JsonResponse(data = json_data, status=200)

		elif check == "quick_response":
			response = data.get("response")
			title_id = data.get("group_title_id")

			if response:
				admin_obj = get_object_or_404(Admin, admin = request.user)
				QuickResponse.objects.create(
					admin = admin_obj, 
					title_id = title_id,
					response=response)

				data = {

				}

				return JsonResponse(data=data, status=200 )
			else:
				return JsonResponse(data=None, status=400)

		elif check == "get_quick_response":
			resp_id = data.get('quic_resp_id')
			response = QuickResponse.objects.get(id=resp_id).response

			data = {
				'response': response
			}
			return JsonResponse(data=data, status=200)

		elif check == "edit_response":
			resp_id = data.get("resp_id")
			title_id = data.get("title_id")
			response = data.get("response")

			QuickResponse.objects.filter(id=resp_id).update(
					title_id = title_id,
					response=response
				)

			json_data = {

			}

			return JsonResponse(data = json_data, status=200)

		elif check == "delete_title":
			title_id = data.get("title_id")

			QuickResponseTitle.objects.filter(id=title_id).delete()
			json_data = {

			}
			return JsonResponse(data = json_data, status=200)		

		elif check == "edit_title":
			title_id = data.get("title_id")
			title = data.get("group_title")

			QuickResponseTitle.objects.filter(id=title_id).update(
					title = title
				)
			json_data = {

			}
			return JsonResponse(data = json_data, status=200)

		elif check == "get_title_to_edit":
			title_id = data.get("title_id")

			title = list(QuickResponseTitle.objects.filter(id=title_id).values())[0]
			json_data = {
				'title': title
			}
			return JsonResponse(data=json_data, status=200)

		elif check == "get_single_response":
			resp_id = data.get("resp_id")

			response = QuickResponse.objects.get(id=resp_id)
			serializer = QuickResponseSerializer(instance=response)

			json_data = {
				"response": serializer.data
			}

			return JsonResponse(data = json_data, status=200)


		elif check == "delete_response":
			resp_id = data.get("resp_id")

			QuickResponse.objects.filter(id=resp_id).delete()

			data = {
			}

			return JsonResponse(data=data, status=200)

		elif check == "get_titles":
			titles = ""
			if request.user.is_superuser:
				titles = QuickResponseTitle.objects.all()
			else:
				titles = QuickResponseTitle.objects.filter(admin__admin=request.user)
			if titles:
				serializer = QuickResponseTitleSerializer(instance=titles, many=True)

			json_data = {
				"titles":serializer.data
			}
			return JsonResponse(data = json_data, status=200)

	elif request.method == "POST":
		check = request.POST.get("check")
		if check == "create":
			everyday = True
			try:
				image = request.FILES['image']
			except:
				image = None
			name = request.POST.get("name")
			response = request.POST.get("response")
			unsubscribed_msg = request.POST.get("unsubscribed_msg")
			if unsubscribed_msg:
				response = response+'\n'+unsubscribed_msg

			gif_url = request.POST.get("gif_url")
			contact_id = request.POST.get("form_ids")
			image_id = request.POST.get("image_id")
			delay_days = request.POST.get("delay_days")
			delay_mins = request.POST.get("delay_mins")
			delay_hours = request.POST.get("delay_hours")
			first_time = request.POST.get("first_time")
			last_time = request.POST.get("last_time")

			# FacebookLead.objects.filter(contact_id=contact_id).update(
			# 		to_reply = True,
			# 		is_active = True
			# 	)

			if not first_time:
				first_time = None
			if not last_time:
				last_time = None
			if not delay_days:
				delay_days = 0
			if not delay_mins:
				delay_mins = 0
			if not delay_hours:
				delay_hours = 0
			is_sat = request.POST.get("is_sat")
			is_sun = request.POST.get("is_sun")
			is_mon = request.POST.get("is_mon")
			is_tue = request.POST.get("is_tue")
			is_wed = request.POST.get("is_wed")
			is_thu = request.POST.get("is_thu")
			is_fri = request.POST.get("is_fri")

			if is_sat == "on":
				is_sat = True
				everyday = False
			else:
				is_sat = False			
			if is_sun == "on":
				is_sun = True
				everyday = False
			else:
				is_sun = False

			if is_mon == "on":
				is_mon = True
				everyday = False
			else:
				is_mon = False

			if is_tue == "on":
				is_tue = True
				everyday = False
			else:
				is_tue = False			

			if is_wed == "on":
				is_wed = True
				everyday = False
			else:
				is_wed = False			

			if is_thu == "on":
				everyday = False
				is_thu = True
			else:
				is_thu = False			

			if is_fri == "on":
				everyday = False
				is_fri = True
			else:
				is_fri = False

			if image:
				count = Image.objects.count()
				try:
					img_name = "name{}".format(count+1)
					image_obj = Image.objects.create(name = img_name, image=image)
					image_id = image_obj.id
				except Exception as e:
					print("image", e)
			admin_id = get_object_or_404(Admin, admin__username=request.user.username).id

			# find ani_id
			if request.user.is_superuser:
				ani_id = PrimaryNumber.objects.all()[0].ani_id

			Autoresponse.objects.create(
					name = name,
					admin_id = admin_id,
					ani_id = ani_id,
					contact_id = contact_id,
					image_id = image_id,
					gif_url = gif_url,
					response = response,
					delay_days = delay_days,
					delay_mins = delay_mins,
					delay_hours = delay_hours,
					is_sat = is_sat,
					is_sun = is_sun,
					is_mon = is_mon,
					is_tue = is_tue,
					is_wed = is_wed,
					is_thu = is_thu,
					is_fri = is_fri,
					everyday = everyday,
					first_time = first_time,
					last_time = last_time
				)
			return redirect(reverse("responder:auto-responders"))

	contacts = ''
	images = ''
	autoresponses = ''
	try:
		contacts = AdForm.objects.all()
	except:
		pass	
	try:
		images = Image.objects.filter(admin__admin=request.user)
	except:
		pass

	try:
		if request.user.is_superuser:
			pn = PrimaryNumber.objects.all()
			if pn:
				ani_id = pn[0].ani_id
				autoresponses = Autoresponse.objects.filter(ani_id=ani_id)
			else:
				autoresponses = Autoresponse.objects.all()
		else:
			ani_id = None
			anis = AssignedAni.objects.filter(admin__admin=request.user)
			if anis:
				ani_id = anis[0].ani_id
			autoresponses = Autoresponse.objects.filter(ani_id=ani_id).order_by("-id")
	except:
		pass

	context = {
		'autoresponses': autoresponses,
		'contacts': contacts,
		'images':images
	}

	return render(request, 'sidemenu/autoresponders.html', context)

@login_required
def auto_responders_edit_view(request, resp_id):

	if request.method == "POST":
		try:
			image = request.FILES['image']
		except:
			image = None
		name = request.POST.get("name")
		response = request.POST.get("response")
		contact_id = request.POST.get("contact_id")
		image_id = request.POST.get("image_id")
		gif_url = request.POST.get("gif_url")
		delay_days = request.POST.get("delay_days")
		delay_mins = request.POST.get("delay_mins")
		delay_hours = request.POST.get("delay_hours")
		first_time = request.POST.get("first_time")
			
		if not first_time:
			first_time = None
		last_time = request.POST.get("last_time")
		if not last_time:
			last_time = None

		if not delay_days:
			delay_days = 0
		if not delay_mins:
			delay_mins = 0
		if not delay_hours:
			delay_hours = 0
		is_sat = request.POST.get("is_sat")
		is_sun = request.POST.get("is_sun")
		is_mon = request.POST.get("is_mon")
		is_tue = request.POST.get("is_tue")
		is_wed = request.POST.get("is_wed")
		is_thu = request.POST.get("is_thu")
		is_fri = request.POST.get("is_fri")
		everyday = True
		if is_sat == "on":
			is_sat = True
			everyday = False
		else:
			is_sat = False			
		if is_sun == "on":
			is_sun = True
			everyday = False
		else:
			is_sun = False

		if is_mon == "on":
			is_mon = True
			everyday = False
		else:
			is_mon = False

		if is_tue == "on":
			is_tue = True
			everyday = False
		else:
			is_tue = False			

		if is_wed == "on":
			is_wed = True
			everyday = False
		else:
			is_wed = False			

		if is_thu == "on":
			everyday = False
			is_thu = True
		else:
			is_thu = False			

		if is_fri == "on":
			everyday = False
			is_fri = True
		else:
			is_fri = False

		admin_id = get_object_or_404(Admin, admin__username=request.user.username).id
		if image:
			count = Image.objects.count()
			try:
				img_name = "name{}".format(count+1)
				image_obj = Image.objects.create(admin_id=admin_id, name = img_name, image=image)
				image_id = image_obj.id
			except Exception as e:
				print("image", e)
		Autoresponse.objects.filter(id=resp_id).update(
			name = name,
			admin_id = admin_id,
			contact_id = contact_id,
			image_id = image_id,
			gif_url = gif_url,
			response = response,
			first_time = first_time,
			last_time = last_time,
			delay_days = delay_days,
			delay_mins = delay_mins,
			delay_hours = delay_hours,
			is_sat = is_sat,
			is_sun = is_sun,
			is_mon = is_mon,
			is_tue = is_tue,
			is_wed = is_wed,
			is_thu = is_thu,
			is_fri = is_fri,
			everyday = everyday,
		)
		return redirect(reverse("responder:auto-responders"))

	images = Image.objects.filter(admin__admin=request.user)
	if request.user.is_superuser:
		contacts = AdForm.objects.all()
	else:
		contacts = ""

	autoresponse = Autoresponse.objects.get(id = resp_id)

	context = {
		"autoresponse": autoresponse,
		"images": images,
		"contacts": contacts
	}
	return render(request, 'sidemenu/edit_autoresponder.html', context)

@login_required
def gallery_view(request, cam_id):
	alert = ""

	if request.method == "POST":
		check = request.POST.get("check")

		if check == 'gallery':			
			images = request.FILES.getlist('bulk-img')
			name = request.POST['name']
			if images:
				admin_obj = get_object_or_404(Admin, admin__username=request.user)
				i=1
				for image in images:
					Image.objects.create(name="{}-{}".format(name,i),admin=admin_obj,\
					 image=image)
					i+=1
				alert = "Images uploaded"
		elif check == "delete":
			items = request.POST.getlist("item_id")
			if items:
				images = Image.objects.filter(id__in=items)
				for image in images:
					try:
						os.remove(image.image.path)
						image.delete()
					except:
						pass
				alert = "Items Deleted Succesfully"
			else:
				error = "Please select items"

	try:
		images = ""
		if request.user.is_superuser:
			images = Image.objects.all()
		else:
			images = Image.objects.filter(admin__admin=request.user)
	except:
		pass

	context = {
		"alert": alert,
		"images": images

	}
	return render(request, 'responder/campaigns/gallery.html', context)

def test_view(request, slug):
	return render(request, 'test.html')

@login_required
def followup_view(request,cam_id):
	alert = ""
	error = ''
	user = Admin.objects.get(admin__username=request.user)
	is_response = user.is_response
	try:
		followups = ""
		cam_obj = ""

		admin_id = Campaign.objects.filter(id=cam_id)[0].admin_id
		try:
			followups = FollowupSms.objects.filter(admin_id=admin_id, campaign_id=cam_id).order_by('timestamp')
			cam_obj = Campaign.objects.all()
		except Exception as e:
			print(e)
		try:
			images = Image.objects.filter(admin__admin=request.user)
		except:
			pass
	except Exception as e:
		print(e)
	if request.method == "POST" or request.FILES and is_response:
		try:
			check = request.POST['check']
			if check == "bulk-sequence":
				sequences = request.FILES['bulk-file'].read().decode("utf-8").split("\n")
				for index, item in enumerate(sequences, 1):
					msg = None
					is_logic = False
					try:
						msg = item.strip()
					except Exception as e:
						print(e)
					try:
						FollowupSms.objects.create(admin_id=admin_id, campaign_id=cam_id,is_logic=is_logic,\
							sequence=index, message=msg)
						alert = "Added Succesfully"
					except Exception as e:
						print(e)
			elif check == "delete":
				f_ids = request.POST.getlist("followup_id")
				if f_ids:
					f_objs = FollowupSms.objects.filter(admin_id=admin_id, campaign_id=cam_id)
					for f_id in f_ids:
						f_objs.filter(id=f_id).delete()
					alert = "Deleted Succesfully"
			elif check == "single-add":

				image_obj = None
				if request.POST['image_id'] != "No":
					image_id = request.POST['image_id']
					image_obj = get_object_or_404(Image, id=image_id)
				elif request.FILES:
					try:
						image = request.FILES['image']
					except:
						pass
					if image:
						count = Image.objects.count()
						try:
							name = "name{}".format(count+1)
							Image.objects.create(name = name,image=image)
							image_obj = get_object_or_404(Image, name=name)
						except Exception as e:
							print("image", e)
				try:
					sequence = request.POST['sequence']
				except Exception as e:
					try:
						sequence = FollowupSms.objects.filter(campaign__id=cam_id)\
						.order_by("-sequence")[0].sequence+1
					except:
						sequence = 1
						pass
				# delay
				delay_days = request.POST.get('delay_days')
				if not delay_days:
					delay_days = 0
		
				delay_hours = request.POST.get('delay_hours')
				if not delay_hours:
					delay_hours = 0

				delay_mins = request.POST.get('delay_mins')
				if not delay_mins:
					delay_mins = 0
				try:
					message = request.POST['message']
				except Exception as e:
					print(e)
				try:
					logic = request.POST['logic']
				except Exception as e:
					print(e)
				if logic == "Yes":
					logic = True
				else:
					logic = False

				FollowupSms.objects.create(
					admin_id = admin_id,
					campaign_id = cam_id,
					sequence = sequence,
					delay_days = delay_days,
					delay_hours = delay_hours,
					delay_mins = delay_mins,
					message = message,
					is_logic = logic, 
					image=image_obj)
				alert = "Added Succesfully"
		except Exception as e:
			print(e)
	else:
		if request.method == 'POST':
			error = "Permission Denied"

	context= {
		'followups': followups,
		"images": images,
		'cam_id':cam_id,
		'cam_obj': cam_obj,
		"error":error,
		"alert":alert
	}
	return render(request,"responder/campaigns/follow-ups.html", context)

@login_required
def import_view(request):
	"""
	input: txt files containing numbers
	output: send bulk sms
	"""
	images = ""
	msg_id = ""
	anis = []
	alert = ""
	error = ""
	link = ""
	is_lead = False
	url = ''
	message = ""
	names = None
	numbers = None
	bulks = ''
	contacts = ""
	anis = ''

	user = Admin.objects.get(admin__username=request.user)
	is_bulk = user.is_bulk

	admin_id = user.id

	if request.is_ajax():
		data = json.loads(request.body)
		check = data.get('check')

		if check == "bulk_details":
			bulk_id = data.get("bulk_id")

			bulk_details = BulkSms.objects.get(id = bulk_id)
			serializer = BulkSmsSerializer(instance=bulk_details)

			json_data = {
				"bulk_details":serializer.data
			}
			return JsonResponse(data=json_data, status=200)

		elif check == "bulk_delete":
			bulk_id = data.get("bulk_id")

			BulkSms.objects.filter(id=bulk_id).delete()

			json_data = {

			}
			return JsonResponse(data=json_data, status=200)

	elif request.method == "POST" and is_bulk:
		try:
			check = request.POST["check"]

			if check == "default-message":
				image = ''
				try:
					image = request.FILES['image']
				except:
					pass
				if image:
					count = Image.objects.count()
					name = "image{}".format(count+1)
					admin_obj = get_object_or_404(Admin, admin=request.user)
					image_id = Image.objects.create(name=name, image=image, admin=admin_obj).id
					updated_request = request.POST.copy()
					updated_request['image_id'] = image_id
				else:
					updated_request = request.POST.copy()

				t = threading.Thread(target=send_bulk_sms, args=(request, updated_request,),)
				t.start()
				alert = "Bulk sms starts sending"

		except Exception as e:
			error_handler(
				error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
				view="Bulk sms", 
				reason="")

	else:
		if request.method == "POST":
			error = 'Import Error'
	try:
		if request.user.is_superuser:
			contacts = AdForm.objects.all()
		else:
			contacts = AssignContact.objects.filter(admin__admin=request.user)
	except Exception as e:
		print(e)
	try:
		images = Image.objects.filter(admin__admin=request.user)
	except:
		pass
	try:
		if request.user.is_superuser:
			pn = PrimaryNumber.objects.all()
			if pn:
				ani_id = pn[0].ani_id
				bulks = BulkSms.objects.filter(ani_id=ani_id)
			else:
				bulks = ""
		else:
			contacts = AssignContact.objects.filter(admin__admin=request.user)
			if contacts:
				ani_id = contacts[0].ani_id
				bulks = BulkSms.objects.filter(ani_id__in=ani_id)
			else:
				bulks = ""
	except:
		pass
	try:
		if request.user.is_superuser:
			anis = Ani.objects.all()
		else:
			anis = Ani.objects.filter(admin__admin=request.user)
	except:
		pass
		
	context = {
		"anis": anis,
		"bulks":bulks,
		"images":images,
		"alert":alert,
		"error":error,
		"contacts":contacts,
	}
	return render(request,"responder/campaigns/import-leads.html", context)

@login_required
def lead_view(request, id):

	leads = ""
	pages = ""
	try:
		is_registered = Admin.objects.filter(admin__username=request.user, is_permitted=True).exists()
	except:
		is_registered = False
	if is_registered:
		try:
			leads = InOutSms.objects.filter(admin__admin=request.user, campaign__id=id,is_lead=True).order_by("-timestamp").values()
		except:
			pass
		page = request.GET.get('page', 1)
		paginator = Paginator(leads, 10)
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
		    pages = paginator.page(1)
		except EmptyPage:
		    pages = paginator.page(paginator.num_pages)
		if request.method == "POST":
			check = request.POST["check"]
			if check == "delete":
				dniss = request.POST.getlist("dnis")
				to_delete = InOutSms.objects.filter(admin__admin=request.user, campaign_id=id)
				for dnis in dniss:
					try:
						to_delete.filter(dnis=dnis).delete()
					except:
						pass

	context = {
	
		"pages":pages
	}	
	return render(request,"responder/campaigns/leads.html", context)

@login_required
def side_conversations_view(request):
	leads = ""
	chats = ""
	is_manual = False
	spams = []
	chats = ""
	msg_id = ""
	ani_dnis = ""
	dnis = ""
	perms = ""
	json_data = ""

	try:
		perms = Admin.objects.filter(admin__username=request.user)[0]
	except:
		pass
	if request.is_ajax():
		if request.method == 'GET':
			images = list(Image.objects.values().order_by('-id'))[:6]
			json_data = {
				'images': images
			}
			return JsonResponse(json_data, status=200)

		if request.method == 'POST':
			if request.FILES:
				check = request.POST.get("check")
				if check == "upload_image":
					image = request.FILES.get("image")

					if image:
						admin_obj = get_object_or_404(Admin, admin__username=request.user)
						image_id = Image.objects.count()
						name = 'image_{}'.format(image_id)
						Image.objects.create(
							admin = admin_obj, 
							name = name, 
							image=image)
					images = list(Image.objects.values().order_by('-id')[:6])
					json_data = {
						"images": images
					}
					return JsonResponse(json_data, status=200)

			else:
				data = json.loads(request.body)
				check = data['check']

				if check == "get_user_name":
					admin_id = data.get('admin_id')
					username = Admin.objects.get(id=admin_id).admin.username
					
					json_data = {
						'username':username
					}
					return JsonResponse(json_data, status=200)

				elif check == "cancel_scheduled_sms":
					sms_id = data.get("sms_id")
					obj = InOutSms.objects.get(id=sms_id)
					obj.delete()

					json_data = {}

					return JsonResponse(json_data, status=200)

				elif check == 'update_list':

					first_name = data.get('contact').get("first_name", "")
					last_name = data.get('contact').get("last_name", "")
					email = data.get('contact').get("email", "")
					lead_id = data.get("contact").get("id")

					if not lead_id:
						dnis = data.get("dnis")
						lead_id = FacebookLead.objects.create(
								first_name = first_name,
								last_name = last_name,
								phone = dnis,
								full_name = '{} {}'.format(first_name, last_name),
								email = email
							).id

					contact_id = data.get("list").get("id")

					FacebookLead.objects.filter(id=lead_id).update(
							first_name = first_name,
							last_name = last_name,
							full_name = '{} {}'.format(first_name, last_name),
							email = email,
							contact_id = contact_id,
						)
					data = {
						'success': True
					}
					return JsonResponse(data=data, status=200)

				elif check == 'get_list':
					dnis = data.get('dnis')
					lists = ''

					if request.user.is_superuser:
						lists = AdForm.objects.all()
						lists_serializer = AdFormSerializer(instance=lists, many=True)

					contacts = FacebookLead.objects.filter(phone__contains=dnis)

					contact = ''
					if contacts:
						contact = contacts[0]
						contact_serializer = FacebookLeadSerializer(instance=contact)
						contact = contact_serializer.data
					
					data = {
						'contact': contact,
						'lists': lists_serializer.data
					}
					return JsonResponse(data=data, status=200)

				elif check == "delete_response":

					resp_id = data.get("resp_id")
					QuickResponse.objects.filter(id=resp_id).delete()

					responses = list(QuickResponse.objects.filter(admin__admin=request.user).order_by('-id').values())

					data = {
						'responses':responses
					}
					return JsonResponse(data=data, status=200)

				elif check == "get_quick_response":

					resp_id = data.get('quic_resp_id')
					response = QuickResponse.objects.get(id=resp_id).response

					data = {
						'response': response
					}
					return JsonResponse(data=data, status=200)

				elif check == 'manage_like':
					sms_id = data.get("sms_id")
					if not Like.objects.filter(sms_id=sms_id, admin__admin__username=request.user.username):
						admin_obj = get_object_or_404(Admin, admin=request.user)
						Like.objects.create(sms_id=sms_id, admin=admin_obj)

				elif check == "quick_response":
					response = data.get("response")
					if response:
						admin_obj = get_object_or_404(Admin, admin = request.user)
						QuickResponse.objects.create(admin = admin_obj, response=response)

						data = {
							'responses': list(QuickResponse.objects.filter(admin__admin=request.user).order_by('-id').values())
						}

						return JsonResponse(data=data, status=200 )
					else:
						return JsonResponse(data=None, status=400)

				elif check == "switch_autoresponse":

					dnis = data.get("dnis")
					manual = data.get("is_manual")
					if not manual:
						manual = True
					else:
						manual = False

					FacebookLead.objects.filter(phone__contains=dnis.replace("+", "")).update(is_active=manual)

					json_data = {
						"is_manual": manual
					}
					return JsonResponse(json_data, status=200)

				elif check == "leads":
					first = data['first']
					second = data['second']
					filter_type = data.get('filter_type')
					leads = ""
					ani = ''
					total_lead = 0
					
					if request.user.is_superuser:
						# print('total_lead')
						pn = PrimaryNumber.objects.all()
						if pn:
							ani_id = pn[0].ani_id
							if filter_type == "newest wait":
								lead_objs = InOutSms.objects.filter(
									ani_id = ani_id,
									is_lead=True,
								).order_by('-is_wait', '-reply_at')
							else:
								lead_objs = InOutSms.objects.filter(
									ani_id = ani_id,
									is_lead=True,
								).order_by('-is_wait', 'reply_at')

							if lead_objs:
								total_lead = lead_objs.count()
								lead_objs = lead_objs[first:second]

							ani = pn[0].ani.ani
					else:
						ani_objs = AssignedAni.objects.filter(admin__admin=request.user)
						if ani_objs:
							ani_id = ani_objs[0].ani_id
							ani = ani_objs[0].ani.ani

							if filter_type == "newest wait":
								lead_objs = InOutSms.objects.filter(
									ani_id = ani_id,
									is_lead=True).order_by('has_incoming').order_by("-reply_at")
							else:
								lead_objs = InOutSms.objects.filter(
									ani_id = ani_id,
									is_lead=True).order_by('has_incoming').order_by("reply_at")
							if lead_objs:
								total_lead = lead_objs.count()
								lead_objs = lead_objs[first:second]

					if lead_objs:
						serializer = InOutSmsSerializer(instance=lead_objs, many=True)
						leads = serializer.data
					else:
						leads = None							
					json_data = {
						"leads":leads,
						"total_lead": total_lead,
						"ani": ani,
					}
					return JsonResponse(json_data, status=200)

				elif check == "search_dnis":
					leads = ''
					dnis = data['dnis']
					print(dnis)
					if request.user.is_superuser:
						pn = PrimaryNumber.objects.all()
						if pn:
							ani_id = pn[0].ani_id
							leads_obj = InOutSms.objects.filter(
								is_lead = True,
								ani_id = ani_id, 
								dnis__contains = dnis)
						
					else:
						ani_id = Ani.objects.filter(admin__admin=request.user)[0].id
						if len(dnis)>1:
							leads_obj = InOutSms.objects.filter(ani_id=ani_id, \
							is_lead=True, dnis__contains=dnis)
						else:
							leads_obj = InOutSms.objects.filter(ani_id=ani_id, \
							is_lead=True)

					if leads_obj:
						serializer = InOutSmsSerializer(instance=leads_obj, many=True)
						leads = serializer.data

					json_data = {
						"leads":leads
					}
					return JsonResponse(data = json_data, status=200)

				elif check == "remove_dnis":
					dnis = data['dnis']

					FacebookLead.objects.filter(phone__contains=dnis.replace("+", "")).delete()
					if request.user.is_superuser:
						InOutSms.objects.filter(dnis__contains=dnis.replace("+","")).delete()
					else:
						InOutSms.objects.filter(
							admin__admin = request.user, 
							dnis = dnis.strip()).delete()

					json_data = {
					}
					
					return JsonResponse(data = json_data, status=200)

				elif check == "send_note":
					error = ""
					ani = data.get("ani")
					dnis = data.get("dnis")
					note = data.get("message")

					if request.user.is_superuser:
						pn = PrimaryNumber.objects.all()
						if pn:
							ani_id = pn[0].ani_id
							ani_objs = Ani.objects.filter(id__contains=ani_id)
					else:
						ani_objs = Ani.objects.filter(admin__admin=request.user)

					ani_objs = Ani.objects.filter(ani=ani.strip())
					ani_id = ani_objs[0].id
					admin_id = ani_objs[0].admin_id
					gateway = ani_objs[0].gateway.gateway.gateway

					if note is not "":
						InOutSms.objects.create(
							admin_id = admin_id,
							dnis = dnis, 
							ani_id = ani_id, 
							note = note)

					if request.user.is_superuser:
						chats = InOutSms.objects.filter(dnis__contains=dnis[1:].strip()).order_by("id")
					else:
						chats = InOutSms.objects.filter(ani_id=ani_id, dnis__contains=dnis[1:].strip()).\
							order_by("id")

					if chats:
						serializer = InOutSmsSerializer(instance=chats, many=True)
						chats = serializer.data

					json_context = {
						"chats":chats,
					}
					return JsonResponse(data = json_context, status=200)

				elif check == "new_message":
					print("new message")
					# print(data)

					error = ""
					dnis = data.get("new_number")

					dnis = get_dnis(dnis)

					message = data.get("new_message")
					scheduled_at = data.get("scheduled_at")
					image_id = data.get('mms')
					gif_url = data.get('gif_url')

					if request.user.is_superuser:
						pn = PrimaryNumber.objects.all()
						if pn:
							ani_id = pn[0].ani_id
							ani_objs = Ani.objects.filter(id=ani_id)
						else:
							ani_objs = Ani.objects.filter(admin__admin=request.user)
					else:
						ani_objs = Ani.objects.filter(admin__admin=request.user)

					if ani_objs:
						ani_id = ani_objs[0].id
						ani = ani_objs[0].ani
						gateway_id = ani_objs[0].gateway_id
						gateway = ani_objs[0].gateway.gateway.gateway

						admin_id = get_object_or_404(Admin, admin=request.user).id

						if image_id or gif_url:
							is_mms = True
						else:
							is_mms = False

						auth = AddGateway.objects.filter(id=gateway_id).values()[0]

						if image_id or gif_url:
							urls = []
							is_mms = True

							if image_id:
								url = Image.objects.filter(id=image_id)[0].image.url
								site = Site.objects.all()[0].domain
								url = site + url
								urls.append(url)
							
							msg_id, error, code, status = send_fax(auth, gateway, ani, dnis, message, urls)
						else:
							pass
							# r = send_sms(auth, gateway, ani, dnis, message)
						is_lead = InOutSms.objects.filter(ani_id=ani_id, dnis__contains=dnis.replace("+","")).exists()
						
						if is_lead:
							is_lead = False
						else:
							is_lead = True

						sms_obj = InOutSms.objects.create(
							admin_id=admin_id,
							image_id=image_id,
							gif_url=gif_url,
							is_mms=is_mms, 
							ani_id=ani_id, 
							dnis=dnis, 
							sent=message,
							del_status=status,
							is_lead=is_lead,
							type='fax',
							message_id=msg_id)

						if not msg_id:
							sms_obj.error = error
							sms_obj.del_status = 'undelivered'
							sms_obj.save()

					if request.user.is_superuser:
						chats = InOutSms.objects.filter(dnis__contains=dnis.replace("+", "").strip()).order_by("id")
					else:
						chats = InOutSms.objects.filter(ani_id=ani_id, \
							dnis__contains=dnis.replace("+", "").strip()).order_by("id")
					if chats:
						dnis = chats[0].dnis
						ani = chats[0].ani.ani
						serializer = InOutSmsSerializer(instance=chats, many=True)
						chats = serializer.data

					json_context = {
						"chats":chats,
						"ani":ani,
						"dnis":dnis
					}
					return JsonResponse(data = json_context, status=200)

				elif check == "manual_text":
					print("Manual text")

					ani = data.get("ani")
					dnis = data["dnis"]
					message = data["message"]
					image_id = data.get("mms")
					gif_url = data.get("gif_url")
					scheduled_at = data["scheduled_at"]

					ani_objs = Ani.objects.filter(ani=ani.strip())
					ani_id = ani_objs[0].id
					gateway_id = ani_objs[0].gateway_id
					gateway = ani_objs[0].gateway.gateway.gateway
					print('GATEWAY', gateway)
					admin_id = ani_objs[0].admin_id
					if image_id:
						is_mms = True
					else:
						is_mms = False

					if scheduled_at:
						InOutSms.objects.create(
							admin_id = admin_id, 
							ani_id = ani_id,
							image_id = image_id,
							gif_url = gif_url,
							dnis = dnis, 
							sent = message,
							is_scheduled = True,
							is_mms = is_mms,
							scheduled_at = scheduled_at,
							message_id = msg_id)
					else:
						auth = AddGateway.objects.filter(id=gateway_id).values()[0]
						print("yesss")
						urls = []
						is_mms = True
						if image_id:
							url = Image.objects.filter(id=image_id)[0].image.url
							site = Site.objects.all()[0].domain
							url = site + url
							urls.append(url)
						if gif_url:
							urls.append(gif_url)
						print("yes 3")
						fax_id, error, code, status = send_fax(auth, gateway, ani, dnis, message, urls)		
						
						is_lead = InOutSms.objects.filter(ani_id=ani_id, dnis__contains=dnis.replace("+","")).exists()
							
						if is_lead:
							is_lead = False
						else:
							is_lead = True

						sms_obj = InOutSms.objects.create(
							admin_id=admin_id,
							image_id=image_id,
							gif_url=gif_url,
							is_mms=is_mms, 
							ani_id=ani_id, 
							dnis=dnis, 
							sent=message,
							del_status=status,
							is_lead=is_lead,
							type='fax',
							message_id=fax_id)
						
						if error:
							sms_obj.error = error
							sms_obj.code = code
							sms_obj.del_status = "undelivered"
							sms_obj.save()

					chats = ''
					ani = ''
					json_context = {
						"chats":chats,
						"ani":ani,
					}
					return JsonResponse(data = json_context, status=200)
	try:
		if request.session['dnis']:
			dnis = request.session.get("dnis")
			if request.user.is_superuser:
				chats = InOutSms.objects.filter(dnis__contains=dnis.strip()\
					).order_by('id')
			else:
				chats = InOutSms.objects.filter(admin__admin=request.user, dnis__contains=dnis.strip())\
				.order_by("id")
			request.session['dnis'] = ""
	except:
		pass

	if request.method == "POST" and not request.is_ajax():
		check = request.POST["check"]

		if check == 'manual':
			dnis = request.POST['dnis']
			sms_obj = InOutSms.objects.filter(dnis=dnis)
			if sms_obj.filter(is_manual=True).exists():
				sms_obj.update(is_manual=False)
			else:
				sms_obj.update(is_manual=True)
			return redirect(reverse('responder:conversation', args=(cam_id,dnis)))
		else:
			pass

	context = {

	}
	
	return render(request, 'responder/campaigns/side-conversations.html', context)

@login_required
def chat_details(request, dnis):

	if request.is_ajax() and request.method == "POST":

		chats = ''
		ani = ''
		name = ''
		data = json.loads(request.body)
		check = data['check']
		dnis = dnis.replace("+", "")
		ani = data.get('ani')
		# print(data)
		if check == "chat_details":
			fb_objs = FacebookLead.objects.filter(phone__contains=dnis.replace("+",""))
			if fb_objs:
				is_manual = fb_objs[0].is_active
			else:
				is_manual=False
			if request.user.is_superuser:
				chats = InOutSms.objects.filter(
					ani__ani__contains=ani.replace('+', ""),
					dnis__contains=dnis.replace("+", "")).order_by("id")
			else:
				chats = InOutSms.objects.filter(
					ani__ani__contains=ani.replace('+', ""),
					dnis__contains=dnis.replace("+", "")).order_by("id")
			try:
				dnis = chats[0].dnis
				ani = chats[0].ani.ani
			except:
				pass
			try:
				name = chats[0].name
			except:
				pass
			chat_details = ''
			if chats:
				serializer = InOutSmsSerializer(instance=chats, many=True)
				chat_details = serializer.data
			
		json_context = {
			"chats": chat_details,
			"dnis":dnis,
			"name": name,
			"ani":ani,
			"is_manual": is_manual
		}
		return JsonResponse(json_context, status=200)

# sequence and schedule sms
def sequence_response():

	sms_obj = ""
	sms_objs = ""
	reason = ""
	admin_objs = ""
	is_mms = False
	code = 0
	
	# send bulk sms
	print("cronjob starts.....")
	if not CronJob.objects.all():
		CronJob.objects.create(is_bulk=False, is_sequence=True)

	try:
		incoming_sms = InOutSms.objects.filter(check_keyword=False)
		if incoming_sms:
			t = threading.Thread(target=keyword_response, args=(incoming_sms,))
			t.start()
	except Exception as e:
		print(e)
		
	worker_objs = worker.objects.all()
	if not worker_objs:
		worker.objects.create(scheduled_sms=False, new_leads=False, check_keyword=False)
	try:
		if worker.objects.filter(scheduled_sms=False).exists():
			scheduled_sms = InOutSms.objects.filter(is_scheduled=True)
			# send scheduled sms
			if scheduled_sms:
				worker.objects.filter(scheduled_sms=False).update(scheduled_sms=True)
				t = threading.Thread(target = send_schedule_sms, args=(scheduled_sms,))
				t.start()
	except Exception as e:
		print(e)

	try:
		if worker.objects.filter(new_leads=False):

			new_leads = FacebookLead.objects.filter(
				to_reply = True, 
				is_active = True, 
				is_unsubscribed = False
			)

			if new_leads:
				worker.objects.filter(new_leads=False).update(new_leads=True)
				t = threading.Thread(target=send_first_sms, args=(new_leads,))
				t.start()
			
		else:
			print("Worker is running!")
	except Exception as e:
		print(e)

def cronjob_view(request):
	print("cronjob")
	if not Spam.objects.filter(spam='cron').exists():
		Spam.objects.create(spam='cron')		
	try:
		sequence_response()
	except Exception as e:
		print(e)

	return render(request, 'responder/cronjob/cronjob.html')

def cronjob_bulk_view(request):
	print("cronjob bulk")
	if not CronJob.objects.all():
		CronJob.objects.create(is_bulk=False, is_sequence=True)
	if worker.objects.filter(is_bulk=False):
		worker.objects.update(is_bulk=True)		
		try:
			anis = Ani.objects.all()
			sms_objs = InOutSms.objects.filter(is_bulk=True)
			bulk_objs = None
			for ani in anis:
				if not bulk_objs:
					bulk_objs = sms_objs.filter(ani_id=ani.id)[:10]
					continue
				else:
					current_objs = sms_objs.filter(ani_id=ani.id)[:10]
					bulk_objs = bulk_objs | current_objs

			if bulk_objs:
				t = threading.Thread(target=send_bulk, args=(bulk_objs[:10],))
				t.start()
			else:
				print("no bulk to send")
				worker.objects.update(is_bulk=False)
		except Exception as e:
			print(e)

	return HttpResponse("Bulk Cronob", status=200)

@csrf_exempt
def pineapple_response(request):

	cam_obj = None
	is_spam = False
	is_followup = False
	is_manual = False
	link = ""
	sms_obj = ""
	states = ""
	# print(request.POST)
	if request.method == "POST":
		ani = request.POST["dnis"]
		msg_id = request.POST["message_id"]
		dnis = request.POST["ani"]
		message = request.POST["message"]

		# deactivate autoresponse
		new_dnis = dnis.replace("+","")
		fb_objs = FacebookLead.objects.filter(phone__contains=new_dnis)
		if fb_objs:
			fb_objs.update(to_reply=False)
		else:
			if new_dnis[0] == "1":
				fb_objs = FacebookLead.objects.filter(phone__contains=new_dnis[1:])
				if fb_objs:
					fb_objs.update(to_reply=False)

		if 'stop' in message.lower():
			FacebookLead.objects.filter(phone__contains=dnis).update(
					is_unsubscribed = True
				)
		
		ani_objs = Ani.objects.filter(ani__contains = ani)
		ani_id = ani_objs[0].id
		admin_id = ani_objs[0].admin_id

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

		pineapple_obj = get_object_or_404(Gateway, gateway__contains="Pineapple")

		# updating to_reply
		if InOutSms.objects.filter(ani_id=ani_id,dnis__contains=new_dnis,to_reply=True).exists():
			to_reply = False
		else:
			to_reply = True

		if check_duplicate:
			InOutSms.objects.create(
				gateway = pineapple_obj, 
				admin_id = admin_id,
				is_incoming = True, 
				dnis = dnis, 
				reply = message,
				to_reply = to_reply, 
				message_id = msg_id,
				check_keyword = False,
				ani_id = ani_id)
		else:
			InOutSms.objects.create(
				gateway = pineapple_obj,
				admin_id = admin_id,
				is_incoming = True, 
				dnis = dnis.strip(),
				reply = message, 
				message_id = msg_id, 
				ani_id = ani_id,
				check_keyword = False,
				to_reply = to_reply,
				has_incoming = True,
				is_lead = True)

		InOutSms.objects.filter(
			ani_id = ani_id,
			dnis__contains=dnis.replace("+", ""), 
			is_lead=True).update(
				is_seen = False,
				is_wait = True,
				has_incoming = True)

	return render(request, "responder/pineapple_response.html")
	# return HttpResponse(status=200)

@csrf_exempt
def pineapple_dlr(request):
	try:
		if request.method == "POST":
			msg_id = request.POST["message_id"]
			result_code = str(request.POST["error_code"]).strip()
			ani = request.POST["ani"]
			dnis = request.POST["dnis"]
			message = request.POST["message"]
			dlr_details = str(request.POST)

			try:
				sms_obj = InOutSms.objects.filter(dnis__contains = dnis.replace("+", ""), message_id=msg_id)
				admin = sms_obj[0].admin.admin
				campaign = sms_obj[0].campaign
				admin_obj = get_object_or_404(Admin, admin__username=admin)
				cam_obj = get_object_or_404(Campaign, campaign=campaign)
			except:
				pass
			if result_code == "000":
				try:
					obj = sms_obj[0]
					obj.dlr_details = dlr_details
					obj.del_status = "delivered"
					obj.save()
				except Exception as e:
					print(e)
			elif result_code == "470":
				try:
					obj =sms_obj[0]
					obj.dlr_details = dlr_details
					obj.code = 470
					obj.error = message
					obj.del_status = "undelivered"
					obj.save()
				except Exception as e:
					print(e)
			else:
				try:
					obj = sms_obj[0]
					obj.dlr_details = dlr_details
					# obj.reply = str(request.POST)
					obj.code = int(result_code)
					obj.error = message
					obj.del_status = "undelivered"
					obj.save()
				except Exception as e:
					print(e)
	except Exception as e:
		print(e, e.__traceback__.tb_lineno)
		error_handler(
			error=str(e) + ", " + type(e).__name__ + ", line : " + str(e.__traceback__.tb_lineno), 
			view="sequence response", 
			reason=reason)
	return render(request, "responder/pineapple_dlr.html")

def undelivered_view(request, cam_id):

	undelivered = ""
	is_dnis = False

	try:
		is_dnis = Admin.objects.filter(admin__username=request.user)[0].is_dnis
	except Exception as e:
		print(e)
	try:
		undelivered = InOutSms.objects.filter(admin__admin=request.user, campaign_id=cam_id, \
			del_status='undelivered').order_by('-timestamp')
	except Exception as e:
		print(e)
	page = request.GET.get('page', 1)
	paginator = Paginator(undelivered, 20)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
	    pages = paginator.page(1)
	except EmptyPage:
	    pages = paginator.page(paginator.num_pages)
	if request.method == "POST":
		check = request.POST['check']
		if check == "delete":
			ids = request.POST.getlist('sms_id')
			InOutSms.objects.filter(id__in=ids).delete()

	context = {

		"pages":pages,
		"is_dnis":is_dnis
	}
	return render(request, 'responder/campaigns/undelivered.html', context)

def undel_messages_view(request):

	undelivered = ""
	try:
		if request.user.is_superuser:
			undelivered = InOutSms.objects.filter(sent__isnull=False).exclude(del_status='delivered').order_by('-timestamp')			
		else:
			undelivered = InOutSms.objects.filter(admin__admin=request.user).filter(sent__isnull=False).exclude(del_status=\
				'delivered').order_by('-timestamp')
		InOutSms.objects.filter(admin__admin=request.user,is_seen=False).update(is_seen=True)
	except Exception as e:
		print(e)
	page = request.GET.get('page', 1)
	paginator = Paginator(undelivered, 30)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
	    pages = paginator.page(1)
	except EmptyPage:
	    pages = paginator.page(paginator.num_pages)
	if request.method == "POST":
		check = request.POST['check']
		if check == "delete":
			ids = request.POST.getlist('sms_id')
			InOutSms.objects.filter(id__in=ids).delete()

		elif check == "click here":
			dnis = request.POST.get("dnis")
			cam_id = request.POST.get("cam_id")
			request.session['dnis'] = dnis
			return redirect(reverse('responder:conversations', args=(cam_id,)))

		elif check == "export":
			dniss = InOutSms.objects.filter(sent__isnull=False).exclude(del_status='delivered').order_by('-timestamp')
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="undelivered.csv"'
			writer = csv.writer(response)
			cam_id = request.POST['cam_id']
			writer.writerow(["name", "number"])
			for item in dniss:
				dnis = item.dnis
				writer.writerow(['',dnis,])
			return response

		elif check == "delete_all":
			if request.user.is_superuser:
				sms = InOutSms.objects.filter(sent__isnull=False).exclude(del_status='delivered')
				sms.delete()
			else:
				sms = InOutSms.objects.filter(admin__admin=request.user, sent__isnull=False).exclude(del_status='delivered')
				sms.delete()

	context = {

		"pages":pages
	}
	return render(request, 'responder/campaigns/undelivered-messages.html', context)

def delivered_view(request, cam_id):

	delivered = ""
	try:
		delivered = InOutSms.objects.filter(admin__admin=request.user, campaign_id=cam_id, \
			del_status='delivered').order_by('-timestamp')
	except Exception as e:
		print(e)
	page = request.GET.get('page', 1)
	paginator = Paginator(delivered, 100)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
	    pages = paginator.page(1)
	except EmptyPage:
	    pages = paginator.page(paginator.num_pages)
	if request.method == "POST":
		check = request.POST['check']
		if check == "delete":
			ids = request.POST.getlist('id')
			sms_objs = InOutSms.objects.filter(admin__admin=request.user, campaign_id=cam_id)
			for sms_id in ids:
				sms_objs.filter(id=sms_id).delete()

	context = {

		"pages":pages
	}
	return render(request, 'responder/campaigns/delivered.html', context)

def logic_view(request, cam_id):
	logics = ""
	logic_obj = ""
	alert = ""
	error = ''

	user = Admin.objects.get(admin__username=request.user)
	is_response = user.is_response
	
	if  is_response or request.user.is_superuser:
		if request.method == "POST":
			check = request.POST['check']
			cam_obj = get_object_or_404(Campaign, id=cam_id)
			admin_id = cam_obj.admin_id

			if check == 'logic':
				keys = request.POST['keys']
				response = request.POST['response']
				LogicResponse.objects.create(admin_id=admin_id, campaign=cam_obj, keywords=keys, reply=response)
			elif check == "bulk-logic":
				sequences = request.FILES['bulk-file'].read().decode("utf-8").split(">>")
				for index, item in enumerate(sequences, 1):
					keys = None
					response = None
					items = ""
					try:
						items = item.strip().split('\n')
					except Exception as e:
						print(e)
					try:
						keys = items[0].replace("keywords:", "").strip()
					except Exception as e:
						print(e)				
					try:
						response = items[1].replace("reply:", "").strip()
					except Exception as e:
						print(e)
					if keys is not None and response is not None: 
						LogicResponse.objects.create(admin_id=admin_id, campaign=cam_obj, keywords=keys, reply=response)

				return redirect(reverse('responder:logic', args=(cam_id,)))

			elif check == 'delete':
				logic_ids = request.POST.getlist('logic')
				if logic_ids:
					for l_id in logic_ids:	
						objs = LogicResponse.objects.filter(admin_id=admin_id, campaign_id=cam_id, id=l_id)
						objs.delete()
					alert = "Deleted Succesfully"
	else:
		if request.method == "POST":
			error = "Permission Denied"
		
	try:
		logics = LogicResponse.objects.filter(campaign_id=cam_id)
		page = request.GET.get('page', 1)
		paginator = Paginator(logics, 20)
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
		    pages = paginator.page(1)
		except EmptyPage:
		    pages = paginator.page(paginator.num_pages)
	except:
		pass
	context = {

		"pages":pages,
		"cam_id": cam_id,
		"alert":alert,
		"error": error,
	}
	return render(request, 'responder/campaigns/logic-vault.html', context)

def logic_edit_view(request, cam_id, logic_id):

	alert = ""
	error = ""
	logic_obj = ""
	user = Admin.objects.get(admin__username=request.user)
	is_response = user.is_response
	if is_response or request.user.is_superuser:
		logic_obj = LogicResponse.objects.filter(
			campaign_id = cam_id, 
			id = logic_id)[0]
		if request.method == "POST" and is_response:
			check = request.POST["check"]
			if check == "edit":
				keywords = request.POST["keywords"]
				reply = request.POST["reply"]
				cam_obj = get_object_or_404(Campaign, id=cam_id)
				admin_id = cam_obj.admin_id
				LogicResponse.objects.filter(
					admin_id = admin_id, 
					campaign = cam_obj, 
					id=logic_id).update(keywords=keywords, reply=reply)

				return redirect(reverse('responder:logic', args=(cam_id,)))

		else:
			error = "Permission Denied"
	context = {
		'logic_obj': logic_obj,
		"alert":alert,
		"error":error,
	}

	return render(request, 'responder/campaigns/logic-vault-edit.html', context)

def response_edit_view(request, cam_id, resp_id):
	alert = ""
	error = ""
	images = ""
	# user obj to check user permission
	user = Admin.objects.get(admin__username=request.user)
	if user.is_response or request.user.is_superuser:
		admin_id = Campaign.objects.get(id = cam_id).admin_id
		resp_obj = Sequence.objects.filter(campaign_id=cam_id, id=resp_id)[0]
		try:
			images = Image.objects.filter(campaign_id = cam_id)
		except Exception as e:
			print(e)

		if request.method == "POST" and user.is_response:

			image_obj = None
			delay = 0
			message = request.POST.get("message")
			sequence = request.POST.get("sequence")
			logic = request.POST.get("logic")

			delay_days = request.POST.get('delay_days')
			if not delay_days:
				delay_days = 0
	
			delay_hours = request.POST.get('delay_hours')
			if not delay_hours:
				delay_hours = 0

			delay_mins = request.POST.get('delay_mins')
			if not delay_mins:
				delay_mins = 0

			if logic == "yes":
				is_logic = True
			else:
				is_logic = False

			if request.FILES:
				image = request.FILES['image']
				if image:
					count = Image.objects.count()
					try:
						name = "name{}".format(count+1)
						Image.objects.create(name = name,image=image)
						image_obj = get_object_or_404(Image, name=name)
					except Exception as e:
						print("image", e)
			else:
				image_id = request.POST['image_id']
				if not image_id == "No":
					image_obj = get_object_or_404(Image, id=image_id)

			Sequence.objects.filter(campaign__id=cam_id, id=resp_id)\
				.update(
					sequence = sequence,
					message = message, 
					delay_days = delay_days,
					delay_hours = delay_hours,
					delay_mins = delay_mins,
					is_logic=is_logic, image=image_obj)

			return redirect(reverse('responder:outbound', args=(cam_id,)))
	else:
		if request.method == "POST":
			error = "Permission Denied"

	context = {
		'response': resp_obj,
		"images":images,
		"error":error,
		"alert":alert,
	}

	return render(request, 'responder/campaigns/response-edit.html', context)

def registration_view(request):
	return render(request, 'responder/registration.html')

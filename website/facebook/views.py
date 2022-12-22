import json
import threading

from django.shortcuts import render,redirect, reverse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse, JsonResponse

from .models import FacebookLead, AdForm

from responder.models import InOutSms, AssignContact

from .tasker import *

from responder.serializers import(
		AdFormSerializer
	)
from responder.tasker import get_dnis

from django.utils import timezone
import datetime



def facebook_ads_view(request):

	alert = ""
	all_contacts = 0
	unsubscribed = 0
	total_invalid = 0
	unassigned = 0
	lists = ''
	
	if request.method == "POST" and request.is_ajax():
		data = json.loads(request.body)
		check = data.get('check')

		if check == "delete_form":
			form_id = data.get("form_id")

			AdForm.objects.filter(id=form_id).delete()
			# InOutSms.objects.filter(contact_id=form_id).delete()
			
			json_data = {

			}

			return JsonResponse(data=json_data, status=200)

		elif check == 'get_form':
			form_id = data.get("form_id")
			form = AdForm.objects.get(id=form_id)

			serializer = AdFormSerializer(instance=form)

			json_data = {
				'form': serializer.data
			}

			return JsonResponse(data=json_data, status=200)

	if request.method == "POST" and not request.is_ajax():
		check = request.POST.get('check')

		if check == 'add-contact':
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			phone = request.POST.get('phone')
			email = request.POST.get('email')
			form_id = request.POST.get("form_id")

			phone = get_dnis(phone)
			FacebookLead.objects.create(
					contact_id = form_id,
					full_name = '{} {}'.format(first_name, last_name),
					first_name = first_name,
					last_name = last_name,
					phone = phone,
					email = email,
				)
			return redirect(reverse("facebook:fb_ads"))

		elif check == "create-fb-form":
			form_id = request.POST.get("form_id")
			form_name = request.POST.get("form_name")

			AdForm.objects.create(
				form_id = form_id,
				form_name = form_name
			)
			return redirect(reverse("facebook:fb_ads"))		

		elif check == "update-fb-form":
			f_id = request.POST.get('f_id')
			form_name = request.POST.get("form_name")

			AdForm.objects.filter(id=f_id).update(
				form_name = form_name
			)
			return redirect(reverse("facebook:fb_ads"))

		elif check == 'add-bulk':
			contact_id = request.POST.get('contact_id')
			contacts = request.FILES["bulk-contacts"].readlines()
			
			t = threading.Thread(target=add_bulk, args=(contacts, contact_id,))
			t.start()
			return redirect("facebook:fb_ads")

		elif check == "move-contact":
			form_id = request.POST.get("form_id")
			current_form_id = request.POST.get("current_form_id")
			try:
				to_reply = request.POST.get('to_reply')
				if to_reply == "on":
					to_reply = True
				else:
					to_reply = False
			except:
				pass

			FacebookLead.objects.filter(contact_id=current_form_id).update(

				contact_id = form_id,
				to_reply = to_reply
			)
			alert = "Contacts moved Succesfully!"

	if request.user.is_superuser:

		lists = AdForm.objects.all()
		all_contacts = FacebookLead.objects.count()
		unsubscribed = FacebookLead.objects.filter(is_unsubscribed=True).count()
		unassigned = FacebookLead.objects.filter(contact__form_id=None).count()
		sms_objs = InOutSms.objects.filter(is_incoming=False).exclude(del_status='delivered')

		if sms_objs:
			dnis = list(sms_objs.values('dnis'))
			total_invalid = len({item['dnis'] for item in dnis})
	else:
		assigned = AssignContact.objects.filter(admin__admin=request.user)

		if assigned:
			contact_ids = [item['contact_id'] for item in assigned.values('contact_id')]

			all_contacts = FacebookLead.objects.filter(contact_id__in=contact_ids).count()
			unsubscribed = FacebookLead.objects.filter(contact_id__in=contact_ids,\
			 	is_unsubscribed=True).count()
			unassigned = FacebookLead.objects.filter(contact__form_id=None).count()

			sms_objs = InOutSms.objects.filter(contact_id__in=contact_ids, is_incoming=False).exclude(del_status='delivered')
			if sms_objs:
				dnis = list(sms_objs.values('dnis'))
				total_invalid = len({item['dnis'] for item in dnis})

			fb_forms = AdForm.objects.filter(id__in=contact_ids)

	if request.user.is_superuser:
		try:
			fb_forms = AdForm.objects.all()
		except:
			fb_forms = ""
	else:
		fb_forms = AssignContact.objects.filter(admin__admin=request.user)

	context = {
		'lists':lists,
		'fb_forms':fb_forms,
		'all_contacts': all_contacts,
		'unsubscribed': unsubscribed,
		'unassigned': unassigned,
		'invalid': total_invalid,
		'alert':alert
	}
	return render(request, 'facebook/facebook_reports.html', context)

def lead_edit_view(request, form_id, lead_id):

	if request.method == "POST":
		check = request.POST.get("check")
		if check == "edit_lead":
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			phone = request.POST.get('phone')
			email = request.POST.get('email')
			# print(first_name, last_name, phone, email)

			phone = get_dnis(phone)
			FacebookLead.objects.filter(id=lead_id).update(

				first_name = first_name,
				last_name = last_name,
				full_name = '{} {}'.format(first_name, last_name),
				email = email,
				phone = phone,
			)

			return redirect(reverse("facebook:leads", args=(form_id,)))


	lead = FacebookLead.objects.get(id=lead_id)
	context = {
		"lead":lead
	}
	return render(request, "facebook/facebook_edit.html", context)

def form_details_view(request, form_id):
	
	forms = FacebookLead.objects.filter(contact_id=form_id).order_by("-timestamp")

	if request.is_ajax():
		data = json.loads(request.body)
		check = data.get('check')
		if check == "delete_lead":
			lead_ids = data.get("lead_ids")
			FacebookLead.objects.filter(id__in=lead_ids).delete()
			# InOutSms.objects.filter(contact_id__in=lead_ids).delete()
			json_data = {

			}
			return JsonResponse(data=json_data, status=200)
		elif check == "delete_all_lead":
			FacebookLead.objects.filter(contact_id=form_id).delete()
			# InOutSms.objects.filter(contact_id=form_id).delete()
			json_data = {
				'success': True
			}
			return JsonResponse(data=json_data, status=200)

	if request.method == "POST" and not request.is_ajax():
		check = request.POST.get("check")
		if check == "search-number":
			number = request.POST.get("number")
			forms = FacebookLead.objects.filter(phone__contains=number)

	try:
		page = request.GET.get('page', 1)
		paginator = Paginator(forms, 15)
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
		    pages = paginator.page(1)
		except EmptyPage:
		    pages = paginator.page(paginator.num_pages)

	except:
		forms = ""

	context = {
		'pages':pages
	}

	return render(request, 'facebook/ads_details.html', context)

@csrf_exempt
def facebook_ads_incoming_view(request):
	first_name = ""
	last_name = ""
	full_name = ""
	email = ""
	phone_number = ""
	if request.method == 'POST':
		try:
			# check whether the form already created or not in db
			form_id = request.POST.get('form_id')
			if not AdForm.objects.filter(form_id=form_id).exists():
				AdForm.objects.create(
					form_id = form_id
					)
		except:
			form_id = ""
		try:
			first_name = request.POST.get('first_name')
		except:
			pass		
		try:
			last_name = request.POST.get('last_name')
		except:
			pass		
		try:
			email = request.POST.get('email')
		except:
			pass		
		try:
			phone_number = request.POST.get('phone_number')
			phone_number = get_dnis(phone_number)
		except:
			pass

		if not FacebookLead.objects.filter(contact__form_id = form_id, phone=phone_number).exists():
			form_obj = get_object_or_404(AdForm, form_id=form_id)
			FacebookLead.objects.create(

					contact = form_obj,
					first_name = first_name,
					last_name = last_name,
					full_name = '{} {}'.format(first_name, last_name),
					email = email,
					data = str(request.POST),
					phone = phone_number
				)

	return HttpResponse(status=200)
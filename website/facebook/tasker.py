import threading, time

from .models import FacebookLead, AdForm

from responder.models import Error


def add_bulk(contacts, contact_id):

	time.sleep(.5)
	instances = []

	try:
		for item in contacts:
			items = item.decode('utf-8').split(",")
			first_name = items[0]
			last_name = items[1]
			email = items[2]
			phone = items[3]
			if phone[:3:].isnumeric() and len(phone)<19:
				obj = FacebookLead(

						contact_id = contact_id,
						first_name = first_name,
						last_name = last_name,
						full_name = '{} {}'.format(first_name, last_name),
						email = email,
						phone = phone,
					)
				instances.append(obj)
			else:
				continue

		FacebookLead.objects.bulk_create(instances, batch_size=len(instances))

		form_obj = AdForm.objects.filter(id=contact_id)

		if form_obj:
			print("yess")
			last_bulk = form_obj[0].bulk_tried
			if not last_bulk:
				last_bulk = 0

			bulk_accepted = form_obj[0].bulk_accepted
			if not bulk_accepted:
				bulk_accepted = 0

			print(last_bulk, bulk_accepted)
			AdForm.objects.filter(id=contact_id).update(
				bulk_tried=len(contacts)+last_bulk, 
				bulk_accepted=len(instances)+bulk_accepted)

	except Exception as e:
		Error.objects.create(error=str(e))


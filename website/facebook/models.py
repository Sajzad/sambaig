from django.db import models

import responder


class AdForm(models.Model):
	form_id = models.CharField(max_length=100, blank=True, null=True)
	form_name = models.CharField(max_length=100, blank=True, null=True)
	bulk_tried = models.IntegerField(null=True, default=0)
	bulk_accepted = models.IntegerField(null=True, default=0)

	@property
	def bulk_failed(self):
		bulk_failed = 0
		if self.bulk_tried:
			bulk_failed = self.bulk_tried - self.bulk_accepted
		return bulk_failed

	@property
	def total_lead(self):
		return FacebookLead.objects.filter(contact_id = self.id).count()

	@property
	def unsubscribed(self):
		return FacebookLead.objects.filter(contact_id = self.id, is_unsubscribed=True).count()

	@property
	def unassigned(self):
		return FacebookLead.objects.filter(contact_id=self.id, contact__form_name='untitled').count()

	@property
	def invalid(self):
		total_invalid = 0
		sms_objs = responder.models.InOutSms.objects.filter(contact_id=self.id, is_lead=True, \
			is_incoming=False).exclude(del_status='delivered')
		if sms_objs:
			dnis = list(sms_objs.values('dnis'))
			total_invalid = len({item['dnis'] for item in dnis})

		return total_invalid

	def __str__(self):
		if self.form_name:
			return self.form_name
		else:
			return self.form_id

class FacebookLead(models.Model):
	contact = models.ForeignKey(AdForm, on_delete=models.CASCADE, null=True, blank=True)
	first_name = models.CharField(max_length=50, blank=True, null=True, default="")
	last_name = models.CharField(max_length=50, blank=True, null=True, default="")
	full_name = models.CharField(max_length=50, blank=True, null=True, default="")
	email = models.EmailField(blank=True, null=True, default="")
	phone = models.CharField(max_length=20, blank=True, null=True, default="")
	data = models.TextField(null=True)
	to_reply = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	is_unsubscribed = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)




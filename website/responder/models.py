import sys
import random
from datetime import datetime
import string
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q
                                

User = get_user_model()

class Gateway(models.Model):
	gateway = models.CharField(max_length=50)
	price = models.FloatField(default=0.0)
	mms_price = models.FloatField(default=0.0)

	def __str__(self):
		return self.gateway

class UserPassword(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	password = models.CharField(max_length=50)

	def __str__(self):
		return self.password

class Admin(models.Model):
	admin = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')
	is_permitted = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_lead = models.BooleanField(default=False)
	is_response = models.BooleanField(default=False)
	is_link = models.BooleanField(default=False)
	is_bulk = models.BooleanField(default=False)
	is_delivered = models.BooleanField(default=False)
	is_undelivered = models.BooleanField(default=False)
	is_ani = models.BooleanField(default=False)
	is_campaign = models.BooleanField(default=False)
	is_export = models.BooleanField(default=False)
	is_subadmin = models.BooleanField(default=False)
	is_dnis = models.BooleanField(default=False)
	is_gateway = models.BooleanField(default=False)
	is_limit = models.BooleanField(default=False)
	is_delete_lead = models.BooleanField(default=False, null=True, blank=True)
	file_attached = models.BooleanField(default=False)
	balance = models.FloatField(default=0.0)
	date_joined = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.admin.username

	@property
	def anis(self):
		return Ani.objects.filter(admin_id=self.id)
			
	@property
	def contacts(self):
		return AssignContact.objects.filter(admin_id=self.id)

class QuickResponseTitle(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True)
	title = models.CharField(max_length=100)

	def __str__(self):
		return self.title
	
	@property
	def responses(self):
		return QuickResponse.objects.filter(title_id=self.id)

class QuickResponse(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
	title = models.ForeignKey(QuickResponseTitle, on_delete=models.CASCADE, null=True)
	response = models.TextField()

	def __str__(self):
		return self.admin.admin.username

class Number(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	number = models.CharField(max_length=12)

	def __str__(self):
		return self.user.username

class Spam(models.Model):
	spam = models.CharField(max_length=20, help_text="spam shouldn't be more than 20 chracters")
	
	def __str__(self):
		return self.spam
		
class Image(models.Model):
	admin  = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)
	name = models.CharField(max_length=50, null=True, blank=True)
	image = models.ImageField(upload_to='gallery/', null=True, blank=True)

	def __str__(self):
		return self.name

class AddGateway(models.Model):
	name = models.CharField(max_length=30, blank=True, null=True)
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
	gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE, null=True, blank=True)
	pineapple_user = models.CharField(max_length=100, null=True, blank=True)
	pineapple_password = models.CharField(max_length=100, null=True, blank=True)
	user = models.CharField(max_length=100, null=True, blank=True)
	password = models.CharField(max_length=100, null=True, blank=True)
	sid = models.CharField(max_length=150, null=True, blank=True)
	token = models.CharField(max_length=150, null=True, blank=True)
	tel_api = models.CharField(max_length=150, null=True, blank=True)
	vonage_api_key = models.CharField(max_length=150, null=True, blank=True)
	vonage_api_secret = models.CharField(max_length=150, null=True, blank=True)
	signal_api_token = models.CharField(max_length=150, null=True, blank=True)
	signal_space_url = models.CharField(max_length=150, null=True, blank=True)
	signal_project_id = models.CharField(max_length=150, null=True, blank=True)
	plivo_id = models.CharField(max_length=150, null=True, blank=True)
	plivo_token = models.CharField(max_length=150, null=True, blank=True)

	def __str__(self):
		return self.gateway.gateway

class Ani(models.Model):
	name = models.CharField(max_length=100, null=True)
	admin = models.ForeignKey(Admin, on_delete=models.SET_NULL,blank=True, null=True, default=None)
	gateway = models.ForeignKey(AddGateway, on_delete=models.SET_NULL, blank=True, null=True)
	ani = models.CharField(max_length=20, blank=True, null=True)

	def __str__(self):
		return self.name
	@property
	def not_responded(self):
		return InOutSms.objects.filter(ani_id=self.id, to_reply=True).count()
	@property
	def assigned_anis(self):
		return AssignedAni.objects.filter(ani_id=self.id)

class BulkSms(models.Model):
	name = models.CharField(max_length=100, null=True)
	ani = models.ForeignKey(Ani, on_delete=models.CASCADE, null=True, blank=True)
	image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
	gif_url = models.CharField(max_length=250, null=True, blank=True)
	message = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

	@property
	def total_sent(self):
		return InOutSms.objects.filter(bulk_sms_id=self.id).count()

	@property
	def total_delivered(self):
		sms_objs = InOutSms.objects.filter(bulk_sms_id=self.id, del_status='delivered')
		if sms_objs:
			return int(100*(sms_objs.count()/self.total_sent))
		return 0

	def __str__(self):
		return self.name

class AssignedAni(models.Model):
	"""
		Assignment of a single ani to multiple user 
	"""
	ani = models.ForeignKey(Ani, on_delete=models.CASCADE)
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE,blank=True, null=True)

	def __str__(self):
		return self.ani.name

class Autoresponse(models.Model):
	name = models.CharField(max_length=100, null=True)
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True)
	ani = models.ForeignKey(Ani, on_delete=models.CASCADE, null=True, blank=True)
	response = models.TextField()
	image = models.ForeignKey(Image, on_delete=models.SET_NULL ,blank=True, null=True)
	gif_url = models.CharField(max_length=250, null=True)
	delay_days = models.IntegerField(default=0)
	delay_mins = models.IntegerField(default=0)
	delay_hours = models.IntegerField(default=0)
	is_sat = models.BooleanField(default=False)
	is_sun = models.BooleanField(default=False)
	is_mon = models.BooleanField(default=False)
	is_tue = models.BooleanField(default=False)
	is_wed = models.BooleanField(default=False)
	is_thu = models.BooleanField(default=False)
	is_fri = models.BooleanField(default=False)
	everyday = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	first_time = models.TimeField(null=True)
	last_time = models.TimeField(null=True)

	def __str__(self):
		return str(self.name)

	@property
	def total_sent(self):
		return InOutSms.objects.filter(autoresponse_id = self.id).count()

	@property
	def total_delivered(self):
		if self.total_sent>0:
			delivered = InOutSms.objects.filter(autoresponse_id = self.id, del_status="delivered").count()
			total_delivered = int(100*delivered/self.total_sent)
			if total_delivered<1:
				total_delivered = 0
		else:
			total_delivered = 0
		return total_delivered

class PrimaryNumber(models.Model):
	"""Only hold of a single number which represents current primary number"""
	ani = models.OneToOneField(Ani, on_delete=models.CASCADE)

	def __str__(self):
		return self.ani.ani

class AssignContact(models.Model):
	"""
		Asignment of a single list ot multiple user
	"""
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.admin

choices = (
	('fax','fax'),
	('sms','sms')
)

class InOutSms(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE,blank=True, null=True, default=None)
	autoresponse = models.ForeignKey(Autoresponse, on_delete=models.SET_NULL, null=True, blank=True)
	bulk_sms = models.ForeignKey(BulkSms, on_delete=models.SET_NULL, null=True, blank=True)
	gateway = models.ForeignKey(Gateway, on_delete=models.SET_NULL, blank=True, null=True, default=None)
	image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True, default=None)
	ani = models.ForeignKey(Ani, on_delete=models.CASCADE, blank=True, null=True)
	type = models.CharField(max_length=15, choices=choices, default='sms')
	dnis = models.CharField(max_length=20, null=True, blank=True)
	gif_url = models.CharField(max_length=500, null=True, blank=True)
	sent = models.TextField( null=True, blank=True) 
	reply = models.TextField( null=True, blank=True)
	note = models.TextField( null=True, blank=True)
	dlr = models.TextField( null=True, blank=True)
	message_id = models.CharField(max_length=150, blank=True, default=None, null=True)
	del_status = models.CharField(max_length=12, default=None, null=True)
	error = models.CharField(max_length=200, default=None, null=True)
	dlr_details = models.TextField(blank=True, null=True)
	code = models.CharField(max_length = 5, default=None, null=True)
	order = models.IntegerField(default=1)
	undel_count = models.IntegerField(default=0)
	alter_link_count = models.IntegerField(default=0)
	is_scheduled = models.BooleanField(default=False)
	is_mms = models.BooleanField(default=False)
	is_manual = models.BooleanField(default=False)
	is_seen= models.BooleanField(default=False)
	is_lead = models.BooleanField(default=False)
	to_reply = models.BooleanField(default=False)
	is_wait = models.BooleanField(default=False)
	is_bulk = models.BooleanField(default=False)
	is_incoming = models.BooleanField(default=False)
	has_incoming = models.BooleanField(default=False)
	check_keyword = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	reply_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	scheduled_at = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.dnis

	@property
	def is_liked(self):
		if self.note:
			return Like.objects.filter(sms_id=self.id, admin_id=self.admin_id).exists()
		else:
			return False

	@property
	def total_like(self):
		if self.note:
			return Like.objects.filter(sms_id=self.id).count()
		else:
			return 0

	@property
	def is_replied(self):
		is_replied = True
		sms_objs = InOutSms.objects.filter(
			ani_id = self.ani_id,
			dnis__contains=self.dnis.replace("+", ""), 
			to_reply=True)
		if sms_objs.exists():
			is_replied = False 
			# to help sorting wait list
			# InOutSms.objects.filter(
			# 	ani_id=self.ani_id, 
			# 	dnis__contains=self.dnis.replace("+", ""),
			# 	is_lead=True).update(is_wait=True)
		
		return is_replied

	@property
	def admin_name(self):
		if self.admin:
			return self.admin.admin.username
		else:
			return None

	@property
	def latest_timestamp(self):
		if self.is_lead:
			return InOutSms.objects.filter(dnis__contains=self.dnis.replace("+",""))\
				.order_by('-id')[0].timestamp
		else:
			return None

	@property
	def latest_sms(self):
		sms_objs = InOutSms.objects.filter(
			ani_id = self.ani_id,
			dnis__contains = self.dnis.replace('+',''))
		
		if sms_objs:
			obj = sms_objs.order_by('-id')[0]
			if obj.is_incoming:
				latest_sms = obj.reply
			else:
				latest_sms = obj.sent
				if not latest_sms:
					latest_sms = obj.note
		else:
			latest_sms = None

		return latest_sms

	def save(self, *args, **kwargs):
		# if not self.is_incoming and not self.note:
		# 	InOutSms.objects.filter(dnis__contains=self.dnis, is_seen=False).update(is_seen=True)

		if self.is_incoming:
			objs = InOutSms.objects.filter(ani_id=self.ani_id,dnis__contains=self.dnis.\
				replace("+",""), is_lead=True)
			if objs:
				print("yes incoming")
				try:
					objs.update(is_wait=True,reply_at= datetime.now())
				except Exception as e:
					print(e)
		if not self.is_incoming and not self.note:
			InOutSms.objects.filter(ani_id=self.ani_id, dnis__contains=self.dnis.\
				replace("+","")).update(is_wait=False)
			
			objs = InOutSms.objects.filter(ani_id=self.ani_id, dnis__contains=self.dnis.\
				replace("+",""), to_reply=True)
			if objs:
				objs.update(to_reply=False, reply_at= datetime.now())

		super(InOutSms, self).save(*args, **kwargs)

class Like(models.Model):
	sms = models.ForeignKey(InOutSms,on_delete=models.CASCADE, null=True)
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

	def __str__(self):
		return self.admin.admin.username


class Dlr(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE,blank=True, null=True)
	ani = models.CharField(max_length=20, null=True, blank=True)
	dnis = models.CharField(max_length=20, null=True, blank=True)
	result_code = models.CharField(max_length=50, null=True, blank=True)
	message = models.TextField(null=True, blank=True)
	msg_id = models.CharField(max_length=100, null=True, blank=True)
	status = models.CharField(max_length=15, default="unknown")


	def __str__(self):
		return self.ani

class LogicResponse(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE,blank=True, null=True)
	ani = models.ForeignKey(Ani, on_delete=models.CASCADE, blank=True, null=True)
	image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
	keywords = models.TextField()
	reply = models.TextField()
	gif_url = models.CharField(max_length=250, null=True, blank=True)

	def __str__(self):
		return self.reply

class Test(models.Model):
	ani = models.CharField(max_length=20, null=True, blank=True, default="")
	dnis = models.CharField(max_length=20, null=True, blank=True)
	reply = models.TextField( null=True, blank=True)
	message_id = models.CharField(max_length=150, blank=True, null=True)

	def __str__(self):
		return self.dnis

class CronJob(models.Model):
	is_sequence = models.BooleanField(default=False)
	is_bulk = models.BooleanField(default=False)

class NumberUpload(models.Model):
	admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
	schedule = models.DateTimeField(null=True, blank=True)
	thread = models.IntegerField()
	message = models.TextField(null=True)
	image = models.ImageField(upload_to='mms/', blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	is_sent = models.BooleanField(default=False)

	def __str__(self):
		return self.contact.form_name

class DefaultMessage(models.Model):
	models.ForeignKey(Admin, on_delete=models.CASCADE ,null=True, blank=True)
	message = models.TextField(null=True, blank=True)
	image = models.ImageField(null=True, upload_to='default')

	def __str__(self):
		return self.message

class Css(models.Model):
	is_cam_grey = models.BooleanField(default=True)
	is_back_img = models.BooleanField(default=True)

	# def __str__(self):
	# 	return self.cam_color
class Error(models.Model):
	error = models.TextField()
	view = models.CharField(max_length=100, null=True, blank=True)
	reason = models.CharField(max_length=250, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.error


class Day(models.Model):
	day = models.CharField(max_length=15)
	
	def __str__(self):
		return self.day


class Weekend(models.Model):
	day = models.ForeignKey(Day, on_delete=models.CASCADE)

	def __str__(self):
		return self.day

class worker(models.Model):
	scheduled_sms = models.BooleanField(default=False)
	new_leads = models.BooleanField(default=False)
	check_keyword = models.BooleanField(default=False)
	is_bulk = models.BooleanField(default=False)

	def __str__(self):
		return str(self.scheduled_sms)
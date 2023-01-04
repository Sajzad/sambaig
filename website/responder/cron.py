'''
Django do only communicate with db in views and models or the function been called in views
or models.
'''
import requests
from django.contrib.sites.models import Site


site = Site.objects.all()[0].domain
try:
	cron = site + "/campaigns/cronjob/"
	print(cron)
except Exception as e:
	print(e)
	pass
try:
	bulk_sms_url = site + "/campaigns/cron/bulk"
except:
	pass

def my_scheduled_job():
	requests.get(cron)

def send_bulk():
	requests.get(bulk_sms_url)

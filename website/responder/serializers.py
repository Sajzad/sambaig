from rest_framework import serializers
from .models import(
	InOutSms,
	Autoresponse,
	QuickResponse,
	BulkSms,
	QuickResponseTitle
)


class InOutSmsSerializer(serializers.ModelSerializer):
	latest_sms = serializers.CharField()
	name = serializers.CharField()
	admin_name = serializers.CharField()
	latest_timestamp = serializers.DateTimeField()
	is_replied = serializers.BooleanField()
	is_liked = serializers.BooleanField()
	total_like = serializers.IntegerField()
	class Meta:
		model = InOutSms
		fields = ('dnis','ani', 'id', 'error', 'image','sent', 'reply', 'note', 'latest_sms', 'name', \
			'admin_name', 'timestamp', 'is_scheduled', 'scheduled_at', 'del_status', 'latest_timestamp',\
			'is_seen', 'is_replied','gif_url','is_incoming','is_manual', 'is_liked', 'total_like',\
			'is_bulk')
		depth = 1

class AutoresponseSerializer(serializers.ModelSerializer):
	total_sent = serializers.IntegerField()
	total_delivered = serializers.IntegerField()
	class Meta:
		model = Autoresponse
		fields = '__all__'
		extra_fields = ['total_sent', 'total_delivered']
		depth = 1

class BulkSmsSerializer(serializers.ModelSerializer):
	total_sent = serializers.IntegerField()
	total_delivered = serializers.IntegerField()
	class Meta:
		model = BulkSms
		fields = '__all__'
		extra_fields = ['total_sent', 'total_delivered']
		depth = 1

class QuickResponseSerializer(serializers.ModelSerializer):
	class Meta:
		model = QuickResponse
		depth = 1
		fields = '__all__'

class QuickResponseTitleSerializer(serializers.ModelSerializer):
	responses = QuickResponseSerializer(many=True, read_only=True)
	class Meta:
		model = QuickResponseTitle
		fields = '__all__'
		extra_fields = ['responses']
		# depth = 1

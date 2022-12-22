import requests

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        fax_sid = "ab9365e1-c06e-4b0e-8b51-4073da00d5e4"
        space_url = "bfaxes.signalwire.com"
        account_id = '2956f6a5-dad2-4968-a289-d14fa955e144'
        token = 'PT8f8726503c0965b7c4d315b32f8d6b0c66e3a01b03a6f1e0'

        from signalwire.rest import Client as signalwire_client

        client = signalwire_client(account_id, token, signalwire_space_url = space_url)

        fax = client.fax.faxes('0c667383-d286-4f05-8767-3c637363513c').fetch()
        print(fax.media_url)
        # faxes = client.fax.faxes.list()

        # for fax in faxes:
        #     print(fax.media_url)
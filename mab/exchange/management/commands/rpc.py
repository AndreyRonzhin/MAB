
from django.core.management.base import BaseCommand

from calculation_of_services.models import AccrualService

from django.conf import settings

from  exchange import rpc_server

class Command(BaseCommand):
    help = ''
    s = settings
    rpc_server.start()


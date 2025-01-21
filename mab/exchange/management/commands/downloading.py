from os import sep

from django.core.management.base import BaseCommand
from django.conf import settings

import json
import exchange.service as service
from background_information.models import UtilityService, UnitsOfMeasures, PrivatePerson
from building.models import ApartmentBlock, Entrance, Flat, MeterDevice
from calculation_of_services.models import PersonalAccount, AccrualService, InstrumentReading


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        path_json = self.get_path(options['path'])

        with open(path_json, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)

        update = options.get('update', False)

        ed = None

        if options['type'] == 'UtilityService':
            ed = service.UtilityServiceED(keys=('fullname',),
                                          data=data,
                                          model=UtilityService,
                                          update=update)

        if options['type'] == 'UnitsOfMeasures':
            ed = service.UnitsOfMeasuresED(keys=('code', 'name'),
                                           data=data,
                                           model=UnitsOfMeasures,
                                           update=update)

        if options['type'] == 'PrivatePerson':
            ed = service.PrivatePersonED(keys=('firstname', 'lastname', 'middlename'),
                                         data=data,
                                         model=PrivatePerson,
                                         update=update)

        if options['type'] == 'ApartmentBlock':
            ed = service.ApartmentBlockED(keys=('number', 'region', 'city', 'street'),
                                          data=data,
                                          model=ApartmentBlock,
                                          update=update)

        if options['type'] == 'Entrance':
            ed = service.EntranceED(keys=('number', 'apartment_block'),
                                    data=data,
                                    model=Entrance,
                                    update=update)

        if options['type'] == 'Flat':
            ed = service.FlatED(keys=('number', 'entrance'),
                                data=data,
                                model=Flat,
                                update=update)

        if options['type'] == 'PersonalAccount':
            ed = service.PersonalAccountED(keys=('id_gis', 'flat',),
                                           data=data,
                                           model=PersonalAccount,
                                           update=update)

        if options['type'] == 'AccrualServices':
            ed = service.AccrualServicesED(keys=('date', 'personal_account',),
                                             data=data,
                                             model=AccrualService,
                                             update=update)

        if options['type'] == 'MeterDevice':
            ed = service.MeterDeviceED(keys=('factory_number',),
                                       data=data,
                                       model=MeterDevice,
                                       update=update)

        if options['type'] == 'InstrumentReading':
            ed = service.InstrumentReadingED(keys=('date', 'flat', 'meter_device'),
                                       data=data,
                                       model=InstrumentReading,
                                       update=update)

        if ed:
            ed.create()

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--path',
            dest='path',
            required=True,
            help=''
        )
        parser.add_argument(
            '-t',
            '--type',
            dest='type',
            required=True,
            help=''
        )
        parser.add_argument(
            '-u',
            '--update',
            action='store_true',
            default=False,
            help=''
        )

    @staticmethod
    def get_path(name_file):
        return f"{settings.EXCHANGE_DIR}{sep}{name_file}"

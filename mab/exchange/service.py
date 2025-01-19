from django.db.models import Model
from datetime import datetime
import re
from .exchange_data import ExchangeData, ExchangeDataFieldsForeignKey, ProcessingField


class UnitsOfMeasuresED(ExchangeData):
    pass


class PrivatePersonED(ExchangeData):
    pass


class UtilityServiceED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields_json_model = {'name': 'fullname',
                                  'method_calculating': 'quantify',
                                  'type_communal_resources': 'type_device',
                                  'additionally': 'additionally'}

        unit_of_measure = ExchangeDataFieldsForeignKey('unit_of_measure',
                                                       {'unit_code': 'code', 'unit_name': 'name'},
                                                       self.model)
        self.fields_foreign_key = {'unit_of_measure': unit_of_measure}


class ApartmentBlockED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_exclude.append('name')


class EntranceED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'number': 'number'}

        keys_json_model = {'apartment_block_number': 'number',
                           'apartment_block_region': 'region',
                           'apartment_block_city': 'city',
                           'apartment_block_street': 'street'}

        apartment_block = ExchangeDataFieldsForeignKey('apartment_block', keys_json_model, self.model)
        self.fields_foreign_key = {'apartment_block': apartment_block}


class FlatED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields_json_model = {'number': 'number',
                                  'area_of_apartments': 'area_of_apartments'}

        entrance = EntranceFieldsForeignKey('entrance',
                                            {'entrance_number': 'number'},
                                            self.model)

        keys_json_model = {'owner_firstname': 'firstname',
                           'owner_lastname': 'lastname',
                           'owner_middlename': 'middlename'}

        owner = ExchangeDataFieldsForeignKey('owner', keys_json_model, self.model)
        self.fields_foreign_key = {'owner': owner, 'entrance': entrance}


class FlatFieldsForeignKey(ExchangeDataFieldsForeignKey):

    def find_by_keys(self, data) -> [Model, None]:
        entrance_foreign_key = EntranceFieldsForeignKey('entrance',
                                                        {'entrance_number': 'number'},
                                                        self.model)

        entrance = entrance_foreign_key.find_by_keys(data)

        value_filter = {'entrance': entrance}
        value_filter |= {v: data[k] for k, v in self.keys.items()}

        return self.find_obj_model(value_filter)


class EntranceFieldsForeignKey(ExchangeDataFieldsForeignKey):

    def find_by_keys(self, data) -> [Model, None]:
        apartment_block_foreign_key = ExchangeDataFieldsForeignKey('apartment_block',
                                                                   {'apartment_block_number': 'number',
                                                                    'apartment_block_region': 'region',
                                                                    'apartment_block_city': 'city',
                                                                    'apartment_block_street': 'street'},
                                                                   self.model)

        apartment_block = apartment_block_foreign_key.find_by_keys(data)

        value_filter = {'apartment_block': apartment_block}
        value_filter |= {v: data[k] for k, v in self.keys.items()}

        return self.find_obj_model(value_filter)


class PersonalAccountFieldsForeignKey(ExchangeDataFieldsForeignKey):

    def find_by_keys(self, data) -> [Model, None]:
        flat_foreign_key = FlatFieldsForeignKey('flat',
                                                {'flat_number': 'number'},
                                                self.model)

        flat = flat_foreign_key.find_by_keys(data)

        value_filter = {'flat': flat}
        value_filter |= {v: data[k] for k, v in self.keys.items()}

        return self.find_obj_model(value_filter)

class MeterDeviceFieldsForeignKey(ExchangeDataFieldsForeignKey):

    def find_by_keys(self, data) -> [Model, None]:
        flat_foreign_key = FlatFieldsForeignKey('flat',
                                                {'flat_number': 'number'},
                                                self.model)

        flat = flat_foreign_key.find_by_keys(data)

        factory_number = FactoryNumber(['meter_device_factory_number', 'meter_device_code'])
        number = factory_number.do_processing(data)

        value_filter = {'flat': flat, 'factory_number': number}

        return self.find_obj_model(value_filter)

class PersonalAccountED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'number': 'number',
                                  'closing_date': 'closing_date',
                                  'is_active': 'is_active',
                                  'personal_account_id_gis': 'id_gis',
                                  'quantify': 'quantify'}

        flat = FlatFieldsForeignKey('flat',
                                    {'flat_number': 'number'},
                                    self.model)

        payer = ExchangeDataFieldsForeignKey('payer',
                                             {'payer_firstname': 'firstname',
                                              'payer_lastname': 'lastname',
                                              'payer_middlename': 'middlename'},
                                             self.model)

        self.fields_foreign_key = {'flat': flat, 'payer': payer}


class DateStartMonth(ProcessingField):
    FORMATE_DATE = ((r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', '%Y-%m-%dT%H:%M:%SZ'),
                    (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '%Y-%m-%dT%H:%M:%S'),)

    def do_processing(self, data):

        for format_date in self.FORMATE_DATE:
            if re.fullmatch(format_date[0], data['date']):
                convert_date = datetime.strptime(data['date'], format_date[1])
                year = convert_date.year
                month = convert_date.month
                return datetime(year, month, 1)


class AccrualServicesED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'date': 'date',
                                  'area_of_apartments': 'area_of_apartments',
                                  'total': 'total',
                                  'total_renewal': 'total_renewal'}

        company = ExchangeDataFieldsForeignKey('company',
                                               {'company_inn': 'inn'},
                                               self.model)
        apartment_block = ExchangeDataFieldsForeignKey('apartment_block',
                                                       {'apartment_block_number': 'number'},
                                                       self.model)
        entrance = EntranceFieldsForeignKey('entrance',
                                            {'entrance_number': 'number'},
                                            self.model)
        flat = FlatFieldsForeignKey('flat',
                                    {'flat_number': 'number'},
                                    self.model)
        personal_account = PersonalAccountFieldsForeignKey('personal_account',
                                                           {'personal_account_id_gis': 'id_gis'},
                                                           self.model)

        personal_account_renewal = PersonalAccountFieldsForeignKey('personal_account_renewal',
                                                           {'personal_account_renewal_id_gis': 'id_gis'},
                                                           self.model)

        self.fields_foreign_key = {'company': company,
                                   'apartment_block': apartment_block,
                                   'entrance': entrance,
                                   'flat': flat,
                                   'personal_account': personal_account,
                                   'personal_account_renewal': personal_account_renewal,}

        date_start_month = DateStartMonth()
        self.fields_processing ={'date': date_start_month}


class FactoryNumber(ProcessingField):

    def __init__(self, list_fields):
        if list_fields:
            self.list_fields = list_fields
        else:
            self.list_fields = []

    def do_processing(self, data):
        for field in self.list_fields:
            if data[field]:
                return data[field]

        return None


class IsInstalledMeterDevice(ProcessingField):

    def do_processing(self, data):
        return bool(re.match(r'0001-01-01', data['decommissioning_date']))


class TypeDevice(ProcessingField):

    def do_processing(self, data):

        if data['communal_resources'] == 'Холодная вода':
            return 1

        if data['communal_resources'] == 'Горячая вода':
            return 2

        if data['communal_resources'] == 'Электрическая энергия':
            return 3


class MeterDeviceED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'brand': 'brand',
                                  'type': "type",
                                  'verification_interval': 'verification_interval',
                                  'electricity': 'electricity',
                                  'number_of_tariffs': 'number_of_tariffs',
                                  'remote_reading': 'remote_reading',
                                  'date_of_sealing': 'date_of_sealing',
                                  'installation_date': 'installation_date',
                                  'commissioning_date': 'commissioning_date',
                                  'decommissioning_date': 'decommissioning_date'}

        flat = FlatFieldsForeignKey('flat',
                                    {'flat_number': 'number'},
                                    self.model)

        self.fields_foreign_key = {'flat': flat}

        factory_number = FactoryNumber(['factory_number', 'code'])
        is_installed = IsInstalledMeterDevice()
        type_device = TypeDevice()

        self.fields_processing = {'factory_number': factory_number,
                                  'is_installed': is_installed,
                                  'type_device': type_device}

class InstrumentReadingED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'date': 'date',
                                  'value_t1': "value"}

        flat = FlatFieldsForeignKey('flat',
                                    {'flat_number': 'number'},
                                    self.model)

        meter_device = MeterDeviceFieldsForeignKey('meter_device',
                                                   {},
                                                   self.model)

        self.fields_foreign_key = {'flat': flat, 'meter_device': meter_device}

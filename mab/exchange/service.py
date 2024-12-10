from django.db.models import Model
import re
from .exchange_data import ExchangeData, ExchangeDataFieldsForeignKey


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


class UnitsOfMeasuresED(ExchangeData):
    pass


class ApartmentBlockED(ExchangeData):
    pass


class EntranceED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_exclude.append('name')
        self.field_upper_model = 'apartment_block'

        model_flat = kwargs.get('inner_models').get('flat')
        flat_ed = FlatED(keys=('number',),
                         model=model_flat,
                         update=self.update, )

        self.fields_inner = {'flat': flat_ed}


class FlatED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        keys_json_model = {'owner_firstname': 'firstname',
                           'owner_lastname': 'lastname',
                           'owner_middlename': 'middlename'}

        owner = ExchangeDataFieldsForeignKey('owner', keys_json_model, self.model)
        self.fields_foreign_key = {'owner': owner}


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
                                                                   {'apartment_block_number': 'number'},
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


class AccrualOfServicesED(ExchangeData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_json_model = {'date': 'date',
                                  'area_of_apartments': 'area_of_apartments'}

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
        self.fields_foreign_key = {'company': company,
                                   'apartment_block': apartment_block,
                                   'entrance': entrance,
                                   'flat': flat,
                                   'personal_account': personal_account}


class ProcessingField:

    def do_processing(self, data):
        pass


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

        factory_number = FactoryNumber(['code', 'factory_number'])
        is_installed = IsInstalledMeterDevice()
        type_device = TypeDevice()

        self.fields_processing = {'factory_number': factory_number,
                                  'is_installed': is_installed,
                                  'type_device': type_device}

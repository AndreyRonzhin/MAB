from django.db.models import Model, DateField, Field
from datetime import datetime
import re


class ExchangeData:
    FORMATE_DATE = ((r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', '%Y-%m-%dT%H:%M:%SZ'),
                    (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '%Y-%m-%dT%H:%M:%S'),)

    EMPTY_DATE = datetime(1, 1, 1, 0, 0, 0)

    def __init__(self, **kwargs):
        self.keys = kwargs.get('keys', None)
        self.data_to_download = kwargs.get('data', None)
        self.model = kwargs.get('model', None)
        self.update = kwargs.get('update', False)
        self.fields_json_model = {}
        self.fields_foreign_key = {}
        self.fields_default = {}
        self.fields_processing = {}
        self.fields_exclude = []

    def create(self):
        serialize = SerializerJSON(self.data_to_download, self)
        serialize.serialize()

        for data in serialize:
            pass
            if not self.update and data.object:
                continue
            elif self.update and data.object:
                model = data.object

                for field, value in data.model.items():
                    setattr(model, field, value)

                model.save()
            else:
                model = self.model(**data.model)
                model.save()

    def get_data(self, data: dict) -> dict:
        result = {}

        result |= self.get_values_from_json(data)
        result |= self.get_processing_values(data)
        result |= self.get_default_values()
        result |= {k: v.find_by_keys(data) for k, v in self.fields_foreign_key.items()}

        self.convert_to_datetime(result)

        return result

    def get_values_from_json(self, data_json: dict) -> dict:

        if self.fields_json_model:
            result = {v: data_json[k] for k, v in self.fields_json_model.items()}
        else:
            result = {k: v for k, v in data_json.items() if k not in self.fields_exclude}

        return result

    def get_default_values(self) -> dict:
        return {k: v for k, v in self.fields_default.items()}

    def get_processing_values(self, data) -> dict:
        return {k: v.do_processing(data) for k, v in self.fields_processing.items()}

    def convert_to_datetime(self, model_value: dict):
        for field, value in model_value.items():
            model_field = getattr(self.model, field, None)

            if not isinstance(model_field.field, DateField):
                continue

            for format_date in self.FORMATE_DATE:
                if re.fullmatch(format_date[0], value):
                    convert_date = datetime.strptime(value, format_date[1])
                    model_value[field] = None if convert_date == self.EMPTY_DATE else convert_date

    # def get_field_model(self, name):
    #     result = self.fields_json_model.get(name, None)
    #
    #     if not result:
    #         raise ValueError(f'The value {name} was not found in attribute fields_json_model')
    #
    #     return result


class ExchangeDataFieldsForeignKey:
    __cache_value = {}

    def __init__(self, name: str, keys: [tuple, dict], model: Model):
        self.name = name
        self.model = self.__get_model_by_field(name, model)
        self.keys = keys

    @staticmethod
    def __get_model_by_field(name: str, model: Model) -> Model:
        model_field = getattr(model, name, None)

        if model_field is None:
            raise AttributeError(f'The name {name} of the foreign key field is incorrect')

        return model_field.field.related_model

    def find_by_keys(self, data) -> [Model, None]:
        if isinstance(self.keys, dict):
            value_filter = {v: data[k] for k, v in self.keys.items()}
        else:
            value_filter = {k: data[k] for k in self.keys}

        return self.find_obj_model(value_filter)

    def find_obj_model(self, value_filter):
        cache_value = self.get_cache_value(self.name, tuple(value_filter.values()))

        if cache_value:
            return cache_value

        queryset = self.model.objects.filter(**value_filter)[:1]

        obj_model = queryset.get() if queryset else None

        self.add_cache_value(self.name, tuple(value_filter.values()), obj_model)

        return obj_model

    @classmethod
    def add_cache_value(cls, name, search_values: tuple[str | int], value: Model):
        if value:
            cache_value_name = cls.__cache_value.get(name, None)
            if cache_value_name:
                cache_value_name |= {hash(search_values): value}
            else:
                cls.__cache_value = {name: {hash(search_values): value}}

    @classmethod
    def get_cache_value(cls, name, search_values: tuple[str | int]):
        name_value = cls.__cache_value.get(name, None)

        if name_value:
            hash_value = hash(search_values)
            return name_value.get(hash_value, None)

        return None


class SerializerJSONValue:

    def __init__(self, json: dict, model: dict, object_model: Model):
        self.json = json
        self.model = model
        self.object = object_model
        self.__next = None

    def set_next(self, data):
        self.__next = data

    def get_next(self):
        return self.__next


class SerializerJSON:

    def __init__(self, data: list[dict], exchange_data: ExchangeData):
        self.data_json = data
        self.exchange_data = exchange_data
        self.__head = None
        self.__tail = None
        self.__current = None

    def serialize(self):
        for value_json in self.data_json:
            value_model = self.exchange_data.get_data(value_json)

            value_filter = {k: value_model[k] for k in self.exchange_data.keys}

            queryset = self.exchange_data.model.objects.filter(**value_filter)[:1]

            value_data = SerializerJSONValue(json=value_json,
                                             model=value_model,
                                             object_model=queryset.get() if queryset else None)

            self.add(value_data)

    def add(self, data: SerializerJSONValue):
        if self.__head is None:
            self.__head = data
        else:
            self.__tail.set_next(data)

        self.__tail = data

    def __iter__(self):
        self.__current = self.__head
        return self

    def __next__(self):
        if self.__current:
            current_data = self.__current
            self.__current = self.__current.get_next()
            return current_data
        else:
            raise StopIteration


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


class BuildingsED(ExchangeData):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields_exclude.append('name')
        model_entrance = kwargs.get('inner_models').get('entrance')

        inner_models = {'flat': kwargs.get('inner_models').get('flat')}
        entrance_ed = EntranceED(keys=('number',),
                                 model=model_entrance,
                                 update=self.update,
                                 inner_models=inner_models)

        self.fields_inner = {'entrance': entrance_ed}


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

        self.fields_exclude = ['name', 'owner_firstname', 'owner_lastname', 'owner_middlename']
        self.field_upper_model = 'entrance'

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

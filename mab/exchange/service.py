from django.db.models import Model


class ExchangeData:
    def __init__(self, **kwargs):
        self.keys = kwargs.get('keys', None)
        self.data_to_download = kwargs.get('data', None)
        self.model = kwargs.get('model', None)
        self.update = kwargs.get('update', False)
        self.fields_json_model = {}
        self.fields_foreign_key = {}
        self.fields_default = {}
        self.fields_exclude = []
        self.fields_inner = {}
        self.field_upper_model = ''
        self.upper_model = None

    def create(self):
        serialize = SerializerJSON(self.data_to_download, self)
        serialize.serialize()

        for data in serialize:
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

        fields_exclude = self.fields_exclude.copy()
        fields_exclude.extend(self.fields_inner.keys())

        if self.fields_json_model:
            result |= {v: data[k] for k, v in self.fields_json_model.items()}
        else:
            result |= {k: v for k, v in data.items() if k not in fields_exclude}

        result |= {k: v for k, v in self.fields_default.items()}
        result |= {k: v.find_by_keys(data) for k, v in self.fields_foreign_key.items()}

        if self.upper_model and self.field_upper_model:
            result[self.field_upper_model] = self.upper_model

        return result

    def get_field_model(self, name):
        result = self.fields_json_model.get(name, None)

        if not result:
            raise ValueError(f'The value {name} was not found in attribute fields_json_model')

        return result


class ExchangeDataFieldsForeignKey:

    def __init__(self, name: str, keys: [tuple, dict], model: Model):
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

        queryset = self.model.objects.filter(**value_filter)[:1]

        return queryset.get() if queryset else None


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
            if self.exchange_data.fields_json_model:
                value_filter = {self.exchange_data.get_field_model(k): value_json[k] for k in self.exchange_data.keys}
            else:
                value_filter = {k: value_json[k] for k in self.exchange_data.keys}

            if self.exchange_data.upper_model and self.exchange_data.field_upper_model:
                value_filter[self.exchange_data.field_upper_model] = self.exchange_data.upper_model

            queryset = self.exchange_data.model.objects.filter(**value_filter)[:1]

            value_model = self.exchange_data.get_data(value_json)

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

    def add_inner(self):
        pass

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
                                  'type_communal_resources': 'type_device'}

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
                         update=self.update,)

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




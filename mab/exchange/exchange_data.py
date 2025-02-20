import re
from django.db.models import Model, DateField, Field
from typing import Any
from datetime import datetime


class ExchangeData:
    """

    """
    FORMATE_DATE = ((r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', '%Y-%m-%dT%H:%M:%SZ'),
                    (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '%Y-%m-%dT%H:%M:%S'),)

    EMPTY_DATE = datetime(1, 1, 1, 0, 0, 0)

    def __init__(self,
                 keys: tuple[str, ...],
                 data: list[dict[str, Any]],
                 model: Model,
                 update: bool = False):
        """Create a new instance of ExchangeData

        :param list keys:
        :param list data:
        :param Model model:
        :param bool update:


        """
        self.keys = keys
        self.data_to_download = data
        self.model = model
        self.update = update

        self.fields_json_model: dict[str, str] = {}
        self.fields_foreign_key: dict[str, ExchangeDataFieldForeignKey]= {}
        self.fields_default: dict[str, Any] = {}
        self.fields_processing: dict[str, ProcessingField] = {}
        self.fields_exclude: list[str] = []

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
                model = self.model.objects.create(**data.model)
                model.save()

    def get_data(self, data: dict[str, Any]) -> dict[str, Any]:
        result:dict[str, Any] = {}

        result |= self.get_values_from_json(data)
        result |= self.get_processing_values(data)
        result |= self.get_default_values()
        result |= self.get_fields_foreign_key(data)

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

    def get_fields_foreign_key(self, data):
        return {k: v.find_by_keys(data) for k, v in self.fields_foreign_key.items()}

    def convert_to_datetime(self, model_value: dict):
        for field, value in model_value.items():
            if isinstance(value, datetime):
                continue

            model_field = getattr(self.model, field, None)

            if model_field and not isinstance(model_field.field, DateField):
                continue

            for format_date in self.FORMATE_DATE:
                if re.fullmatch(format_date[0], value):
                    convert_date = datetime.strptime(value, format_date[1])
                    model_value[field] = None if convert_date == self.EMPTY_DATE else convert_date

    def filter(self, value)->Model:
        queryset = self.model.objects.filter(**value)[:1]
        return queryset.get() if queryset else None

    def get_value_filter(self, value)->dict:
        return {k: value[k] for k in self.keys}


class ExchangeDataFieldForeignKey:
    __cache_value = {}

    def __init__(self,
                 name: str,
                 keys: dict[str, str] | tuple[str, ...],
                 model: Model):
        self.name = name
        self.model = self.__get_model_by_field(name, model)
        self.keys = keys

    @staticmethod
    def __get_model_by_field(name: str, model: Model) -> Model:
        model_field = getattr(model, name, None)

        if model_field is None:
            raise AttributeError(f'The name {name} of the foreign key field is incorrect')

        return model_field.field.related_model

    def find_by_keys(self, data: dict[str, Any]) -> Model | None:
        if isinstance(self.keys, dict):
            value_filter = {v: data[k] for k, v in self.keys.items()}
        else:
            value_filter = {k: data[k] for k in self.keys}

        return self.find_obj_model(value_filter)

    def find_obj_model(self, value_filter: dict[str, Any]) -> Model:
        cache_value = self.get_cache_value(self.name, tuple(value_filter.values()))

        if cache_value:
            return cache_value

        queryset = self.model.objects.filter(**value_filter)[:1]

        obj_model = queryset.get() if queryset else None

        self.add_cache_value(self.name, tuple(value_filter.values()), obj_model)

        return obj_model

    @classmethod
    def add_cache_value(cls, name, search_values: tuple[str, ...], value: Model):
        if value:
            cache_value_name = cls.__cache_value.get(name, None)
            if cache_value_name:
                cache_value_name |= {hash(search_values): value}
            else:
                cls.__cache_value = {name: {hash(search_values): value}}

    @classmethod
    def get_cache_value(cls, name, search_values: tuple[str, ...]) ->Model|None:
        name_value = cls.__cache_value.get(name, None)

        if name_value:
            hash_value = hash(search_values)
            return name_value.get(hash_value, None)

        return None

class ProcessingField:

    def do_processing(self, data: dict[str, Any])->Any:
        pass

class SerializerJSONValue:

    def __init__(self, json: dict[str, Any], model: dict[str, Any], object_model: Model):
        self.json = json
        self.model = model
        self.object = object_model
        self.__next: SerializerJSONValue | None = None

    def set_next(self, data):
        self.__next = data

    def get_next(self):
        return self.__next

class SerializerJSON:

    def __init__(self, data: list[dict[str, Any]], exchange_data: ExchangeData):
        self.data_json = data
        self.exchange_data = exchange_data

        self.__head: SerializerJSONValue | None = None
        self.__current: SerializerJSONValue | None = None

    def serialize(self):
        for value_json in self.data_json:

            value_model = self.exchange_data.get_data(value_json)
            value_filter = self.exchange_data.get_value_filter(value_model)
            object_model = self.exchange_data.filter(value_filter)

            value_data = SerializerJSONValue(json=value_json,
                                             model=value_model,
                                             object_model=object_model)

            self.add(value_data)

    def add(self, data: SerializerJSONValue):

        if self.__head and self.__current:
            self.__current.set_next(data)
        else:
            self.__head = data

        self.__current = data


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


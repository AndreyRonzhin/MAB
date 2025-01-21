from __future__ import annotations

from datetime import date
from django.db import transaction
from django.db.models import Max, QuerySet

from background_information.models import UtilityService
from building.models import MeterDevice, Flat
from calculation_of_services.models import InstrumentReading, CompanyApartmentBlock

class DataMeterDevice:

    @staticmethod
    def get_devices(flat: Flat) -> QuerySet:
        return MeterDevice.objects.filter(flat=flat, is_installed=True).order_by('type_device')

class DataInstrumentReading:

    @staticmethod
    def get_last_instrument_readings(devices: list[MeterDevice]) -> QuerySet:

        qs_last_date = (InstrumentReading.objects.filter(meter_device__in=devices).values('meter_device')
                        .annotate(date=Max('date')).values('date'))

        qs_last_values = (InstrumentReading.objects.filter(meter_device__in=devices, date__in=qs_last_date)
                          .values('meter_device', 'date', 'value'))

        return qs_last_values

    @staticmethod
    def save(date_instr_read:date, flat:Flat, devices:OperationInstrumentReading) -> bool:
        try:
            with transaction.atomic():
                for device in devices:
                    instr_read = {'date': date_instr_read,
                                  'flat': flat,
                                  'meter_device': device.model,
                                  'value': device.current_values
                                  }

                    InstrumentReading.objects.create(**instr_read)

        except Exception as ex:
            print(ex)
            return False

        return True

class OperationMeterDevice:

    def __init__(self, model:MeterDevice):
        self.model: MeterDevice = model
        self.pk_device: int = model.pk
        self.date: date | None = None
        self.type_device: int = model.type_device
        self.factory_number: str = model.factory_number
        self.is_installed: bool = model.is_installed
        self.current_values: float = 0
        self.previous_values: float = 0

    @property
    def count(self):
        return self.current_values - self.previous_values

    def __str__(self):
        return f'{UtilityService.TypeOfDevice(self.type_device).label} №{self.factory_number}'


    @staticmethod
    def get_devices(flat: Flat):
        return DataMeterDevice.get_devices(flat)

class OperationInstrumentReading:

    def __init__(self, flat: Flat):
        self.__flat = flat

        self.__date: date | None = None
        self.__devices: dict[int, OperationMeterDevice] = {}
        self.__index_key: int = 0
        self.__list_key: list[int] = []

        self.fill_devices()
        self.fill_values_device()

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index_key < len(self.__list_key):
            device = self.__devices[self.__list_key[self.__index_key]]
            self.__index_key += 1
            return device
        else:
            self.__index_key = 0
            raise StopIteration

    def fill_devices(self):
        devices_qs = DataMeterDevice.get_devices(self.__flat)

        for device_qs in devices_qs:
            self.__devices[device_qs.pk] = OperationMeterDevice(device_qs)
            self.__list_key.append(device_qs.pk)

    def fill_values_device(self):

        for last_values in DataInstrumentReading.get_last_instrument_readings(self.devices):
            device = self.get_device(last_values['meter_device'])
            device.date = last_values['date']
            device.previous_values = float(last_values['value'])

    @property
    def devices(self) -> list[MeterDevice]:
        return [v.model for v in self.__devices.values()]

    @property
    def date(self) -> date | None:
        return self.__date

    @date.setter
    def date(self, date_instr_read: date):
        self.__date = date_instr_read

    @property
    def flat(self) -> Flat:
        return self.__flat

    def get_device(self, device_number: int) -> OperationMeterDevice | None:
        return self.__devices.get(device_number, None)

    def set_current_values(self, device_number: int, value: float):
        device = self.get_device(device_number)
        if device:
            device.current_values = value
        else:
            raise Exception('Прибор учета не найден по ключу')


    def save_readings(self) -> bool:
        if self.__date:
            return DataInstrumentReading.save(self.__date, self.__flat, self)
        else:
            return False


    def valid_instrument_reading(self) -> list:
        result = []

        for device in self.__devices.values():
            if (device.date and self.date) and device.date >= self.date:
                error = (device.pk_device, f'Дата {self.date} меньше даты последних показаний {device.date}')
                result.append(error)
                continue

            if device.current_values < device.previous_values:
                error = (device.pk_device, f'Введённое показание {device.current_values} '
                                           f'меньше предыдущего {device.previous_values}')
                result.append(error)

        return result

class DataCompanyApartmentBlock:

    @staticmethod
    def get_active_apartment_block(company_id: int) -> QuerySet:
        return (CompanyApartmentBlock.objects.filter(company=company_id, is_active=True)
                .values('apartment_block').annotate(date=Max('date')))

    @staticmethod
    def get_not_active_apartment_block(company_id: int) -> QuerySet:
        return (CompanyApartmentBlock.objects.filter(company=company_id, is_active=False)
                .values('apartment_block').annotate(date=Max('date')))


class OperationCompanyApartmentBlock:

    def __init__(self, company_id: int):
        self.__active_apartment_block: dict[int, date] = {}
        self.__company_id = company_id

    def list_apartment_block(self) -> dict[int, date]:
        qs_active_apartment_block = DataCompanyApartmentBlock.get_active_apartment_block(self.__company_id)

        for active_apartment in qs_active_apartment_block:
            apartment_block_id = active_apartment['apartment_block']
            self.__active_apartment_block[apartment_block_id] = active_apartment['date']

        qs_not_active_apartment_block = DataCompanyApartmentBlock.get_not_active_apartment_block(self.__company_id)

        for not_active_apartment in qs_not_active_apartment_block:
            date_active_apartment_block = self.__active_apartment_block.get(not_active_apartment['apartment_block'],
                                                                            None)
            if date_active_apartment_block and date_active_apartment_block < not_active_apartment['date']:
                del self.__active_apartment_block[not_active_apartment['apartment_block']]

        return self.__active_apartment_block



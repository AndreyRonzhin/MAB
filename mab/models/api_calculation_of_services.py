
from django.db import transaction
from django.db.models import Max

from building.models import MeterDevice, Flat

from calculation_of_services.models import InstrumentReading
from models.api_building import MeterDeviceAPI

class InstrumentReadingAPI:

    def __init__(self, flat):

        self.__date = None
        self.__flat = flat
        self.__devices = {}

        devices_qs = MeterDevice.objects.filter(flat=flat)

        for device_qs in devices_qs:
            self.__devices[device_qs.pk] = MeterDeviceAPI(device_qs)

        self.fill_values_device()

    @property
    def devices(self) -> list:
        return [v.model_api for v in self.__devices.values()]

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    def get_device(self, device_number: int) -> MeterDevice | None:
        return self.__devices.get(device_number, None)

    def set_current_values(self, device_number: int, value: float):
        device = self.get_device(device_number)
        if device:
            device.current_values = value
        else:
            raise 'Прибор учета не найден по номеру'

    def fill_values_device(self):

        qs_last_date = (InstrumentReading.objects.filter(meter_device__in=self.devices).values('meter_device')
                        .annotate(date=Max('date')))

        list_last_date = [last_date['date'] for last_date in qs_last_date]

        qs_last_values = (InstrumentReading.objects.filter(meter_device__in=self.devices, date__in=list_last_date)
                          .values('meter_device', 'date', 'value'))

        for last_values in qs_last_values:
            device = self.get_device(last_values['meter_device'])
            device.date = last_values['date']
            device.previous_values = last_values['value']

    # def fill_date_values(self):
    #     qs_date =

    def save_readings(self):

        try:
            with transaction.atomic():
                for device in self.__devices.values():

                    instr_read = {'date': self.__date,
                                  'flat': self.__flat,
                                  'meter_device': device.model_api,
                                  'value': device.current_values
                                  }

                    InstrumentReading.objects.create(**instr_read)

        except Exception as ex:
            print(ex)
            return False

        return True

    def valid_instrument_reading(self) -> list:

        result = []

        for device in self.__devices.values():

            if device.date >= self.date:
                error = (device.pk_device, f'Дата {self.date} меньше даты последних показаний {device.date}')
                result.append(error)
                continue

            if device.current_values < device.previous_values:
                error = (device.pk_device, f'Введённое показание {device.current_values} '
                                           f'меньше предыдущего {device.previous_values}')
                result.append(error)

        return result

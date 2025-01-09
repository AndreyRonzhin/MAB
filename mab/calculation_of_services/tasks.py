from .models import StatisticInstrumentReadings
from .service import OperationInstrumentReading
from django.core.cache import cache
from celery import shared_task


@shared_task
def set_statistic_instrument_readings(key:str):

    instr_read = cache.get(key)

    for device in instr_read:
        count = device.count

        create_defaults = {'date': instr_read.date,
                           'flat': instr_read.flat,
                           'meter_device': device.model,
                           'count': count}
        StatisticInstrumentReadings.objects.update_or_create(date=instr_read.date,
                                                             flat=instr_read.flat,
                                                             meter_device=device.model,
                                                             defaults={'count': count},
                                                             create_defaults=create_defaults)

    cache.delete(key)


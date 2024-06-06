from django.db import models

from datetime import datetime

from background_information.models import UtilityService
from building.models import Flat, MeterDevice


class Rate(models.Model):
    date = models.DateField(verbose_name="Начало действия")
    service = models.ForeignKey(UtilityService,
                                on_delete=models.PROTECT,
                                null=False, blank=False,
                                verbose_name="Комунальная услуга")
    rate = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Тариф")

    def __str__(self):
        return f'{self.service}({self.rate}) c {self.date}'

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"


class InstrumentReading(models.Model):
    date = models.DateField(verbose_name="Дата ввода")
    flat = models.ForeignKey(Flat,
                             on_delete=models.PROTECT,
                             null=False,
                             blank=False,
                             verbose_name="Квартира")
    meter_device = models.ForeignKey(MeterDevice,
                                on_delete=models.PROTECT,
                                null=False, blank=False,
                                verbose_name="Прибор учета",
                                unique_for_date="date")
    value = models.DecimalField(max_digits=20, decimal_places=5, verbose_name="Покаания")

    def __str__(self):
        return f"{self.date.strftime('%B')} {self.flat} ({self.meter_device}) c {self.value}"

    class Meta:
        verbose_name = "Показания прибора учета"
        verbose_name_plural = "Показания приборов учета"

class PersonalAccount(models.Model):
    numbers = models.CharField(max_length=25, null=False, blank=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Лицевой счет"
        verbose_name_plural = "Лицевые счета"


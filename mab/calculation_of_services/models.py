from django.db import models

from datetime import datetime

from background_information.models import UtilityService, PrivatePerson
from building.models import Flat, MeterDevice, ApartmentBlock, Entrance

import locale

locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)


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
    objects = None
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
                                     )
    value = models.DecimalField(max_digits=20, decimal_places=5, verbose_name="Показания")

    def __str__(self):
        return f"{self.date.strftime('%B')} {self.flat} ({self.meter_device}) c {self.value}"

    class Meta:
        unique_together = ("date", "flat", "meter_device")
        verbose_name = "Показания прибора учета"
        verbose_name_plural = "Показания приборов учета"


class PersonalAccount(models.Model):
    class TypeOfPersonalAccount(models.IntegerChoices):
        UTILITIES = 0, 'коммунальные услуги'
        MAJOR_RENOVATION = 1, 'капитальный ремонт'


    numbers = models.CharField(max_length=25, null=False, blank=False, db_index=True)
    flat = models.ForeignKey(Flat,
                             on_delete=models.PROTECT,
                             null=False,
                             blank=False,
                             related_name='personal_account',
                             verbose_name="Квартира")

    quantify = models.IntegerField(choices=TypeOfPersonalAccount.choices,
                                   default=TypeOfPersonalAccount.UTILITIES,
                                   verbose_name="Вид лицевого счета")

    payer = models.ForeignKey(PrivatePerson,
                              on_delete=models.PROTECT,
                              null=False,
                              blank=False,
                              related_name='personal_account',
                              verbose_name="Плательщик")

    is_active = models.BooleanField(default=False, verbose_name="Активный")

    closing_date = models.DateField(null=True, blank=True, verbose_name="Дата закрытия")

    list_of_service = models.ForeignKey('ListOfService',
                                        on_delete=models.PROTECT,
                                        null=False,
                                        blank=False,
                                        related_name='personal_account',
                                        verbose_name="Список услуг")

    class Meta:
        verbose_name = "Лицевой счет"
        verbose_name_plural = "Лицевые счета"

    def __str__(self):
        return f'Лицевой счет №{self.numbers}'


class ListOfService(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name


class ServiceActions(models.Model):
    date = models.DateField(verbose_name="Период")
    list_service = models.ForeignKey(ListOfService,
                                     on_delete=models.PROTECT,
                                     null=False,
                                     blank=False,
                                     verbose_name="Список усдуг")
    service = models.ForeignKey(UtilityService,
                                on_delete=models.PROTECT,
                                null=False,
                                blank=False,
                                verbose_name="Комунальная услуга")
    month = models.IntegerField(verbose_name="Месяц")
    ordinal_number = models.IntegerField(verbose_name="Порядковый номер")
    is_active = models.BooleanField(null=True, blank=True, verbose_name="Используется")

    class Meta:
        unique_together = ("date", "list_service", "service", "month")


class AccrualOfServices(models.Model):
    date = models.DateField(verbose_name="Период")
    apartment_block = models.ForeignKey(ApartmentBlock,
                                        related_name='accrual_services',
                                        on_delete=models.PROTECT,
                                        null=True)
    entrance = models.ForeignKey(Entrance, related_name='accrual_services', on_delete=models.PROTECT, null=True)
    flat = models.ForeignKey(Flat, related_name='accrual_services', on_delete=models.PROTECT, null=True, blank=True)
    area_of_apartments = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    list_service = models.ForeignKey(ListOfService,
                                     on_delete=models.PROTECT,
                                     null=True,
                                     blank=True,
                                     verbose_name="Список услуг")

    def __str__(self):
        return f"Начисления услуг за {self.date.strftime('%B')} {self.flat}"

    class Meta:
        verbose_name = "Начисление услуг"
        verbose_name_plural = "Начисление услуг"


class SheetOfServices(models.Model):
    accrual_services = models.ForeignKey(AccrualOfServices,
                                         related_name='sheet_services',
                                         on_delete=models.PROTECT,
                                         null=True)
    service = models.ForeignKey(UtilityService,
                                related_name='sheet_services',
                                on_delete=models.PROTECT,
                                null=False,
                                blank=False,
                                verbose_name="Комунальная услуга")
    meter_device = models.ForeignKey(MeterDevice,
                                     related_name='sheet_services',
                                     on_delete=models.PROTECT,
                                     null=False, blank=False,
                                     verbose_name="Прибор учета")

    rate = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Тариф")

    instrument_reading_current = models.DecimalField(max_digits=20,
                                                     decimal_places=3,
                                                     verbose_name="Текущие показания")
    instrument_reading_previous = models.DecimalField(max_digits=20,
                                                      decimal_places=3,
                                                      verbose_name="Предыдущие показания")
    quantity = models.DecimalField(max_digits=15,
                                   decimal_places=3,
                                   verbose_name="Количество")
    amount = models.DecimalField(max_digits=15,
                                 decimal_places=2,
                                 verbose_name="Сумма")

    class Meta:
        verbose_name = "Таблица начисленных услуг"
        verbose_name_plural = "Таблица начисленных услуг"

from django.db import models

from datetime import datetime

from background_information.models import UtilityService, PrivatePerson
from building.models import Flat, MeterDevice, ApartmentBlock, Entrance

import locale


class Company(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name='Наименование')
    inn = models.CharField(max_length=12, null=True, blank=True, verbose_name='ИНН')

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name


class Rate(models.Model):
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT,
                                null=True, blank=True,
                                verbose_name="Организация",
                                related_name='rate')

    date = models.DateField(verbose_name="Начало действия")
    service = models.ForeignKey(UtilityService,
                                on_delete=models.PROTECT,
                                null=False, blank=False,
                                verbose_name="Комунальная услуга",
                                related_name='rate')
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
                             null=False, blank=False,
                             related_name='instrument_reading',
                             verbose_name="Квартира")
    meter_device = models.ForeignKey(MeterDevice,
                                     on_delete=models.PROTECT,
                                     null=False, blank=False,
                                     related_name='instrument_reading',
                                     verbose_name="Прибор учета")
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

    number = models.CharField(max_length=25,
                              null=True,
                              blank=False,
                              db_index=True,
                              verbose_name='Лицевой счет')

    flat = models.ForeignKey(Flat,
                             on_delete=models.PROTECT,
                             null=True, blank=True,
                             related_name='personal_account',
                             verbose_name="Квартира")

    quantify = models.IntegerField(choices=TypeOfPersonalAccount.choices,
                                   default=TypeOfPersonalAccount.UTILITIES,
                                   verbose_name="Вид лицевого счета")

    payer = models.ForeignKey(PrivatePerson,
                              on_delete=models.PROTECT,
                              null=True,
                              blank=True,
                              related_name='personal_account',
                              verbose_name="Плательщик")

    is_active = models.BooleanField(default=False, verbose_name="Активный")

    closing_date = models.DateField(null=True, blank=True, verbose_name="Дата закрытия")

    id_gis = models.CharField(max_length=13,
                              null=True,
                              blank=True,
                              verbose_name='Идентификатор ЖКУ')

    list_of_service = models.ForeignKey('ListOfService',
                                        on_delete=models.PROTECT,
                                        null=True,
                                        blank=True,
                                        related_name='personal_account',
                                        verbose_name="Список услуг")

    class Meta:
        verbose_name = "Лицевой счет"
        verbose_name_plural = "Лицевые счета"
        ordering = ['number']

    def __str__(self):
        closed = '' if self.is_active else ' закрыт'
        return f'Лицевой счет №{self.number}{closed}'


class ListOfService(models.Model):
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT,
                                null=True, blank=True,
                                verbose_name="Организация",
                                related_name='list_of_service')

    name = models.CharField(max_length=255, null=False, blank=False, verbose_name='Наименование')

    class Meta:
        verbose_name = "Список услуг"
        verbose_name_plural = "Набор списков услуг"

    def __str__(self):
        return self.name


class ServiceAction(models.Model):
    date = models.DateField(verbose_name="Период")
    list_service = models.ForeignKey(ListOfService,
                                     on_delete=models.PROTECT,
                                     null=False,
                                     blank=False,
                                     verbose_name="Список услуг")
    service = models.ForeignKey(UtilityService,
                                on_delete=models.PROTECT,
                                null=False,
                                blank=False,
                                verbose_name="Услуга")
    month = models.IntegerField(verbose_name="Месяц")
    ordinal_number = models.IntegerField(verbose_name="Порядковый номер")
    is_active = models.BooleanField(null=True, blank=True, verbose_name="Используется")

    class Meta:
        verbose_name = "Начисление коммунальных услуг"
        verbose_name_plural = "Начисление коммунальных услуг"
        unique_together = ("date", "list_service", "service", "month")

    def __str__(self):
        return f'{self.list_service} {self.service} {self.date} {self.month} '


class AccrualService(models.Model):
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT,
                                null=True, blank=True,
                                related_name='accrual_of_services',
                                verbose_name="Организация")
    date = models.DateField(verbose_name="Период")
    apartment_block = models.ForeignKey(ApartmentBlock,
                                        related_name='accrual_of_services',
                                        on_delete=models.PROTECT,
                                        null=True,
                                        verbose_name="Дом")
    entrance = models.ForeignKey(Entrance,
                                 related_name='accrual_services',
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True,
                                 verbose_name="Подъезд")
    flat = models.ForeignKey(Flat,
                             related_name='accrual_services',
                             on_delete=models.PROTECT,
                             null=True,
                             blank=True,
                             verbose_name="Квартира")
    personal_account = models.ForeignKey(PersonalAccount,
                                         related_name='accrual_services',
                                         on_delete=models.PROTECT,
                                         null=True,
                                         blank=True,
                                         verbose_name="Лицевой счет")
    personal_account_renewal = models.ForeignKey(PersonalAccount,
                                                       related_name='accrual_services_renewal',
                                                       on_delete=models.PROTECT,
                                                       null=True,
                                                       blank=True,
                                                       verbose_name="Лицевой счет кап. ремонт")
    area_of_apartments = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    total = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    total_renewal = models.DecimalField(max_digits=15, decimal_places=2, null=False)


    def __str__(self):
        return f"Начисления услуг за {self.date.strftime('%B')} {self.flat} {self.personal_account}"

    class Meta:
        verbose_name = "Начисление услуг"
        verbose_name_plural = "Начисление услуг"
        ordering = ['-date', 'personal_account__number']


class SheetService(models.Model):
    accrual_services = models.ForeignKey(AccrualService,
                                         on_delete=models.PROTECT,
                                         null=True,
                                         related_name='sheet_services',
                                         verbose_name="Начисление услуг")
    service = models.ForeignKey(UtilityService,
                                related_name='service',
                                on_delete=models.PROTECT,
                                null=False,
                                blank=False,
                                verbose_name="Комунальная услуга")
    meter_device = models.ForeignKey(MeterDevice,
                                     related_name='meter_device',
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

class StatisticInstrumentReadings(models.Model):
    date = models.DateField(verbose_name="Дата")
    flat = models.ForeignKey(Flat,
                             on_delete=models.PROTECT,
                             null=False, blank=False,
                             related_name='statistic_instrument_readings',
                             verbose_name="Квартира")
    meter_device = models.ForeignKey(MeterDevice,
                                     on_delete=models.PROTECT,
                                     null=False, blank=False,
                                     related_name='statistic_instrument_readings',
                                     verbose_name="Прибор учета")
    count = models.DecimalField(max_digits=20, decimal_places=5, verbose_name="Показания")

    def __str__(self):
        return f"{self.date.strftime('%B')} {self.flat} ({self.meter_device}) c {self.count}"

    class Meta:
        unique_together = ("date", "flat", "meter_device")
        verbose_name = "Статистика показаний прибора учета"
        verbose_name_plural = "Статистика показаний приборов учета"


class CompanyApartmentBlock(models.Model):
    date = models.DateField(verbose_name="Дата")
    apartment_block = models.ForeignKey(ApartmentBlock,
                                        on_delete=models.PROTECT,
                                        related_name='company_apartment_block',
                                        verbose_name="Многоквартирный дом")
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT,
                                related_name='company_apartment_block',
                                verbose_name="Организация")
    is_active = models.BooleanField(verbose_name="Сотрудничают ", default=False)

    class Meta:
        unique_together = ("date", "apartment_block", "company")
        verbose_name = "Многоквартирный дом управляющей компании"
        verbose_name_plural = "Многоквартирные дома управляющих компаний"

    def __str__(self):
        return f'{self.date} {self.company}-{self.apartment_block} {'сотрудничают' if self.is_active else 'не сотрудничают'}'
from django.db import models

from background_information.models import PrivatePerson, UtilityService


class BuildingBase(models.Model):
    number = models.CharField(max_length=25)
    objects = models.Manager()
    class Meta:
        abstract = True

class BaseModel(models.Model):
    objects = models.Manager()
    class Meta:
        abstract = True

class ApartmentBlock(BuildingBase):
    region = models.CharField(max_length=225, blank=True)
    city = models.CharField(max_length=225, blank=True)
    street = models.CharField(max_length=225, blank=True)
    address = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.city}, {self.street}, дом №{self.number}"

    class Meta:
        verbose_name = "Многоквартирный дом"
        verbose_name_plural = "Многоквартирные дома"


class Entrance(BuildingBase):
    apartment_block = models.ForeignKey('ApartmentBlock', related_name='entrance', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.apartment_block}, подъезд №{self.number} "

    class Meta:
        verbose_name = "Подъезд"
        verbose_name_plural = "Подъезды"


class Flat(BuildingBase):
    entrance = models.ForeignKey('Entrance', related_name='flat', on_delete=models.PROTECT, null=True)
    area_of_apartments = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    owner = models.ForeignKey(PrivatePerson,
                              related_name='private_person',
                              on_delete=models.PROTECT,
                              null=True,
                              blank=True)

    def __str__(self):
        return f"{self.entrance}, квартира №{self.number}"

    class Meta:
        verbose_name = "Квартиру"
        verbose_name_plural = "Квартиры"
        ordering = ['id']


class MeterDevice(BaseModel):
    flat = models.ForeignKey(Flat, related_name='meter_device', on_delete=models.PROTECT, null=True, blank=True)
    type_device = models.IntegerField(choices=UtilityService.TypeOfDevice.choices,
                                      default=UtilityService.TypeOfDevice.DEFAULT,
                                      verbose_name="Тип прибора учета")
    is_installed = models.BooleanField(default=False, verbose_name="Установлен")
    factory_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Заводской (серийный) номер")
    brand = models.CharField(max_length=100, null=True, blank=True, verbose_name="Марка")
    type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Модел")
    verification_interval = models.IntegerField(default=0, verbose_name="Межповерочный интервал")
    electricity = models.BooleanField(default=False, verbose_name="Учет электроэнергии")
    number_of_tariffs = models.IntegerField(default=0, verbose_name="Количество тарифов")
    remote_reading = models.BooleanField(default=False, verbose_name="Дистанционного снятия показаний")
    date_of_sealing = models.DateField(null=True, blank=True, verbose_name="Дата опломбирования")
    installation_date = models.DateField(null=True, blank=True, verbose_name="Дата установки")
    commissioning_date = models.DateField(null=True, blank=True, verbose_name="Дата ввода в эксплуатацию")
    decommissioning_date = models.DateField(null=True, blank=True, verbose_name="Дата вывода из эксплуатации")

    id_gis = models.CharField(max_length=13,
                              null=True,
                              blank=True,
                              verbose_name="Идентификатор ЖКУ")

    def __str__(self):
        return f"{UtilityService.TypeOfDevice(self.type_device).label} №{self.factory_number} {str(self.flat).lower()}"

    class Meta:
        verbose_name = "Прибор учета"
        verbose_name_plural = "Приборы учета"

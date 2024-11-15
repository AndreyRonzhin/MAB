from django.db import models

from background_information.models import PrivatePerson, UtilityService


class BuildingBase(models.Model):

    number = models.CharField(max_length=25)

    class Meta:
        abstract = True


class ApartmentBlock(BuildingBase):

    region = models.CharField(max_length=225, blank=True)
    city = models.CharField(max_length=225, blank=True)
    street = models.CharField(max_length=225, blank=True)
    address = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"Дом №{self.number}"

    class Meta:
        verbose_name = "Многоквартирный дом"
        verbose_name_plural = "Многоквартирные дома"


class Entrance(BuildingBase):
    apartment_block = models.ForeignKey('ApartmentBlock', related_name='entrance', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"Подъезд №{self.number}"

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
        return f"Квартира №{self.number}"

    class Meta:
        verbose_name = "Квартиру"
        verbose_name_plural = "Квартиры"


class MeterDevice(models.Model):

    name = models.CharField(max_length=255)
    flat = models.ForeignKey(Flat, related_name='meter_device', on_delete=models.PROTECT, null=True, blank=True)
    type_device = models.IntegerField(choices=UtilityService.TypeOfDevice.choices,
                                      default=UtilityService.TypeOfDevice.DEFAULT,
                                      verbose_name="Тип прибора учета")
    is_installed = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{UtilityService.TypeOfDevice(self.type_device).label} {str(self.flat).lower()}"

    class Meta:
        verbose_name = "Прибор учета"
        verbose_name_plural = "Приборы учета"

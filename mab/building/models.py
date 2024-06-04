from django.db import models

from background_information.models import PrivatePerson


class BuildingBase(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=25)

    class Meta:
        abstract = True


class ApartmentBlock(BuildingBase):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Многоквартирный дом"
        verbose_name_plural = "Многоквартирные дома"


class Entrance(BuildingBase):
    apartment_block = models.ForeignKey('ApartmentBlock', related_name='entrance', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подъезд"
        verbose_name_plural = "Подъезды"


class Flat(BuildingBase):
    entrance = models.ForeignKey('Entrance', related_name='flat', on_delete=models.PROTECT, null=True)
    area_of_apartments = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    owner = models.ForeignKey(PrivatePerson, related_name='private_person', on_delete=models.PROTECT, null=True,
                              blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Квартиру"
        verbose_name_plural = "Квартираы"

class MeterDevice(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Прибор учета"
        verbose_name_plural = "Приборы учета"

from django.db import models


class BaseModel(models.Model):
    objects = models.Manager()
    class Meta:
        abstract = True

class PrivatePerson(BaseModel):
    firstname = models.CharField(max_length=255, verbose_name="Фамилия")
    lastname = models.CharField(max_length=255, verbose_name="Имя")
    middlename = models.CharField(max_length=255, blank=True, verbose_name="Отчество")

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.middlename}'

    class Meta:
        verbose_name = "Физическое лицо"
        verbose_name_plural = "Физические лица"


class UtilityService(BaseModel):
    class TypesOfQuantity(models.IntegerChoices):
        DEFAULT = 0, 'по умолчанию 1'
        SQUARE = 1, 'полщадь квартиры'
        QUANTITY_OF_PEOPLE = 2, 'количество людей'
        METER_DEVICE = 3, 'по прибору'
        FORMULA = 4, 'формула'

    class TypeOfDevice(models.IntegerChoices):
        DEFAULT = 0, 'тип прибора не определён'
        COLD_WATER = 1, 'Холодная вода'
        HOT_WATER = 2, 'Горячая вода'
        ELECTRICITY = 3, 'Электроэнергия'
        ELECTRICITY_DAY = 4, 'Электроэнергия день'
        ELECTRICITY_NIGHT = 5, 'Электроэнергия ночь'

    fullname = models.CharField(max_length=255, verbose_name="Наименование")
    unit_of_measure = models.ForeignKey("UnitsOfMeasures", on_delete=models.PROTECT, verbose_name="Ед. имерения")

    quantify = models.IntegerField(choices=TypesOfQuantity.choices,
                                   default=TypesOfQuantity.DEFAULT,
                                   verbose_name="Количество для расчета")

    type_device = models.IntegerField(choices=TypeOfDevice.choices,
                                      default=TypeOfDevice.DEFAULT,
                                      verbose_name="Тип прибора учета")

    additionally = models.BooleanField(default=False, verbose_name="Дополнительная")

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Коммунальная услуга"
        verbose_name_plural = "Коммунальные услуги"


class UnitsOfMeasures(BaseModel):
    name = models.CharField(max_length=25, blank=True, verbose_name="Наименование")
    fullname = models.CharField(max_length=255, blank=True, verbose_name="Полное наименование")
    code = models.CharField(max_length=4, blank=True, verbose_name="Код ед. измерения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Единицы измерения"
        verbose_name_plural = "Единицы измерения"

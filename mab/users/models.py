from django.contrib.auth.models import AbstractUser
from django.db import models

from building.models import Flat
from calculation_of_services.models import PersonalAccount


class User(AbstractUser):
    flat = models.ForeignKey(Flat,
                             on_delete=models.PROTECT,
                             null=True,
                             blank=True,
                             verbose_name="Квартира")
    personal_account = models.ForeignKey(PersonalAccount,
                             on_delete=models.PROTECT,
                             null=True,
                             blank=True,
                             verbose_name="Лицевой счет")

    is_accountant = models.BooleanField(verbose_name="Бухгалтер", default=False)

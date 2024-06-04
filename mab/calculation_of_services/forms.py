import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import NumberInput
from django.utils.deconstruct import deconstructible

from .models import InstrumentReading
from building.models import Flat, MeterDevice
from background_information.models import UtilityService


class AddReadingsFormNew(forms.Form):

    date_ = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label='Дата показаний')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['date_'].initial = datetime.date.today()

        devices = MeterDevice.objects.all()

        for i, devices in enumerate(devices):
            name_field = f'value_{i}'
            self.fields[name_field] = forms.FloatField(label=devices)

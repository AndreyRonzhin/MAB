import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import NumberInput
from django.utils.deconstruct import deconstructible

from .models import InstrumentReading
from building.models import Flat, MeterDevice
from background_information.models import UtilityService


class AddReadingsForm(forms.ModelForm):

    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                            label='Дата показаний')
    class Meta:
        model = InstrumentReading
        fields = ['date', 'flat', 'meter_device', 'value']



class AddReadingsFormNew(forms.Form):

    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                            label='Дата показаний')
    def __init__(self, *args, **kwargs):

        devices = kwargs.get('param_devices', None)
        if devices:
            kwargs.pop('param_devices')

        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()

        if devices:
            for device in devices:
                name_field = f"value_{device.id}"
                self.fields[name_field] = forms.FloatField(label=device.name)

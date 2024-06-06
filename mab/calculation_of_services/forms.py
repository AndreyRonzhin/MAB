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
        fields = ['date']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()

        param_devaces = kwargs.get('initial', None)

        if param_devaces:
            for device in param_devaces:
                name_field = f"value_{device['id']}"
                self.fields[name_field] = forms.FloatField(label=device['name'])

    def save(self, commit=True):
        self.cleaned_data


class AddReadingsFormNew(forms.Form):

    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                            label='Дата показаний')
    def __init__(self, *args, **kwargs):

        param_devaces = kwargs.get('param_devaces',None)
        if param_devaces:
            kwargs.pop('param_devaces')

        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()

        if param_devaces:
            for device in param_devaces:
                name_field = f"value_{device['id']}"
                self.fields[name_field] = forms.FloatField(label=device['name'])
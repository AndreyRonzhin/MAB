import datetime
from dal import autocomplete

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import NumberInput
from django.utils.deconstruct import deconstructible

from .models import InstrumentReading, AccrualOfServices, SheetOfServices
from building.models import Flat, MeterDevice, ApartmentBlock, Entrance
from background_information.models import UtilityService

from datetime import date
from django import forms

from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory


class AddReadingsForm(forms.ModelForm):
    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                           label='Дата показаний')

    class Meta:
        model = InstrumentReading
        fields = ['date', 'flat', 'meter_device', 'value']


class AddReadingsFormNew(forms.Form):
    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label='Дата показаний')

    def __init__(self, *args, **kwargs):

        devices = kwargs.get('param_devices', None)
        if devices:
            kwargs.pop('param_devices')

        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()

        if devices:
            for device in devices:
                name_field = f"value_{device.pk}"
                self.fields[name_field] = forms.FloatField(label=device.name)


class DateSelectorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        months = {month: month for month in range(1, 13)}
        years = {year: year for year in [2023, 2024, 2025]}
        widgets = [
            forms.Select(attrs=attrs, choices=months),
            forms.Select(attrs=attrs, choices=years),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, date):
            return [value.month, value.year]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        month, year = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.
        return date(year=int(year), month=int(month), day=1)  # "{}-{}".format(year, month)


class CreateAccruls(forms.Form):
    date = forms.DateField(widget=DateSelectorWidget(), label='Период начисления')
    apartment_block = forms.ModelChoiceField(queryset=ApartmentBlock.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()


class EditAccrualsForm(forms.ModelForm):

    class Meta:
        model = AccrualOfServices
        fields = '__all__'


class AccrualOfServicesForm(forms.ModelForm):

    entrance = forms.ModelChoiceField(
        queryset=Entrance.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='calculation:entrance_autocomplete',
            forward=['apartment_block']
        ),
    )

    class Meta:
        model = AccrualOfServices
        fields = '__all__'


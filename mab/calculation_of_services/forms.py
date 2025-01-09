import datetime
from dal import autocomplete

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import NumberInput
from django.utils.deconstruct import deconstructible

from .models import InstrumentReading, AccrualService, SheetService
from building.models import Flat, MeterDevice, ApartmentBlock, Entrance
from background_information.models import UtilityService

from datetime import date
from django import forms


class AddReadingsForm(forms.ModelForm):
    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                           label='Дата показаний')

    class Meta:
        model = InstrumentReading
        fields = ['date', 'flat', 'meter_device', 'value']


class AddReadingsFormNew(forms.Form):
    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label='Дата показаний')

    def __init__(self, *args, **kwargs):
        instr_read = kwargs.get('instr_read', None)
        kwargs.pop('instr_read')

        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()

        if instr_read:
            for device in instr_read:
                if device.is_installed:
                    name_field = f"value_{device.pk_device}"
                    self.fields[name_field] = forms.FloatField(label=device)


class DateSelectorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        months = {month: month for month in range(1, 13)}
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


class CreateAccrul(forms.Form):
    date = forms.DateField(widget=DateSelectorWidget(), label='Период начисления')
    apartment_block = forms.ModelChoiceField(queryset=ApartmentBlock.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()


class EditAccrualForm(forms.ModelForm):
    class Meta:
        model = AccrualService
        fields = '__all__'


class AccrualServiceForm(forms.ModelForm):
    entrance = forms.ModelChoiceField(
        queryset=Entrance.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='calculation:entrance_autocomplete',
            forward=['apartment_block']
        ),
    )

    class Meta:
        model = AccrualService
        fields = '__all__'

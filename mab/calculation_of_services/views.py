from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.forms import inlineformset_factory, Textarea
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, CreateView, FormView

from building.models import MeterDevice, Flat, Entrance, BuildingBase, ApartmentBlock
from .forms import AddReadingsFormNew, AddReadingsForm, CreateAccruls, EditAccrualsForm
from .utils import DataMixin
from .models import InstrumentReading, AccrualOfServices, PersonalAccount, SheetOfServices

from django.core.cache import cache
from django.db import transaction
from models.api_calculation_of_services import InstrumentReadingAPI
from celery import shared_task


#from tasks import print_message, print_time, calculate

@login_required()
def home(request):
    return redirect('calculation:accruals') if request.user.is_accountant else redirect('calculation:customers')


class CustomersHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'instrument_reading'
    title_page = 'Главная страница'

    def get_queryset(self):
        flat_user = self.request.user.flat
        period = (InstrumentReading.objects.filter(flat=flat_user).order_by("-date__year", "-date__month")
                  .values("date__year", "date__month").distinct("date__year", "date__month"))

        return period

class AccrualHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'accrual_services'
    title_page = 'Главная страница'

    def get_queryset(self):
        period = AccrualOfServices.objects.all()

        return period

class AddReadings(LoginRequiredMixin, DataMixin, FormView):
    form_class = AddReadingsForm
    template_name = 'calculation_of_services/addreadings.html'
    title_page = 'Добавление показаний прибора'


@login_required()
def add_readings_new(request):

    user_id = request.user.id

    if request.method == 'POST':

        instr_read = cache.get(f'instr_read{user_id}')

        form = AddReadingsFormNew(request.POST, param_devices=instr_read.devices)

        if form.is_valid() and save_readings(form, user_id, instr_read):
            return redirect('calculation:home')

    else:

        instr_read = InstrumentReadingAPI(request.user.flat)

        cache.set(f'instr_read{user_id}', instr_read)

        form = AddReadingsFormNew(param_devices=instr_read.devices)

    data = {
        'title': 'Добавление показаний прибора new',
        'form': form,
    }

    return render(request, 'calculation_of_services/addreadingsnew.html', data)


def save_readings(form, user_id, instr_read):

    instr_read.date = form.cleaned_data['date']

    instr_read_request = {k.split('_')[1]: v for k, v in form.cleaned_data.items() if k.startswith('value_')}

    for device_pk, value in instr_read_request.items():
        instr_read.set_current_values(int(device_pk), value)

    valid_instrument_reading = instr_read.valid_instrument_reading()

    if valid_instrument_reading:

        for valid in valid_instrument_reading:
            form.add_error(f"value_{valid[0]}", valid[1])

        return False

    else:

        if instr_read.save_readings():
            cache.delete(f'instr_read{user_id}')

            return True


@login_required
def show_readings_new(request):
    return HttpResponseNotFound("<h1>Страница в разработке </h1>")


@login_required()
def create_accruals(request):

    if request.method == 'POST':

        form = CreateAccruls(request.POST)

        if form.is_valid():

            create_accruals_(form.cleaned_data['apartment_block'], form.cleaned_data['date'])

            return redirect('calculation:home')

    else:

        form = CreateAccruls()

    data = {
        'title': 'Создать начисления',
        'form': form,
    }

    return render(request, 'calculation_of_services/createAccruls.html', data)

def create_accruals_(apartment_block, date):
    pa_qs = PersonalAccount.objects.prefetch_related('flat__entrance__apartment_block').filter(
        flat__entrance__apartment_block=apartment_block)

    for pa in pa_qs:

        accrual = AccrualOfServices()
        accrual.date = date
        accrual.flat = pa.flat
        accrual.entrance = pa.flat.entrance
        accrual.apartment_block = pa.flat.entrance.apartment_block

        accrual.area_of_apartments = pa.flat.area_of_apartments

        accrual.save()

def edit_accruals(request, id):
    accrual_of_services = AccrualOfServices.objects.get(pk=id)


    SheetOfServicesInlineFormSet = inlineformset_factory(AccrualOfServices,
                                                         SheetOfServices,
                                                         fields='__all__',
                                                         extra=0,
                                                         )

    if request.method == "POST":
        form = EditAccrualsForm(request.POST, instance=accrual_of_services)
        formset = SheetOfServicesInlineFormSet(request.POST, request.FILES, instance=accrual_of_services)

        if form.is_valid():
            form.save()

        if formset.is_valid():
            formset.save()

        return redirect('calculation:home')

    else:
        form = EditAccrualsForm(instance=accrual_of_services)
        formset = SheetOfServicesInlineFormSet(instance=accrual_of_services)
    return render(request, "calculation_of_services/editAccrual.html", {"formset": formset,
                                                                                            "form": form})

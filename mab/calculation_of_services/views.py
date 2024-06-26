from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, CreateView, FormView

from building.models import MeterDevice, Flat, Entrance, BuildingBase, ApartmentBlock
from .forms import AddReadingsFormNew, AddReadingsForm
from .utils import DataMixin
from .models import InstrumentReading, AccrualOfServices

from django.core.cache import cache
from django.db import transaction
from celery import shared_task


#from tasks import print_message, print_time, calculate

class CustomersHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'instrument_reading'
    title_page = 'Главная страница'

    def get_queryset(self):
        flat_user = self.request.user.flat
        period = (InstrumentReading.objects.filter(flat=flat_user).order_by("-date__year", "-date__month")
                  .values("date__year", "date__month").distinct("date__year", "date__month"))

        return period


class AddReadings(LoginRequiredMixin, DataMixin, FormView):
    form_class = AddReadingsForm
    template_name = 'calculation_of_services/addreadings.html'
    title_page = 'Добавление показаний прибора'


@login_required()
def add_readings_new(request):
    user_id = request.user.id

    if request.method == 'POST':

        user_cache = cache.get(f'user_cache{user_id}')

        form = AddReadingsFormNew(request.POST, param_devices=user_cache['devices'])

        if form.is_valid():
            if __save_readings(form, user_cache['flat_user'], user_cache['devices']):
                cache.delete(f'user_cache{user_id}')
                return redirect('calculation:home')

    else:

        flat_user = request.user.flat
        devices_qt = MeterDevice.objects.filter(flat=flat_user)

        user_cache = {'flat_user': flat_user,
                      'devices': devices_qt}

        cache.set(f'user_cache{user_id}', user_cache)

        form = AddReadingsFormNew(param_devices=devices_qt)

    data = {
        'title': 'Добавление показаний прибора new',
        'form': form,
    }

    return render(request, 'calculation_of_services/addreadingsnew.html', data)


@login_required
def show_readings_new(request):
    return HttpResponseNotFound("<h1>Страница в разработке </h1>")


def __save_readings(form, flat_user, devices):
    date_add = form.cleaned_data['date']

    if not __is_valid_instrument_reading(form, devices):
        return True

    try:
        with transaction.atomic():
            for device in devices:
                instr_read = {'date': date_add,
                              'flat': flat_user,
                              'meter_device': device,
                              'value': form.cleaned_data[f"value_{device.id}"]
                              }

                InstrumentReading.objects.create(**instr_read)

    except Exception as ex:
        print(ex)
        return False

    return True


def __is_valid_instrument_reading(form, devices):

    is_valid = True

    # получаем даты последние даты показаний по приборам учета
    qs_last_date = (InstrumentReading.objects.filter(meter_device__in=devices).values('meter_device')
                    .annotate(date=Max('date')))

    # формируем список дат
    list_last_date = [last_date['date'] for last_date in qs_last_date]

    # получаем последние показания по приборам учета
    qs_last_values = (InstrumentReading.objects.filter(meter_device__in=devices, date__in=list_last_date)
                      .values('meter_device', 'value'))

    # формируем dict где ключ-id прибора учета значение, значение - последние показания
    instr_read_values = {}
    for device in devices:
        instr_read_values[device.id] = form.cleaned_data[f"value_{device.id}"]

    # сравниваем введёные показания и полученные из базы
    for last_values in qs_last_values:
        if instr_read_values[last_values['meter_device']] < last_values['value']:
            form.add_error(f"value_{last_values['meter_device']}", f'Введённое показание меньше предыдущего.')
            is_valid = False

    return is_valid

class AccrualHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'accrual_services'
    title_page = 'Главная страница'

    def get_queryset(self):
        period = AccrualOfServices.objects.all()

        return period

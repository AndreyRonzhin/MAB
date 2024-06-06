from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, FormView

from building.models import MeterDevice
from .forms import AddReadingsFormNew, AddReadingsForm
from .utils import DataMixin, MENU
from .models import InstrumentReading


class CustomersHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'instrument_reading'
    title_page = 'Главная страница'

    def get_queryset(self):
        period = InstrumentReading.objects.order_by("-date").values("date__year", "date__month").distinct()

        return period

@login_required
def show_readings_new(request):
    return HttpResponseNotFound("<h1>Страница в разработке </h1>")

class AddReadings(LoginRequiredMixin, DataMixin, FormView):
    form_class = AddReadingsForm
    template_name = 'calculation_of_services/addreadings.html'
    title_page = 'Добавление показаний прибора'

    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)

    def get_initial(self):
        devices = MeterDevice.objects.filter(flat=self.request.user.flat)
        param_devaces = []

        for device in devices:
            param_devaces.append({'id': device.id, 'name': device.name})

        return param_devaces

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

@login_required
def add_readings_new(request):

    flat_user = request.user.flat
    devices = MeterDevice.objects.filter(flat=flat_user)
    param_devaces = []
    object_devices = {}
    for device_qt in devices:
        param_devaces.append({'id': device_qt.id, 'name': device_qt.name})
        object_devices[device_qt.id] = device_qt

    if request.method == 'POST':
        form = AddReadingsFormNew(request.POST, param_devaces=param_devaces)
        if form.is_valid():
            date_add = form.cleaned_data['date']
            for id_device, device in object_devices.items():

                instr_read = {'date': date_add,
                              'flat': flat_user,
                              'meter_device': device,
                              'value': form.cleaned_data[f'value_{id_device}']
                              }

                InstrumentReading.objects.create(**instr_read)

            return redirect('calculation:home')

    else:
        form = AddReadingsFormNew(param_devaces=param_devaces)


    data = {
        'menu': MENU,
        'title': 'Добавление показаний прибора new',
        'form': form,
    }

    return render(request, 'calculation_of_services/addreadingsnew.html', data)

from dal import autocomplete

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.generic import ListView
from rest_framework.views import APIView

from building.models import Entrance
from .forms import AddReadingsFormNew, CreateAccrul, EditAccrualForm
from .utils import DataMixin
from .models import InstrumentReading, AccrualService, PersonalAccount, SheetService

from django.core.cache import cache
from .service import OperationInstrumentReading
from .tasks import set_statistic_instrument_readings

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
        period = AccrualService.objects.all()

        return period


@login_required()
def add_readings(request):
    user_id = request.user.id
    session_key = request.session.session_key
    if request.method == 'POST':
        instr_read = cache.get(f'instr_read_{session_key}')

        form = AddReadingsFormNew(request.POST, instr_read=instr_read)

        if form.is_valid() and save_readings(form, instr_read, session_key):
            return redirect('calculation:home')
    else:
        instr_read = OperationInstrumentReading(request.user.flat)

        cache.set(f'instr_read_{session_key}', instr_read)

        form = AddReadingsFormNew(instr_read=instr_read)

    data = {
        'title': 'Добавление показаний прибора',
        'form': form,
    }

    return render(request, 'calculation_of_services/addreadings.html', data)



def save_readings(form, instr_read, session_key):
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
            cache.delete(f'instr_read_{session_key}')

            key = f'instr_read_static_{session_key}'
            cache.set(key, instr_read)
            set_statistic_instrument_readings.delay(key)

            return True


@login_required
def show_readings_new(request):
    return HttpResponseNotFound("<h1>Страница в разработке </h1>")


@login_required()
def create_accruals(request):
    if request.method == 'POST':
        form = CreateAccrul(request.POST)

        if form.is_valid():
            create_accruals_(form.cleaned_data['apartment_block'], form.cleaned_data['date'])

            return redirect('calculation:home')
    else:
        form = CreateAccrul()

    data = {
        'title': 'Создать начисления',
        'form': form,
    }

    return render(request, 'calculation_of_services/createAccruls.html', data)


def create_accruals_(apartment_block, date):
    pa_qs = PersonalAccount.objects.prefetch_related('flat__entrance__apartment_block').filter(
        flat__entrance__apartment_block=apartment_block)

    for pa in pa_qs:
        accrual = AccrualService()
        accrual.date = date
        accrual.flat = pa.flat
        accrual.entrance = pa.flat.entrance
        accrual.apartment_block = pa.flat.entrance.apartment_block

        accrual.area_of_apartments = pa.flat.area_of_apartments

        accrual.save()


def edit_accruals(request, id):
    accrual_of_services = AccrualService.objects.get(pk=id)

    SheetOfServicesInlineFormSet = inlineformset_factory(AccrualService,
                                                         SheetService,
                                                         fields='__all__',
                                                         extra=0,
                                                         )

    if request.method == "POST":
        form = EditAccrualForm(request.POST, instance=accrual_of_services)
        formset = SheetOfServicesInlineFormSet(request.POST, request.FILES, instance=accrual_of_services)

        if form.is_valid():
            form.save()

        if formset.is_valid():
            formset.save()

        return redirect('calculation:home')

    else:
        form = EditAccrualForm(instance=accrual_of_services)
        formset = SheetOfServicesInlineFormSet(instance=accrual_of_services)
    return render(request, "calculation_of_services/editAccrual.html", {"formset": formset,
                                                                        "form": form})


class EntranceAutocompleteView(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Entrance.objects.none()

        apartment_block = self.forwarded.get('apartment_block', None)
        if apartment_block:
            qs = Entrance.objects.filter(apartment_block=apartment_block)
        else:
            qs = Entrance.objects.none()

        return qs

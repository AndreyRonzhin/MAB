from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView, FormView

from .forms import AddReadingsFormNew
from .utils import DataMixin, MENU
from .models import InstrumentReading


class СustomersHome(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'calculation_of_services/index.html'
    context_object_name = 'instrument_reading'
    title_page = 'Главная страница'

    def get_queryset(self):
        return InstrumentReading.objects.all()

class AddReadings(DataMixin, FormView):
    pass
    # form_class = AddReadingsFormNew
    # template_name = 'calculation_of_services/addreadings.html'
    # title_page = 'Добавление показаний прибора'
    #
    # def get(self, request, *args, **kwargs):
    #     pass
    #     return super().get(request, args, kwargs)


@login_required
def add_readings_new(request):

    if request.method == 'POST':
        form = AddReadingsFormNew(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = AddReadingsFormNew()

    data = {
        'menu': MENU,
        'title': 'Добавление показаний прибора new',
        'form': form,
    }
    return render(request, 'calculation_of_services/addreadingsnew.html', data)

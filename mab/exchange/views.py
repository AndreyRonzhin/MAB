from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, Max, QuerySet
from django.http import QueryDict
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from building.models import ApartmentBlock
from calculation_of_services.models import InstrumentReading, CompanyApartmentBlock
from calculation_of_services.service import OperationCompanyApartmentBlock
from .serializers import InstrumentReadingSerializer
from .permissions import ReadApartmentBlockPermission


class InstrumentReadingAPIView(APIView):
    permission_classes = [IsAuthenticated, ReadApartmentBlockPermission, ]

    def get(self, request, id_apartment):
        filter_query = self.get_filter_query(request.query_params)

        try:
            apartment_block = ApartmentBlock.objects.get(id=id_apartment)
        except ObjectDoesNotExist:
            apartment_block = id_apartment

        filter_query |= {'flat__entrance__apartment_block':apartment_block}

        valid_data = self.valid_param(filter_query)

        if valid_data:
            return Response({'errors': valid_data})

        instrument_reading = InstrumentReading.objects.select_related('flat').select_related('meter_device').filter(
            **filter_query).annotate(
            value2=Value(0),
            value3=Value(0))

        return Response({'instrument_reading': InstrumentReadingSerializer(instrument_reading, many=True).data})

    @staticmethod
    def get_filter_query(query_params: QueryDict) -> dict:
        filter_param = {}

        year = query_params.get('year', None)
        month = query_params.get('month', None)
        flat_number = query_params.get('flat_number', None)

        filter_param |= {'date__year':year, 'date__month':month}

        if flat_number:
            filter_param |= {'flat__number': flat_number}

        return filter_param


    @staticmethod
    def valid_param(param_filter:dict)->list[str]:
        result = []

        apartment_block = {'text':'Apartment building not found by id={}',
                           'check': lambda v: isinstance(v, ApartmentBlock)}

        year = {'text': 'Year parameter={} not valid',
                'name_param': 'year',
                'check': lambda v: v.isdigit() and 1<=int(v)}

        month = {'text': 'Month parameter={} not valid',
                 'name_param': 'month',
                 'check': lambda v: v.isdigit() and 1<=int(v)<=12}

        check_param ={'flat__entrance__apartment_block': apartment_block,
                      'date__year': year,
                      'date__month': month,}

        for check_param_key, check_param_value in check_param.items():
            param_value = param_filter.get(check_param_key, None)
            if param_value:
                func_check = check_param_value.get('check')
                if not func_check(param_value):
                    result.append(check_param_value.get('text').format(param_value))
            else:
                result.append(f"Parameter \"{check_param_value['name_param']}\" is not set")

        return result


class ListApartmentBlockUserAPIView(APIView):

    def get(self, request):
        response = []

        company_id = request.user.company_id

        operation_company_apartment_block = OperationCompanyApartmentBlock(company_id)
        active_company_apartment_block = operation_company_apartment_block.list_apartment_block()

        list_id_apartment = list(active_company_apartment_block.keys())
        qs_apartment_block = self.get_data_apartment_block(list_id_apartment)

        for apartment_block in qs_apartment_block:
            response.append(
                {
                    'region': apartment_block['region'],
                    'city': apartment_block['city'],
                    'street': apartment_block['street'],
                    'id': apartment_block['pk'],
                }
            )

        if response:
            return Response({'list_apartment_block': response})
        if response:
            return Response({'info': 'There are no active apartment buildings'})

    @staticmethod
    def get_data_apartment_block(list_id_apartment:list)->QuerySet:
        qs_apartment_block = ApartmentBlock.objects.filter(pk__in=list_id_apartment).values('pk', 'region', 'city',
                                                                                            'street')
        return qs_apartment_block
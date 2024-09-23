from django.shortcuts import render

from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import PrivatePerson
from .serializers import PrivatePersonSerializer


class PrivatePersonViewSet(viewsets.ModelViewSet):
    queryset = PrivatePerson.objects.all()
    serializer_class = PrivatePersonSerializer

    @action(detail=False, methods=['get'])
    def find(self, request):

        name_params = ('firstname', 'lastname', 'middlename')

        filter_name = {}

        for name in name_params:
            value_param = request.query_params.get(name)
            if value_param:
                filter_name[f'{name}__icontains'] = value_param

        qs_private_person = PrivatePerson.objects.filter(**filter_name)

        return Response(self.serializer_class(qs_private_person, many=True).data)

from dal import autocomplete
from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import ApartmentBlock, Entrance
from .serializers import ApartmentBlockSerializer


# class ApartmentBlockViewSet(APIView):
#     def get(self, request):
#         apartment_block = ApartmentBlock.objects.all()
#         serializer = ApartmentBlockSerializer(instance=apartment_block, many=True)
#         return Response(serializer.data)

class ApartmentBlockViewSet(ModelViewSet):

    queryset = ApartmentBlock.objects.all()
    serializer_class = ApartmentBlockSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.response, status=status.HTTP_201_CREATED, headers=headers)

    #def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #
    #     # headers = self.get_success_headers(serializer.data)
    #     # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #     return None




from django.shortcuts import render

from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import PrivatePerson
from .serializers import PrivatePersonSerializer

#viewsets.ModelViewSet
#class PrivatePersonAPIList(generics.ListCreateAPIView):
#     queryset = PrivatePerson.objects.all()
#     serializer_class = PrivatePersonSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, many=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#class PrivatePersonViewSet(mixins.CreateModelMixin,
#                    mixins.RetrieveModelMixin,
#                    mixins.ListModelMixin,
#                    GenericViewSet):
#     serializer_class = PrivatePersonSerializer
#
#     def get_queryset(self):
#         pk = self.kwargs.get("pk")
#
#         if not pk:
#             return PrivatePerson.objects.all()
#
#         return PrivatePerson.objects.filter(pk=pk)
class PrivatePersonViewSet(APIView):

    def get(self, request):
        p = PrivatePerson.objects.all()
        return Response(PrivatePersonSerializer(p, many=True).data)

    def post(self, request):
        serializer = PrivatePersonSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

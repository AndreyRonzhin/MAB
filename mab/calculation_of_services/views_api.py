from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PersonalAccount
from .serializers import PersonalAccountSerializer


class PersonalAccountViewSet(viewsets.ModelViewSet):
    queryset = PersonalAccount.objects.all()
    serializer_class = PersonalAccountSerializer

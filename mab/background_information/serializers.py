import io

from rest_framework import serializers
from .models import PrivatePerson


class PrivatePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivatePerson
        fields = ['firstname', 'lastname', 'middlename', 'id']

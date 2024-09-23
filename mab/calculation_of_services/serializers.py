import io

from rest_framework import serializers
from .models import PersonalAccount


class PersonalAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalAccount
        fields = '__all__'

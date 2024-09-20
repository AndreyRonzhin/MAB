import io

from rest_framework import serializers
from .models import PrivatePerson

class PrivatePersonSerializer(serializers.ModelSerializer):

    # def create(self, validated_data):
    #     return PrivatePerson.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     instance.firstname = validated_data.get("firstname", instance.title)
    #     instance.lastname = validated_data.get("lastname", instance.content)
    #     instance.middlename = validated_data.get("middlename", instance.time_update)
    #     instance.save()
    #     return instance


    class Meta:
        model = PrivatePerson
        fields = ['firstname', 'lastname', 'middlename', 'id']

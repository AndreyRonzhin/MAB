from rest_framework.serializers import Serializer, CharField, IntegerField, DecimalField

class FlatSerializer(Serializer):
    number = CharField(max_length=10)

class MeterDeviceSerializer(Serializer):
    factory_number = CharField(max_length=50)
    type_device = CharField(max_length=15)
    number_of_tariffs = IntegerField()

class InstrumentReadingSerializer(Serializer):
    flat = FlatSerializer()
    meter_device = MeterDeviceSerializer()
    value = DecimalField(max_digits=20, decimal_places=5)
    value2 = DecimalField(max_digits=20, decimal_places=5)
    value3 = DecimalField(max_digits=20, decimal_places=5)



from rest_framework import serializers
from .models import *


class FlatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flat
        fields = ['name', 'number', 'area_of_apartments']

    def create_flat(self, entrance_s, validated_entrance):

        flat_dict = {}
        list_entrance = []
        list_number_flat = []
        for entrance_v in validated_entrance:

            entrance_data = entrance_s.entrance_dict.get(entrance_v['number'])
            list_entrance.append(entrance_data)

            for flat_v in entrance_v['flat']:
                list_number_flat.append(flat_v['number'])

                flat_dict[flat_v['number']] = {'validated_flat': flat_v,
                                               'entrance': entrance_data,
                                               'found': False}

        flat_qs = Flat.objects.filter(entrance__in=list_entrance, number__in=list_number_flat).values('number',
                                                                                                      'name',
                                                                                                      'entrance__number')

        for value_qs in flat_qs:
            flat_dict[value_qs['number']]['found'] = True

        for v in list(filter(lambda v: not v['found'], flat_dict.values())):
            Flat.objects.create(name=v['validated_flat'].get('name'),
                                number=v['validated_flat'].get('number'),
                                area_of_apartments=v['validated_flat'].get('area_of_apartments'),
                                entrance=v['entrance'])


class EntranceSerializer(serializers.ModelSerializer):
    flat = FlatSerializer(many=True, read_only=False)

    apartment_data = None
    entrance_dict = {}

    class Meta:
        model = Entrance
        fields = ['name', 'number', 'flat']

    def set_entrance(self, validated_entrance):

        entrance_number_list = [validated_entrance.get('number') for validated_entrance in validated_entrance]
        entrance_qs = Entrance.objects.filter(apartment_block=self.apartment_data, number__in=entrance_number_list)

        for value_qs in entrance_qs:
            self.entrance_dict[value_qs.number] = value_qs

    def create_entrance(self, validated_entrance):

        for validated_entrance in validated_entrance:

            entrance_data = self.entrance_dict.get(validated_entrance.get('number'), None)

            if not entrance_data:
                entrance_data = Entrance.objects.create(name=validated_entrance.get('name'),
                                                        number=validated_entrance.get('number'),
                                                        apartment_block=self.apartment_data)

                self.entrance_dict[validated_entrance.get('number')] = entrance_data


class ApartmentBlockSerializer(serializers.ModelSerializer):
    response = {}
    apartment_data = None
    entrance = EntranceSerializer(many=True, read_only=False)

    class Meta:
        model = ApartmentBlock
        fields = ['name', 'number', 'entrance']

    def set_apartment(self, number_apartment):
        apartment_qs = ApartmentBlock.objects.filter(number=number_apartment)[:1]

        if apartment_qs:
            self.apartment_data = apartment_qs[0]
            self.response['apartment'] = f'Найден {self.apartment_data}'


    def create(self, validated_data):

        self.set_apartment(validated_data['number'])

        if not self.apartment_data:
            new_validated_data = {'name': validated_data['name'],
                                  'number': validated_data['number']}
            #self.apartment_data = super().create(new_validated_data)
            self.apartment_data = ApartmentBlock.objects.create(**new_validated_data)
            self.response['apartment'] = f'Добавлен {self.apartment_data}'

        entrance_s = EntranceSerializer()
        entrance_s.apartment_data = self.apartment_data
        entrance_s.set_entrance(validated_data.get('entrance'))
        entrance_s.create_entrance(validated_data.get('entrance'))


        flat_s = FlatSerializer()
        flat_s.create_flat(entrance_s, validated_data.get('entrance'))

        pass


        # entrance_qs = Entrance.objects.filter(apartment_block=apartment_data, number__in=entrance_number_list)
        #
        # entrance_dict = {value_qs.number: value_qs for value_qs in entrance_qs}
        #
        # for validated_entrance in validated_data.get('entrance'):
        #
        #     entrance_data = entrance_dict.get(validated_entrance.get('number'), None)
        #
        #     if not entrance_data:
        #         entrance_data = Entrance.objects.create(name=validated_entrance.get('name'),
        #                                                 number=validated_entrance.get('number'),
        #                                                 apartment_block=apartment_data)

        #     #Или можно так?
        #     # validated_entrance_data = {'name': entrance.get('name'),
        #     #                            'number': entrance.get('number'),
        #     #                            'apartment_block': instance}
        #     #
        #     # entrance_serializer = EntranceSerializer()
        #     #
        #     # entrance_serializer.create(validated_entrance_data)
        #
        #     for validated_flat in validated_entrance.get('flat'):
        #         Flat.objects.create(name=validated_flat.get('name'),
        #                             number=validated_flat.get('number'),
        #                             entrance=entrance_data)

        return self.apartment_data

from rest_framework import permissions
from calculation_of_services.service import OperationCompanyApartmentBlock

class ReadApartmentBlockPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        id_apartment = request.parser_context['kwargs'].get('id_apartment')

        company_id = request.user.company_id

        operation_company_apartment_block = OperationCompanyApartmentBlock(company_id)
        company_apartment_block = operation_company_apartment_block.list_apartment_block()

        return company_apartment_block.get(id_apartment, None) is not None
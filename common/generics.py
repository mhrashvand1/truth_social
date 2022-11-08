from common.mixins import PaginationMixin, FilterMixin, SerializerMixin
from rest_framework.viewsets import ViewSet
from rest_framework.settings import api_settings
from rest_framework.response import Response


class CustomGenericViewSet(
    PaginationMixin,
    FilterMixin,
    SerializerMixin,
    ViewSet
):
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        pass 
    
    def paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
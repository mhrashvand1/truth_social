from common.mixins import PaginationMixin, FilterMixin, SerializerMixin
from rest_framework.viewsets import ViewSet
from rest_framework.settings import api_settings


class CustomGenericViewSet(
    PaginationMixin,
    FilterMixin,
    SerializerMixin,
    ViewSet
):
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

from common.mixins import PaginationMixin, FilterMixin, SerializerMixin
from rest_framework.viewsets import ViewSet
from rest_framework.settings import api_settings
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404


class CustomGenericViewSet(
    PaginationMixin,
    FilterMixin,
    SerializerMixin,
    ViewSet
):
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    
    lookup_field = 'pk'
    lookup_url_kwarg = None
    
    def paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
  
    def get_queryset(self):
        pass

    def get_object(self, queryset=None, lookup_field=None, lookup_url_kwarg=None):

        qs = queryset if queryset else self.get_queryset()
        if not qs:
            raise AssertionError('You must to write get_queryset method or send queryset argument to get_object method.')
        queryset = self.filter_queryset(qs)

        lookup_field = lookup_field if lookup_field else self.lookup_field
        lookup_url_kwarg = lookup_url_kwarg if lookup_url_kwarg else self.lookup_url_kwarg
        # Perform the lookup filtering.
        lookup_url_kwarg = lookup_url_kwarg or lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
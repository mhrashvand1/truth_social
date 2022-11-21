from rest_framework.validators import UniqueValidator, qs_filter


class UsernameUniqueValidator(UniqueValidator):
    
    def filter_queryset(self, value, queryset, field_name):
        filter_kwargs = {'%s__%s' % ('username', self.lookup): value}
        return qs_filter(queryset, **filter_kwargs)
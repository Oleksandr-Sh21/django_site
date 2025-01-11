import django_filters

from products.models import AttributeValue, Product


class ProductFilter(django_filters.FilterSet):
    attributes = django_filters.ModelMultipleChoiceFilter(
        queryset=AttributeValue.objects.all(),
        field_name='attributes__attribute_value',
        conjoined=False,
        label="Характеристики"
    )

    class Meta:
        model = Product
        fields = ['attributes']
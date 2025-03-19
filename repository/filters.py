from django_filters import rest_framework as filters
from django_filters import CharFilter, ChoiceFilter, ModelMultipleChoiceFilter
from .models import Experiment, Individual


class ExperimentFilter(filters.FilterSet):
    individual = CharFilter(
        field_name="sample__sampling_event__individual__name",
        lookup_expr="contains",
        label="Individual Name",
    )

    # country = CharFilter(
    #     field_name='sample__sampling_event__collection_country',
    #     lookup_expr='exact',
    #     label='Country'
    # )
    class Meta:
        model = Experiment
        fields = {
            "library_strategy": ["exact"],
        }

class IndividualFilter(filters.FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="contains",
        label='Name'
    )


    class Meta:
        model = Individual
        fields = {
            "sex": ["exact"],
            "organism": ["exact"]
        }

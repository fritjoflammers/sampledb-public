import django_tables2 as tables
from django_tables2.utils import Accessor as A
from .models import Experiment, Individual


class UpperColumn(tables.Column):
    def render(self, value):
        return value.upper()


class ExperimentTable(tables.Table):
    sampling_date = tables.DateColumn(
        accessor="sample.sampling_event.sampling_date",
        verbose_name="Sampling Date")
    sampling_country = tables.Column(
        accessor="sample.sampling_event.sampling_country",
        verbose_name="Country")
    individual = tables.Column(
        accessor="sample.sampling_event.individual.name",
        linkify=(
            "repository:individual",
            {"name": tables.A("sample__sampling_event__individual")},
        ),
        verbose_name="Individual Name",
    )
    file = tables.Column(
        accessor=A("file.count"),
        verbose_name="# Files")
    experiment = tables.Column(accessor="id", linkify=True, verbose_name="Experiment")

    class Meta:
        model = Experiment
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = ("experiment", "individual", "sampling_country", "sampling_date", "library_strategy", "file")


class IndividualTable(tables.Table):

    individual = tables.Column(
        accessor="name",
        linkify=True,
        verbose_name="Name"
    )

    species = tables.Column(
        accessor="organism__scientific_name",
        verbose_name="Species"
    )

    sex = tables.Column(
        accessor=A("sex__name"),
        verbose_name="Sex"
    )

    # throat_color = tables.Column(
    #     accessor="sampling_event__throat_phenotype__label",
    #     verbose_name="Throat Color"
    # )
    # back_color = tables.Column(
    #     accessor="sampling_event.back_color_score",
    #     verbose_name="Back Color"
    # )

    sampling_events = tables.ManyToManyColumn(
        accessor="sampling_event__sampling_date",
        verbose_name="Samples"
    )
    class Meta:
        model = Individual
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = ("individual", "species", "sex", "sampling_events")

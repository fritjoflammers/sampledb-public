from import_export import resources, fields, widgets
from repository.models import (
    BioSample,
    SamplingEvent,
    Organism,
    Age,
    SampleSex,
    Color,
    Tissue,
    TissuePreservative,
    Person,
    Country,
    Instrument,
    Individual,
)


class MultiElementSeparators:
    RINGER_NAME_SEPARATOR = ", "
    PRESERVATIVE_SEPARATOR = ";"


class BioSampleResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        ind_obj = Individual.objects.get(name=row["name"])
        sampling_event_obj = SamplingEvent.objects.get(individual=ind_obj)

        row["sampling_event"] = sampling_event_obj

    sampling_event = fields.Field(
        column_name="sampling_event",
        attribute="sampling_event",
        widget=widgets.ForeignKeyWidget(SamplingEvent, field="label"),
    )

    tissue_type = fields.Field(
        column_name="tissue",
        attribute="tissue",
        widget=widgets.ForeignKeyWidget(Tissue, field="name"),
    )

    preservative = fields.Field(
        column_name="preservative",
        attribute="preservative",
        widget=widgets.ManyToManyWidget(
            TissuePreservative,
            field="label",
            separator=MultiElementSeparators.PRESERVATIVE_SEPARATOR,
        ),
    )

    class Meta:
        model = BioSample
        use_transactions = True


class SamplingEventResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        # Ringer Name get or create
        ringer_name_initials = row["ringer_name"].split(
            MultiElementSeparators.RINGER_NAME_SEPARATOR
        )
        for initials in ringer_name_initials:
            Person.objects.get_or_create(
                initials=initials, defaults={"name": "", "affiliation": "Unknown"}
            )

        individual = row["name"]
        ind_obj = Individual.objects.get(name=individual)
        row["name"] = ind_obj

    individual = fields.Field(
        column_name="name",
        attribute="individual",  # TODO check
        widget=widgets.ForeignKeyWidget(Individual, field="name"),
    )

    collection_country = fields.Field(
        column_name="collection_country",
        attribute="collection_country",
        widget=widgets.ForeignKeyWidget(Country, field="name"),
    )

    ringer_name = fields.Field(
        column_name="ringer_name",
        attribute="ringer_name",
        widget=widgets.ManyToManyWidget(
            Person,
            field="initials",
            separator=MultiElementSeparators.RINGER_NAME_SEPARATOR,
        ),
    )

    throat_phenotype = fields.Field(
        column_name="throat_phenotype",
        attribute="throat_phenotype",
        widget=widgets.ForeignKeyWidget(Color, field="label"),
    )

    back_color_score = fields.Field(
        column_name="back_color_score",
        attribute="back_color_score",
        widget=widgets.ForeignKeyWidget(Color, field="label"),
    )

    neck_color_score = fields.Field(
        column_name="neck_color_score",
        attribute="neck_color_score",
        widget=widgets.ForeignKeyWidget(Color, field="label"),
    )
    collection_date = fields.Field(
        column_name="collection_date",
        attribute="collection_date",
        widget=widgets.DateWidget(format="%d/%m/%Y"),
    )

    class Meta:
        model = SamplingEvent
        use_transactions = True


class IndividualResource(resources.ModelResource):
    organism = fields.Field(
        column_name="organism",
        attribute="organism",
        widget=widgets.ForeignKeyWidget(Organism, field="scientific_name"),
    )

    age = fields.Field(
        column_name="age",
        attribute="age",
        widget=widgets.ForeignKeyWidget(Age, field="label"),
    )

    sex = fields.Field(
        column_name="sex",
        attribute="sex",
        widget=widgets.ForeignKeyWidget(SampleSex, field="name"),
    )

    name = fields.Field(column_name="name", attribute="name")

    class Meta:
        model = Individual
        use_transactions = True


class OrganismResource(resources.ModelResource):
    class Meta:
        model = Organism


class AgeResource(resources.ModelResource):
    class Meta:
        model = Age


class SampleSexResource(resources.ModelResource):
    class Meta:
        model = SampleSex


class ColorResource(resources.ModelResource):
    class Meta:
        model = Color


class PersonResource(resources.ModelResource):
    class Meta:
        model = Person


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country


class InstrumentResource(resources.ModelResource):
    class Meta:
        model = Instrument


class TissuePreservativeResource(resources.ModelResource):
    class Meta:
        model = TissuePreservative


class TissueResource(resources.ModelResource):
    class Meta:
        model = Tissue

from typing import Dict, Type

from django.contrib import admin

from .models import (
    BioSample,
    SamplingEvent,
    Organism,
    Age,
    Experiment,
    SampleSex,
    File,
    Color,
    Tissue,
    TissuePreservative,
    Person,
    ExternalCollection,
    Country,
    Instrument,
    SequencingRun,
    Individual,
)

from import_export.admin import ImportExportModelAdmin
from repository.resources import (
    BioSampleResource,
    OrganismResource,
    AgeResource,
    InstrumentResource,
    CountryResource,
    PersonResource,
    ColorResource,
    SampleSexResource,
    TissuePreservativeResource,
    TissueResource,
)


def register_admin_classes(admin_classes: Dict[Type, Type]):
    """
    Register admin classes for models using the provided mapping.

    Args:
        admin_classes: A dictionary mapping models to their corresponding
        resource classes.
    """

    def generate_admin_class(resource_class: Type) -> Type[ImportExportModelAdmin]:
        """
        Generate a custom admin class using ImportExportModelAdmin as the base class.

        Args:
            resource_class: The resource class for the model.

        Returns:
            AdminClass: The generated admin class.
        """

        class AdminClass(ImportExportModelAdmin):
            resource_classes = [resource_class]

        return AdminClass

    # Register the models with their corresponding admin classes
    for model, resource_class in admin_classes.items():
        admin_class = generate_admin_class(resource_class)
        admin.site.register(model, admin_class)


# Define the mapping between models and resource classes
admin_classes = {
    Organism: OrganismResource,
    BioSample: BioSampleResource,
    Age: AgeResource,
    SampleSex: SampleSexResource,
    Color: ColorResource,
    Person: PersonResource,
    Country: CountryResource,
    Instrument: InstrumentResource,
    TissuePreservative: TissuePreservativeResource,
    Tissue: TissueResource,
    Individual: None,
    SamplingEvent: None,
    Experiment: None,
    File: None,
    ExternalCollection: None,
    SequencingRun: None,
}


register_admin_classes(admin_classes)

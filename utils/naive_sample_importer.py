#!/usr/env python
"""
Import data to Database

Expect 3 CSV files with the following columns:

1) Sample data

2) Library data

3) File data
"""

import argparse
import decimal
import os
from typing import Type
import django.db.models
import numpy as np
import pandas as pd
from django.db import transaction

from decimal import InvalidOperation

# Import relevant models from Django application
from repository.models import (
    BioSample,
    SamplingEvent,
    Organism,
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
    Individual,
)

from datetime import datetime

# Import settings and utilities from Django application
from sampledb.settings.base import DATE_INPUT_FORMATS

from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db.utils import IntegrityError

# Custom exception for database import errors
class DBImportError(Exception):
    pass

def catch_validation_error(func):
    """Decorator to catch validation errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            print(f"Validation Error: {e}")

    return wrapper

def catch_multipleobjects_error(func):
    """ Decorator to catch multiple objects returned errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MultipleObjectsReturned as e:
            print(f"MultipleObjectsReturned Error: {e}")

    return wrapper


# Function to delete all records from the database
def delete_all():
    # Delete all records from specified models
    File.objects.all().delete()
    Experiment.objects.all().delete()
    BioSample.objects.all().delete()
    SamplingEvent.objects.all().delete()
    Individual.objects.all().delete()

    transaction.commit()

def parse_date(date_str):
    """Parse date from string by DATE_INPUT_FORMATS of current language"""
    for item in DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(date_str, item).date()
        except (ValueError, TypeError):
            continue

    return None


def get_single_object(model_obj: Type[django.db.models.Model], **kwargs):
    """Get single object from a Django database model"""
    obj = model_obj.objects.get(**kwargs)
    if type(obj) == model_obj:
        return obj
    if type(obj) == list:
        print(obj)
    else:
        raise DBImportError


def robust_round(number, ndigits=None):
    """Round if applicable, return number as is if not"""
    if type(number) == float:
        return round(number, ndigits)
    else:
        return number


# Labels for input data
INPUT_DATA_LABELS = ["samples", "experiments", "files"]

# Additional attributes for experiment spreadsheet
EXP_SPREADSHEET_ADDITIONAL_ATTRIBUTES = ["i7", "i5", "date_extraction", "dilution"]

parser = argparse.ArgumentParser()

# Add command-line arguments for input CSV files
for data_label in INPUT_DATA_LABELS:
    parser.add_argument(f"--{data_label}", required=True)

# Example command-line arguments for testing
cl_args = (
    "--samples resources/dummy-data/samples_anonymized.csv"
    " --experiments resources/dummy-data/experiments_anonymized.csv"
    " --files resources/dummy-data/files_anonymized.csv"
)

# Parse command-line arguments
args = parser.parse_args(cl_args.split())

# Load data from CSV files into a dictionary
data = {
    label: pd.read_csv(fname).replace(np.nan, None)
    for label, fname in vars(args).items()
}

# Function to create individual, sampling event, and biosample records
@catch_validation_error
def create_individual_sampling_sample(row: pd.Series):
    organism, organism_created = Organism.objects.get_or_create(
        scientific_name=row.organism
    )
    row.sex = "unknown" if not row.sex else row.sex
    sex, sex_created = SampleSex.objects.get_or_create(name=row.sex)

    # create individual
    if row["name"] != "":
        try:
            individual, individual_created = Individual.objects.get_or_create(
                name=row["name"], title=row["name"], organism=organism, sex=sex
            )
            if individual_created:
                print(f">NEW INDIVIDUAL: {individual}")
        except IntegrityError as e:
            print(f"Could not create individual {row['name']}: {e} ")
            return None
    else:
        print(f"ERROR: Can't import data without sample name: {', '.join(row.to_list)}")

    row.collection_country = "Unknown" if row.collection_country is None else row.collection_country

    print(row.collection_country )
    country, country_created = Country.objects.get_or_create(
        name=row.collection_country
    )
    # create sampling event

    if row.throat_phenotype:
        throat_phenotype, throat_phenotype_created = Color.objects.get_or_create(
            label=row.throat_phenotype
        )
    else:
        throat_phenotype = None

    if row.back_color_score:
        back_color_score, back_color_score_created = Color.objects.get_or_create(
            label=row.back_color_score
        )
    else:
        back_color_score = None

    if row.neck_color_score:
        neck_color_score, neck_color_score_created = Color.objects.get_or_create(
            label=row.neck_color_score
        )
    else:
        neck_color_score = None
    try:
        sampling_event, sampling_event_created = SamplingEvent.objects.get_or_create(
            sampling_country=country,
            sampling_location=row.collection_location,
            individual=individual,
            sampling_date=parse_date(row.collection_date),
            sampling_time=row.collection_time,
            sampling_latitude_dec=robust_round(row.collection_latitude_dec, 8),
            sampling_longitude_dec=robust_round(row.collection_longitude_dec, 8),
            sampling_latitude=row.collection_latitude,
            sampling_longitude=row.collection_longitude,
            throat_phenotype=throat_phenotype,
            back_color_score=back_color_score,
            neck_color_score=neck_color_score,
            forehead_length=row.forehead_length,
            bill_length=row.bill_length,
            black_above_eye=row.black_above_eye,
            length_third_primary=row.length_third_primary,
            wing_length=row.wing_length,
            tarsus_length=row.tarsus_length,
            body_mass=row.body_mass,
            projection_first_primary_over_primary_coverts=row.projection_first_primary_over_primary_coverts,  # noqa: E501
            picture_ids=row.picture_ids,
            ring_number=row.ring_number,
            # logger_id=row.logger_id,
            comment="",
        )
    except InvalidOperation as e:
        print(f"Error {e} for row: \n{row}")


    sampling_event.save()

    if row.ringer_name:
        ringers_to_add = []
        for initials in row.ringer_name.strip().split(","):
            ringer, ringer_created = Person.objects.get_or_create(
                initials=initials, defaults={"name": "", "affiliation": "Unknown"}
            )
            ringers_to_add.append(ringer)
        sampling_event.ringer_name.set(ringers_to_add)

    sampling_event.save()

    # create biosample(s)
    preservatives = row.preservative

    if row.external_collection_name:
        external_collection, external_collection_created = ExternalCollection.objects.get_or_create(
            name=row.external_collection_name
        )
    else:
        external_collection = None

    tissue = Tissue.objects.get(name="whole blood")  # FIXME assum everything is blood
    biosample, biosample_created = BioSample.objects.get_or_create(
        sampling_event=sampling_event,
        tissue_type=tissue,
        tissue_sample_box=row.tissue_sample_box,
        tissue_sample_tube=row.tissue_sample_tube,
        external_sample_id=row.external_sample_id,
        external_collection_name=external_collection,
    )
    biosample.save()
    if preservatives:
        for preservative_label in preservatives.split(";"):
            preservative = TissuePreservative.objects.get(label=preservative_label)
            biosample.preservative.add(preservative)
    biosample.save()

    transaction.commit()


@catch_multipleobjects_error
@catch_validation_error
def create_experiment(row_series: pd.Series):
    try:
        individual = get_single_object(Individual, name=row_series.individual)
    except Individual.DoesNotExist:
        print(f"ERROR:Individual {row_series.individual} not found.")
        return None

    try:
        sampling_event = get_single_object(SamplingEvent, individual=individual)
    except SamplingEvent.DoesNotExist:
        print(f"ERROR: SamplingEvent for {individual} not found.")
        return None

    tissue_type, tissue_type_created = Tissue.objects.get_or_create(
        name=row_series.tissue_type
    )

    biosample = get_single_object(
        BioSample, sampling_event=sampling_event, tissue_type=tissue_type
    )

    instrument_model = Instrument.objects.get(
        model=row_series.instrument_model, platform=row_series.platform
    )

    experiment, experiment_created = Experiment.objects.get_or_create(
        title="",
        sample=biosample,
        library_strategy=row_series.library_strategy,
        library_layout=row_series.library_layout,
        library_selection=row_series.library_selection,
        library_source=row_series.library_source,
        instrument_model=instrument_model,
        design_description=row_series.design_description,
        exp_attributes=str(
            dict(
                (fieldname, row_series[fieldname])
                for fieldname in EXP_SPREADSHEET_ADDITIONAL_ATTRIBUTES
            )
        ),
    )

    return experiment


@catch_validation_error
def create_file(row_series: pd.Series):
    experiment = Experiment.objects.get(id=row_series.experiment_id)
    file = File.objects.get_or_create(
        filepath=row_series.filepath,
        checksum=row_series.checksum,
        checksum_type=row_series.checksum_type.lower(),
        host=row_series.host,
        filetype=row_series.filetype,
        experiment=experiment,
    )
    return file

# Create individual, sampling event, and biosample records from sample data
samples = data["samples"].apply(create_individual_sampling_sample, axis=1)

# Create experiment records from experiment data
experiments = data["experiments"].apply(create_experiment, axis=1)
data["experiments"].loc[:, "experiment_id"] = experiments.apply(
    lambda elem: elem.id if elem else None
)

# Merge files data with experiments data and create file records
data["files"] = data["files"].merge(
    data["experiments"],
    how="left",
    left_on="sample_name",
    right_on="individual",
    validate="many_to_one",
)
files = data["files"].apply(create_file, axis=1)

# Commit the transaction to save changes to the database
transaction.commit()

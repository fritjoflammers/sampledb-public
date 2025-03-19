#!/usr/env python

import pandas as pd
import tablib

from repository.admin import (
    IndividualResource,
    SamplingEventResource,
    BioSampleResource,
)


df = pd.read_csv("resources/samples_curated.csv")
df.fillna("", inplace=True)
colnames = df.columns.to_list()

dataset_failed = tablib.Dataset(headers=colnames)

dataset = tablib.Dataset(headers=colnames)
for i, row in df.iterrows():
    dataset.append(row.to_list())

biosample_resource = BioSampleResource()
individual_resource = IndividualResource()
samplingevent_resource = SamplingEventResource()

results = individual_resource.import_data(dataset, dry_run=False)
# results = samplingevent_resource.import_data(dataset, dry_run=True)
# results = biosample_resource.import_data(dataset, dry_run=True)

print(results.totals)

if results.total_rows != len(results.valid_rows()):
    for i, row in df.iterrows():
        dataset = tablib.Dataset(row.to_list(), headers=colnames)
        for resource in [
            individual_resource,
            samplingevent_resource,
            biosample_resource,
        ]:
            results = resource.import_data(dataset, dry_run=True)
            if len(results.valid_rows()) == 1:
                results = resource.import_data(dataset, dry_run=False)
                print(f"row {i} successful  for {resource.__class__()}")
            else:
                print(f"row {i} unsuccessful for {resource.__class__()}")
                dataset_failed.append(row.to_list())
    dataset_failed.get_df().to_csv(
        "resources/samples_curated.failed_import.csv", index=False
    )

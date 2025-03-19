import pandas as pd
import sys

# Read command line arguments as input CSV files
input_csv = sys.argv[1:]

# Load the column information from a CSV file
df_column_info = pd.read_csv("resources/samples_column_info.csv")


def get_column_map(df):
    """
    Generates a mapping dictionary for column name conversion.

    Args:
        df (pd.DataFrame): DataFrame containing the column mapping information.

    Returns:
        dict: A dictionary mapping old column names to new column names.
    """
    df_subset = df[["column_name_tissueDB", "column_name_new"]].dropna()
    df_t = df_subset.transpose()
    df_t.columns = df_t.loc["column_name_tissueDB",].to_list()
    df_t = df_t.drop("column_name_tissueDB")
    column_map = df_t.to_dict("list")
    column_map = dict((key, value[0]) for key, value in column_map.items())
    return column_map


def tissue_preservative_mapper(df, target_colname="preservative"):
    """
    Maps tissue preservation information to a single column.

    Args:
        df (pd.DataFrame): DataFrame containing tissue preservation information.
        target_colname (str): Name of the target column to store preservation data.

    Returns:
        pd.DataFrame: DataFrame with the preservation data mapped to the target column.
    """
    _tp_colnames = ["EtOH", "Thymol", "FTA", "QLB", "RNAlater", "BC-QLB"]
    tp_cols = df[_tp_colnames]
    tp_cols = tp_cols.fillna("no")
    tp_series = tp_cols.apply(
        lambda row: ";".join(row[row == "yes"].index.to_list()), axis=1
    )
    df[target_colname] = tp_series
    df = df.drop(columns=_tp_colnames)
    return df


def prepare_csv(input_csv, column_rename_map):
    """
    Preprocesses an input CSV file.

    Args:
        input_csv (str): Path to the input CSV file.

    Returns:
        pd.DataFrame: Processed DataFrame with renamed and modified columns.
    """
    # Load the raw CSV file
    csv_raw = pd.read_csv(input_csv)
    # Map tissue preservation information to a single column
    csv_raw = tissue_preservative_mapper(csv_raw)
    # Rename columns according to the mapping
    csv_renamed = csv_raw.rename(columns=column_rename_map)
    # Filter columns based on the mapping
    csv_filtered = csv_renamed[list(set(column_rename_map.values()))]
    # Fill missing values with empty strings
    csv_filledNA = csv_filtered.fillna("")
    csv_filledNA["title"] = csv_filledNA.name

    # Replace empty organism values with "Unknown"
    csv_filledNA.loc[csv_filledNA.organism == "", "organism"] = "Unknown"

    # Update sex values to "male" or "female" based on patterns
    csv_filledNA.loc[
        csv_filledNA.sex.str.contains("^m.*", regex=True, case=False), "sex"
    ] = "male"
    csv_filledNA.loc[
        csv_filledNA.sex.str.contains("^f.*", regex=True, case=False), "sex"
    ] = "female"

    # Replace "O." with "Oenanthe" in organism names
    csv_filledNA["organism"] = csv_filledNA.organism.apply(
        lambda x: x.replace("O.", "Oenanthe")
    )
    return csv_filledNA


# Generate a mapping of old column names to new column names
column_rename_map = get_column_map(df_column_info)

# Process and concatenate all input CSV files
csv_output = pd.concat([prepare_csv(file, column_rename_map) for file in input_csv])

# Write the final processed CSV to stdout
csv_output.to_csv(sys.stdout, index=False)

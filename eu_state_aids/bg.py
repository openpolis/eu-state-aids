import os
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import typer
import validators

from eu_state_aids.utils import validate_year

app = typer.Typer()


@app.command()
def fetch(
    year: str,
    local_path: str = typer.Option(
        "./data/bg",
        help="Local path to use for eufunds excel files. Always use forward slashes."
    )
):
    """Fetch Excel file from the source and store it locally.

    Create the directory if it does not exist. Default directory is ./data/bg,
    and it can be changed with local_path.

    Forward slaches based paths are translated into proper paths using `pathlib`,
    so, even on Windows, there's no need to use backward slashes.
    """

    # script parameters validations
    assert(validate_year(year))

    # years are mapped to their codes (sic)
    years_encoding = {
        '2014': '3xRCSNcrgNc%3D',
        '2015': '8U%2BIPGXBzzM%3D',
        '2016': 'L35Wg8m16s0%3D',
        '2017': 'wxlx7atW%2FuQ%3D',
        '2018': 'DrjrB6YmlCo%3D',
        '2019': 'c3E0NC9D3EE%3D',
        '2020': 'ip23bQ8hOOQ%3D',
        '2021': 'mwei5Zc2UEA%3D',
        '2022': '2Q0LfOC9lQ4%3D',
        '2023': 'VuK356PVlaY%3D'
    }

    # create directory if not existing
    local_path = Path(local_path)
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # build remote url and filepath, out of the year,
    typer.echo(f"Fetching EU data for year: {year}")
    excel_url = f"http://2020.eufunds.bg/en/0/0/Project/ExportToExcel?StFrom={years_encoding[year]}&" \
        f"StTo={years_encoding[year]}&ShowRes=True&IsProgrammeSelected=False&IsRegionSelected=False"

    # read remote excel file content
    r = requests.get(excel_url)

    # store it locally
    filepath = local_path / f"projects_{year}.xlsx"
    with open(filepath, 'wb') as f:
        f.write(r.content)
    typer.echo(f"File saved to {filepath}")


@app.command()
def export(
    year: str,
    local_path: str = typer.Option(
        "./data/bg",
        help="Local path to use for eufunds excel files. Leave unset to use eufunds.org source."
    ),
    stateaid_url: str = typer.Option("https://stateaid.minfin.bg/document/860", help="URL of stateaid excel file"),
    program_start_year: str = typer.Option("2014", help="Program's starting year"),
):
    """Read Excel file from local path, produces CSV output in the same local path.

    Local path defaults to ./data/bg, and can be changed with local_path.
    Uses pandas to read from Excel, transform the dataframe, and cross the data with
    a second source to find out which of the EU funds are related to state aids.
    """

    # script parameters validations
    assert(validate_year(year))
    assert(validate_year(program_start_year))
    assert(validators.url(stateaid_url))

    # read the dataframe from the local file
    # the header starts at the 4th line
    # the pandas.DataFrame is created reading from the excel file's url
    typer.echo(f"Fetching EU data for year: {year}")
    local_path = Path(local_path)
    excel_file = local_path / f"projects_{year}.xlsx"
    eu_df = pd.read_excel(f"file://localhost/{os.path.abspath(excel_file)}", header=3)

    # The last 6 rows are removed from the dataframe, as they contain the notes
    eu_df = eu_df[:-6]
    typer.echo(f"DataFrame with {len(eu_df)} rows created from {excel_file}")

    # EU dataframe transformations

    def lookup_name(x):
        try:
            return str(x).split(' ', 1)[1]
        except IndexError:
            return str(x)
    eu_df['Name of the beneficiary'] = eu_df.Beneficiary.apply(lookup_name)

    def lookup_id(x):
        try:
            return int(str(x).split(' ', 1)[0])
        except ValueError:
            return np.NAN
    eu_df['ID of the beneficiary'] = eu_df.Beneficiary.apply(lookup_id)

    def build_eu_prog_id(x):
        splits = x.split('-', 1)
        if len(splits) < 2:
            return np.NAN
        return program_start_year + x.split('-', 1)[0]
    eu_df['European operation program (ID)'] = eu_df['Project proposal number'].apply(build_eu_prog_id)

    eu_df['Amounts (€)'] = eu_df['Total'] * 0.51
    eu_df['Amounts (€)'] = eu_df['Amounts (€)'].astype(float).round(decimals=2)

    eu_df['Date'] = year

    # the stateaid file is fetched (download)
    typer.echo(f"Fetching stateaid data at {stateaid_url}")
    r = requests.get(stateaid_url)

    # DataFrame is created out of a stream, generated by a content
    # the header starts at the 1st line
    # only the first 10 columns are kept
    stateaid_df = pd.read_excel(BytesIO(r.content), header=1)
    stateaid_df = stateaid_df.iloc[:, :10]

    def build_eu_prog_aid_id(x):
        splits = x.split('-')
        if len(splits) < 3:
            return np.NAN
        else:
            return '-'.join(splits[:-1])
    eu_df.dropna(subset=['Project proposal number'], inplace=True)
    eu_df['EUProgAidID'] = eu_df['Project proposal number'].apply(build_eu_prog_aid_id)
    eu_df.dropna(subset=['EUProgAidID', 'ID of the beneficiary'], inplace=True)

    def lookup_prog_id(x):
        """Looks up for program ID in stateaid_df

        :param x:
        :return:
        """
        has_x = stateaid_df[stateaid_df.iloc[:, 1].str.contains(x)]
        if not has_x.empty:
            return has_x.iloc[0, 0].split(',')[0]
        else:
            return np.NAN
    eu_df['State aid Scheme'] = eu_df['EUProgAidID'].apply(lookup_prog_id)
    eu_df.dropna(subset=['State aid Scheme'], inplace=True)

    eu_df.drop(
        columns=[
            'Beneficiary', 'Address', 'Location', 'Project proposal number',
            'Project Name', 'Total', 'Grant', 'Self-financing by the Beneficiary',
            'Actual amounts paid', 'Duration (months)',
            'Status of Implementation of the Contract/Order of the Grant',
            'EUProgAidID'
        ],
        inplace=True
    )

    # emit csv
    typer.echo(f"{len(eu_df)} matches found.")
    csv_filepath = local_path / f"{year}.csv"
    if len(eu_df):
        typer.echo(f"Writing results to {csv_filepath}")
        eu_df.to_csv(csv_filepath, na_rep='', index=False)

import os
import re
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_read_xml as pdx
from pandas_read_xml import flatten, fully_flatten

import requests
import typer

from eu_state_aids.utils import validate_year, validate_year_month

app = typer.Typer()


def normalize_cod_ce(x):
    c = re.compile(r'SA[. ](\d+)')
    m = re.match(c, x)
    if m and len(m.groups()) == 1:
        return f"SA.{m.group(1)}"
    else:
        return np.NAN


@app.command()
def generate_measures(
    local_path: str = typer.Option(
        "./data/it",
        help="Local path to use for XML files. Always use forward slashes."
    )
):
    """Fetch all Misure XML files locally, generate a DataFrame with the fields:
       - COD_CE,
       - DESC_FONDO
    and store a CSV in local_path.

    Create local_path if it does not exist. Forward slaches based paths
    are translated into proper paths using `pathlib`,
    so, even on Windows, there's no need to use backward slashes.
    """

    # create directory if not existing
    local_path = Path(local_path)
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # build remote url and filepath, out of the year,
    typer.echo("Fetching all misure files")

    df = pd.DataFrame()
    for year in range(2014, 2022):
        for month in range(1, 13):

            if year == 2021 and month in (8, 10):
                continue
            if year == 2014 and month < 5:
                continue

            xml_url = f"http://eu-state-aids.s3-eu-west-1.amazonaws.com/it/rna_mirror/" \
                f"OpenDataMisure/OpenData_Misura_{year}_{month:02}.xml.zip"

            typer.echo(f"Processing {xml_url}")

            # read remote excel file content
            r = requests.get(xml_url)
            z = zipfile.ZipFile(BytesIO(r.content))
            z_filename = [f.filename for f in z.filelist][0]
            with z.open(z_filename, "r") as zf:
                ydf = pdx.read_xml(zf.read().decode(), ["ns0:LISTA_MISURE_TYPE"])
                ydf = ydf.pipe(flatten).pipe(flatten)
                if "MISURA|LISTA_COFINANZIAMENTI" not in ydf.columns:
                    continue
                ydf = ydf[
                    ydf.notnull()["MISURA|LISTA_COFINANZIAMENTI"]
                ][['MISURA|COD_CE', 'MISURA|LISTA_COFINANZIAMENTI']]
                ydf = ydf.pipe(flatten).pipe(flatten).pipe(flatten)
                ydf.rename(columns={
                    'MISURA|COD_CE': 'cod_ce',
                    'MISURA|LISTA_COFINANZIAMENTI|COFINANZIAMENTO|DESCRIZIONE_FONDO': 'fondo_desc',
                }, inplace=True)
                ydf = ydf[ydf.notnull()["cod_ce"]]

                if 'MISURA|LISTA_COFINANZIAMENTI|COFINANZIAMENTO|COD_FONDO' in ydf.columns:
                    del ydf['MISURA|LISTA_COFINANZIAMENTI|COFINANZIAMENTO|COD_FONDO']
                    del ydf['MISURA|LISTA_COFINANZIAMENTI|COFINANZIAMENTO|IMPORTO']

                ydf['cod_ce'] = ydf.cod_ce.apply(normalize_cod_ce)
                ydf = ydf[ydf.notnull()["cod_ce"]].drop_duplicates()

                df = df.append(ydf)

    df = df.drop_duplicates()

    # emit csv
    typer.echo(f"{len(df)} recordss found.")
    csv_filepath = local_path / "misure.csv"
    if len(df):
        typer.echo(f"Writing results to {csv_filepath}")
        df.to_csv(csv_filepath, na_rep='', index=False)


@app.command()
def fetch(
    year_month: str,
    local_path: str = typer.Option(
        "./data/it",
        help="Local path to use for XML files. Always use forward slashes."
    )
) -> bool:
    """Fetch Aiuti XML file for the given year and month from the source and store it locally.

    Create the directory if it does not exist. Default directory is ./data/it,
    and it can be changed with local_path.

    Forward slaches based paths are translated into proper paths using `pathlib`,
    so, even on Windows, there's no need to use backward slashes.

    Returns True if the operation fetched the file successfully, False otherwise.
    """

    # script parameters validations
    assert(validate_year_month(year_month))

    year, month = year_month.split("_")

    # create directory if not existing
    local_path = Path(local_path)
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # build remote url and filepath, out of the year,
    typer.echo(f"Fetching Aiuti data for year: {year}, month: {month}")
    z_url = f"http://eu-state-aids.s3-eu-west-1.amazonaws.com/it/rna_mirror/" \
        f"OpenDataAiuti/OpenData_Aiuti_{year}_{month}.xml.zip"

    # read remote excel file content
    r = requests.get(z_url)

    if r.status_code == 200:
        # store it locally
        filepath = local_path / f"aiuti_{year}_{month}.xml.zip"
        with open(filepath, 'wb') as f:
            f.write(r.content)
        typer.echo(f"File saved to {filepath}")
        return True
    else:
        typer.echo("File not found")
        return False


@app.command()
def export(
    year_month: str,
    local_path: str = typer.Option(
        "./data/it",
        help="Local path to use for XML files. "
    ),
    delete_processed: bool = typer.Option(False, help="Delete zipped xml file after processing")
):
    """Read XML from local path, filter with misure from misure.csv, then
    compute and emit data as CSV file.

    Local path defaults to ./data/it, and can be changed with local_path.
    """

    # script parameters validations
    # for both use cases: single month (YYYY_MM) and full year (YYYY)
    if validate_year_month(year_month):
        year, month = year_month.split("_")
    elif validate_year(year_month):
        year, month = year_month, None
    else:
        typer.echo(f"Invalid year, month value: {year_month}. Use YYYY or YYYY_MM.")
        return

    # read misure csv from local_path
    csv_filepath = Path(local_path) / "misure.csv"
    misure_df = pd.read_csv(csv_filepath)
    typer.echo(f"Misure dataframe read from {csv_filepath}.")

    # define months range in both cases
    if month is None:
        months = range(1, 13)
    else:
        months = [int(month)]

    df = pd.DataFrame()  # empty dataframe that will contain all matching records

    # main loop over the months range
    for m in months:
        # if xml file is not already there, then use the fetch program, to fetch it
        if not os.path.exists(Path(local_path) / f"aiuti_{year}_{m:02}.xml.zip"):
            if not fetch(year_month=f"{year}_{m:02}", local_path=local_path):
                continue

        local_path = Path(local_path)
        zip_file = local_path / f"aiuti_{year}_{m:02}.xml.zip"
        typer.echo(f"Processing {zip_file}")

        # parse content of zipped xml file
        z = zipfile.ZipFile(zip_file)
        z_filename = [f.filename for f in z.filelist][0]
        with z.open(z_filename, "r") as zf:
            c = zf.read().decode()
            try:
                adf = pdx.read_xml(re.sub(r"&#(\d+);", "", c), ["LISTA_AIUTI"])
            except Exception as e:
                typer.echo(f"Error {e} while parsing {zip_file}")
                continue

            adf = adf.pipe(fully_flatten)

        # clean up if required
        if delete_processed:
            os.unlink(zip_file)
            typer.echo(f"Removing {zip_file}")

        # skip when no COD_CE_MISURA values are in the xml file
        if 'AIUTO|COD_CE_MISURA' not in adf.columns:
            typer.echo("No COD_CE_MISURA in file")
            continue

        # transform needed columns
        adf = adf[adf.notnull()["AIUTO|COD_CE_MISURA"]]
        adf.rename(columns={
            "AIUTO|COD_CE_MISURA": "cod_ce",
            "AIUTO|DENOMINAZIONE_BENEFICIARIO": "denom_benef",
            "AIUTO|CODICE_FISCALE_BENEFICIARIO": "cf_benef",
            "AIUTO|COMPONENTI_AIUTO|COMPONENTE_AIUTO|STRUMENTI_AIUTO|STRUMENTO_AIUTO|IMPORTO_NOMINALE":
            "componenti_importo_aiuto"
        }, inplace=True)

        # normalise cod_ce into SA.XXXX format
        adf['cod_ce'] = adf.cod_ce.apply(normalize_cod_ce)

        # keep only records with valid cod_ce
        adf = adf[adf.notnull()["cod_ce"]]

        # sip when no valid records
        if len(adf) == 0:
            continue

        # only keep needed columns
        adf = adf[['cod_ce', 'denom_benef', 'cf_benef', 'componenti_importo_aiuto']]

        # join the misure dataframe, to keep only records found in the misure sources
        ydf = pd.merge(adf, misure_df, on="cod_ce", suffixes=("_a", "_m"))

        typer.echo(f"{len(ydf)} records with matching cod_ce found in file")

        # append to final dataframe
        df = df.append(ydf)

    typer.echo(f"{len(df)} matches found.")
    if len(df):
        # transform import into float, before properly summing it
        df.componenti_importo_aiuto = df.componenti_importo_aiuto.astype(float)
        df = df.groupby([
            'cf_benef', 'denom_benef', 'cod_ce', 'fondo_desc'
        ])['componenti_importo_aiuto'].sum().reset_index()

        # emit the final csv for the period
        csv_filepath = local_path / f"{year_month}.csv"
        typer.echo(f"Writing results to {csv_filepath}")
        df.to_csv(csv_filepath, na_rep='', index=False)

import os
import shutil
from pathlib import Path

import requests_mock

from validators.utils import ValidationFailure

from eu_state_aids import __version__
from eu_state_aids.utils import validate_year

from typer.testing import CliRunner

from eu_state_aids.main import app

runner = CliRunner()
encoded_test_year = "8U%2BIPGXBzzM%3D"  # 2015 encoded
excel_test_url = f"http://2020.eufunds.bg/en/0/0/Project/ExportToExcel?StFrom={encoded_test_year}&" \
    f"StTo={encoded_test_year}&ShowRes=True&IsProgrammeSelected=False&IsRegionSelected=False"
local_test_path = Path("./data/test/")


def test_version():
    assert __version__ == "0.1.3"


def test_validate_year_not_int():
    r = validate_year("a3bc")
    assert type(r) == ValidationFailure


def test_validate_year_inrange():
    r = validate_year("2015")
    assert r is True


def test_validate_year_outrange():
    r = validate_year("2009")
    assert type(r) == ValidationFailure
    r = validate_year("2059")
    assert type(r) == ValidationFailure


def test_bg_command():
    result = runner.invoke(app, ["bg", "--help"], prog_name='eu-state-aids')
    assert result.exit_code == 0
    assert "Usage: eu-state-aids bg" in result.stdout


def test_non_existing_command():
    result = runner.invoke(app, ["xx", "--help"], prog_name='eu-state-aids')
    assert result.exit_code != 0


def test_bg_fetch():

    with requests_mock.Mocker() as mock:
        shutil.rmtree(local_test_path)

        mock.get(excel_test_url, text='resp')
        result = runner.invoke(
            app, ["bg", "fetch", "2015", "--local-path=./data/test"], prog_name='eu-state-aids'
        )

        assert result.exit_code == 0
        assert result.stdout == "Fetching EU data for year: 2015\nFile saved to data/test/projects_2015.xlsx\n"

        assert(os.path.exists(local_test_path))
        with open(local_test_path / f"projects_2015.xlsx") as test_xls:
            assert(test_xls.read() == 'resp')


def test_bg_export():

    with open(Path("./tests") / f"bg_projects_sample.xlsx", mode='rb') as sample_xls:
        sample_content = sample_xls.read()

    with requests_mock.Mocker() as mock:
        shutil.rmtree(local_test_path)

        mock.get(excel_test_url, text=str(sample_content))
        result = runner.invoke(
            app, ["bg", "fetch", "2015", "--local-path=./data/test"], prog_name='eu-state-aids'
        )

        assert result.exit_code == 0
        assert result.stdout == "Fetching EU data for year: 2015\nFile saved to data/test/projects_2015.xlsx\n"

        assert(os.path.exists(local_test_path))
        with open(local_test_path / f"projects_2015.xlsx", mode='rb') as test_xls:
            assert(test_xls.read() == sample_content)

        result = runner.invoke(
            app, ["bg", "export", "2015", "--local-path=./data/test"], prog_name='eu-state-aids'
        )
        assert result.exit_code == 0
        assert result.stdout == "Fetching EU data for year: 2015\nFile saved to data/test/projects_2015.xlsx\n"

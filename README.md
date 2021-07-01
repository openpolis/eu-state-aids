## Description

`eu-state-aids` is a package to import **state aids related data** from single countries sources
and produce CSV files, according to a common data structure.

[![TravisCI Badge](https://travis-ci.com/openpolis/eu-state-aids.svg?branch=master "TravisCI building status")](https://travis-ci.com/github/openpolis/eu-state-aids)
[![PyPI version](https://badge.fury.io/py/eu-state-aids.svg)](https://badge.fury.io/py/eu-state-aids)
![Tests Badge](https://op-badges.s3.eu-west-1.amazonaws.com/eu-state-aids/tests-badge.svg?2)
![Coverage Badge](https://op-badges.s3.eu-west-1.amazonaws.com/eu-state-aids/coverage-badge.svg?2)
![Flake8](https://op-badges.s3.eu-west-1.amazonaws.com/eu-state-aids/flake8-badge.svg?2)

The tool provides both a Command Line Interface (the `eu-state-aids` command), 
and an API. See the [Usage](#Usage) section.

The common CSV format used for the export:

|Name|Type|Meaning|
|----|----|-------|
|Name of the beneficiary| String | The name of the aid's beneficiary|
|ID of the beneficiary| Long Integer | The unique ID of the aid's beneficiary|
|European operation program (ID)| String | The unique CCI code of the european program, see details [here](https://ec.europa.eu/sfc/sites/sfc2014/files/QG+pdf/CCI_0.pdf) |
|Amounts (€)| Float with 2 digits precision | Total amount of the project (in Euro) |
|Date| Date `YYYY[-MM-DD]` | Date of the beginning of the aid program (at least the year) |
|State aid Scheme| String | The aid scheme code. The format is `SA.XXXXX`, wher the Xs are digits. |


## Installation

Python versions from 3.7 are supported.
 
The package depends on these python packages:
* typer
* openpyxl
* pandas
* requests
* validators

So, it's better to create a *virtualenv* before installation.

The package is hosted on pypi, and can be installed, for example using pip:

    pip install eu-state-aids 


## Usage

### Command Line Interface
The `eu-state-aids` binary command will be available after installation. 
It offers help with:

    eu-state-aids --help

The `opstate-aids` command can be used to extract the data from the official sources, 
and populate the CSV files.

For each country, data files will firstly be *fetched* and stored locally, 
and thereafter *used* in order to **export** CSV files.

This two-step procedure is useful, since it is not always possible to download source files (Excel, XML, ...) from 
BI systems of nation states, as it has been seen that they tend to time-out whenever the number of records is 
high enough.

The logic of these two phases can vary for each single european state, so each country will have a dedicated module,
that will be executable as a sub-command.

To retrieve data and produce a CSV file for Bulgary (bg), 2015:
 
      eu-state-aids bg fetch 2015
      eu-state-aids bg export 2015

To launch the scripts *for all years* for Bulgary (bg):

    # download all years' excel files into local storage 
    for Y in $(seq 2014 2022)
    do 
      eu-state-aids bg fetch $Y
    done
    
    # process all years' excel files and export CSV records into local storage 
    #./data/bg/$Y.csv files
    for Y in $(seq 2014 2022)
    do
      python  -m eu_state_aids bg export $Y
    done

### API
The fetch and export logics can be used from within a python program, 
importing the packages. All options values must be explicited in API calls.

    from eu_state_aids import bg

    for year in ['2015', '2016', '2017']:
      bg.fetch(year, local_path='./data/bg')
      bg.export(
        year, local_path='./data/bg', 
        stateaid_url="https://stateaid.minfin.bg/document/860", 
        program_start_year="2014"
      )
  

### Note on italian data

Italian government sources suffer from two issues.
1. XML files are not automatically downloadable from single dedicated URLS, but must be downloaded manually,
as the softare solution adopted for the open data section of the web site does not allow such individual downloads.
They have been mirrored on a [public AWS resource](http://eu-state-aids.s3-website-eu-west-1.amazonaws.com/it/rna_mirror/), 
and will be fetched from there.
2. XML files have not been compressed and the `OpenData_Aiuto_*.xml` files are huge (~1GB). Once compressed, 
their size reduce to 1/25th of the original size. So they will be stored on the AWS mirror in zipped format.
 
## Support

There is no guaranteed support available, but authors will try to keep up with issues 
and merge proposed solutions into the code base.

## Project Status
This project is funded by the European Commission and is currently (2021) under active developement.

## Contributing
In order to contribute to this project:
* verify that python 3.7+ is being used (or use [pyenv](https://github.com/pyenv/pyenv))
* verify or install [poetry](https://python-poetry.org/), to handle packages and dependencies in a leaner way, 
  with respect to pip and requirements
* clone the project `git clone git@github.com:openpolis/eu-state-aids.git` 
* install the dependencies in the virtualenv, with `poetry install`,
  this will also install the dev dependencies
* develop wildly, running tests and coverage with `coverage run -m pytest`
* create a [pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
* wait for the maintainers to review and eventually merge your pull request into the main repository

### Testing
Tests are under the tests folder. [requests-mock](https://requests-mock.readthedocs.io/en/latest/index.html)
is used to mock requests to remote data files, in order to avoid slow remote connections during tests.

## Authors
Guglielmo Celata - guglielmo@openpolis.it

## Licensing
This package is released under an MIT License, see details in the LICENSE.txt file.

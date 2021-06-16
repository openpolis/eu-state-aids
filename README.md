## Description

`eu-state-aids` is a Command Line Interface that can be used 
to import **state aids related data** from single countries sources sitesm
and produce CSV files, according to a common  data structure.


![TravisCI Badge](https://travis-ci.com/openpolis/eu-state-aids.svg?branch=master "TravisCI building status")
[![PyPI version](https://badge.fury.io/py/eu-state-aids.svg)](https://badge.fury.io/py/eu-state-aids)
![Tests Badge](https://op-badges.s3.eu-west-1.amazonaws.com/eu-state-aids/tests-badge.svg)
![Coverage Badge](https://op-badges.s3.eu-west-1.amazonaws.com/eu-state-aids/coverage-badge.svg)

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
      eu-state-aids bg export $Y
    done

## Support

There is no guaranteed support available, but issues can be created on this project 
and the authors will try to answer and merge proposed solutions into the code base.

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

### Testing
Tests are under the tests folder. [requests-mock](https://requests-mock.readthedocs.io/en/latest/index.html)
is used to mock requests to remote data files, in order to avoid slow remote connections during tests.

## Authors
Guglielmo Celata - guglielmo@openpolis.it

## Licensing
This package is released under an MIT License, see details in the LICENSE.txt file.


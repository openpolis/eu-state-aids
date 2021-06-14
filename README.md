## Description

`op-state-aids` is a Command Line Interface that can be used 
to import **state aids related data**.


![TravisCI Badge](https://travis-ci.com/openpolis/op-state-aids.svg?branch=master "TravisCI building status")


* passing tests and coverage
* pypi package

## Installation

Python version 3.7 and greater are supported.
 
The package depends on these packages:
* typer
* openpyxl
* pandas
* requests
* validators

So, it's better to create a *virtualenv* before installation.

The package is hosted on pypi, and can be installed, for example using pip:

    pip install op-state-aids 


## Usage

The `op-state-aids` binary command will be available after installation. 
It offers help with:

    op-state-aids --help

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
 
      op-state-aids bg fetch 2015
      op-state-aids bg export 2015

To launch the scripts *for all years* for Bulgary (bg):

    # download all years' excel files into local storage 
    for Y in $(seq 2014 2022)
    do 
      op-state-aids bg fetch $Y
    done
    
    # process all years' excel files and export CSV records into local storage 
    #./data/bg/$Y.csv files
    for Y in $(seq 2014 2022)
      op-state-aids bg export $Y
    done

## Support

There is no guaranteed support available, but issues can be created on this project 
and the authors will try to answer and merge proposed solutions into the code base.

## Project Status

This project is funded by the European Commission and is currently (2021) under active developement.

## Roadmap
Data fetching for over 12 EU countries will be implemented in the course of 2021.
Please have a look at the CHANGELOG.md to check the proceedings.
 


## Contributing
In order to contribute to this project:
* git clone
* tests and coverage
* python versions

## Authors
Guglielmo Celata for Fondazione Openpolis

## Licensing
This package is licensed through an MIT License, see details in the LICENSE.txt file.


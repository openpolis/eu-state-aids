CLI to launch the import of state aids related data.

The `opstate-aids` command can be used to extract the data from the official web sites, 
and populate the CSV files.

To install and launch:

    pip install op-state-aids 
    op-state-aids --help
    
For each country, Excel files can be fetched (and stored locally), and thereafter used in order to produce CSV files.

This two-step procedure is useful, since it is not always possible to download Excel files from 
BI systems of nation states, as it has been seen that they tend to time-out whenever the number of records is 
high enough.

The logic of these two phases can vary for each single european state, so each country will have a dedicated module,
that will be executable as a sub-command.

As an example, to launch the scripts for all years for Bulgary (bg):

    # download all years' excel files into local storage 
    for Y in $(seq 2014 2022)
    do 
      op-state-aids bg fetch
    done
    
    # process all years' excel files and export CSV records into local storage 
    #./data/bg/$Y.csv files
    for Y in $(seq 2014 2022)
      op-state-aids bg export $Y
    done

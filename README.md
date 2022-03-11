# Lab 1 Semantic Data Analysis
Convert a DBLP (Computer Science Bibliography) XML file to CSV format.

## Data Source
Data being used is the BYU Engineering Publications in Scopus 2017-2021. The dataset is available [on kaggle here](https://www.kaggle.com/dpixton/byu-engineering-publications-in-scopus-201721/version/1)

## Notes on loading data to neo4j

Loads CSV, splits columns based on `FIELDTERMINATOR` `,` and splits array based on `|` separator
```cypher
LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/small.csv'
  AS row FIELDTERMINATOR ','
with toInteger( row.id ) AS ID,
split(row.list_name, '|') AS names
RETURN ID, names
LIMIT 3;
```

## Data Pre-processing
Some pre-processing steps took place without scripting and were completed manually via regex commands. Documentation of the steps can be found [here](docs/PRE-PROCESS-STEPS.md).
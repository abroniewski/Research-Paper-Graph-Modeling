# Lab 1 Semantic Data Analysis
Convert a DBLP (Computer Science Bibliography) XML file to CSV format.

### Resources 
Link to OneDrive:
https://universitelibrebruxelles-my.sharepoint.com/personal/adam_broniewski_ulb_be/_layouts/15/onedrive.aspx?ct=1646567441278&or=OWA%2DNT&cid=dada99ac%2D1ba5%2D81b3%2D6166%2D77e719e536e9&id=%2Fpersonal%2Fadam%5Fbroniewski%5Fulb%5Fbe%2FDocuments%2FSDM%20%2D%20Lab01%20%2D%20DBLP%20Research%20Paper%20Modelling

## Notes on loading data to neo4j

Loads CSV, splits columns based on `FIELDTERMINATOR` `;` and splits array based on `|` separator
```cypher
LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/small.csv'
  AS row FIELDTERMINATOR ';'
with toInteger( row.id ) AS ID,
split(row.list_name, '|') AS names
RETURN ID, names
LIMIT 3;
```

## Architecture/ Schema of the Graph

### Article
- ID (Integer)
- author (string[] - string array)
- author-aux (string) 
- cite: (string[] )


`string[]` - means string array.

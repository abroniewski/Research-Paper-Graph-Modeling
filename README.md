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
Columns are in order so the ones to appear first, are first in file as well.

### Article
- article (ID:Integer)
- author (string[] - string array)
- author-aux (string) 
- Author-orcid 
- booktitle:string
- cite: (string[] )
- cite-label: (string)
- crossref: (string)
- editor: (string[])
- editor-orcid: (string[])
- ee: (string[])
- ee-type: (string[])
- i: (string[])
- journal: (string)
- key:string
- mdate:date
- month:string
- note:string[]
- note-label:string
- note-type:string[]
- number:string
- pages:string
- publisher:string
- publnr:string
- publtype:string
- sub:string[]
- sup:string[]
- title:string
- title-bibtex:string
- tt:string[]
- url:string
- volume:string
- year:int
- 
### author_authored_by
- article_id
- author_id

`string[]` - means string array.

--relationships:published_by "output_psublisher_published_by.csv" 
--relationships:edited_by "output_editor_edited_by.csv"  
--relationships:published_in "output_journal_published_in.csv" 
--relationships:has_citation "output_cite_has_citation.csv" 
--relationships:authored_by "output_author_authored_by.csv"
--relationships:submitted_at "output_school_submitted_at.csv" 
--relationships:is_part_of "output_series_is_part_of.csv"

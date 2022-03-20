# Dataset Pre-processing Steps 

## Dropping Columns
Unnecessary columns were dropped prior to any pre-processing to reduce the amount of redundant checks and niche cases that needed to be handled.

## Delimiter replacement
Prior to working with the dataset, some manual pre-processing took place using regex find/replace to get the dataset quickly ready for use.

Prior to setting delimiters, following replacements were completed to account for exceptions:
1. i.e., -> i.e,
2. IEEE., -> EEEE,
3. ACME., -> ACME,
4. OSA., -> OSA,
5. et. al., -> et. al,

With exceptions resolved, a global replacement was completed for:
1. ., -> ,
2. ; -> |

The replacement of the ".," values may not have been required everywhere, but it was done as a quick way to create an array of author names in Neo4j, as all author names were inside `"double quotes"`, which Neo4j treats as strings. These strings can now be split during initialization.

## Header Modifications
Headers were all modified to be lower case and without spaces for easier manipulation and consistency.

## Creating Indexes and Citations
A unique index was created for each paper. There were ~500 missing indexes, so that existing ones (which were unique) were dropped and new unique indexes were created. A column with number of citations existed, but it did not point to specific papers. An array of unique IDs was created equivalent to the number of citations each paper had. This was done with the function `create_cited_by_column(df)` in [neo4j-kaggle-preprocess](src/neo4j-kaggle-preprocess.py)

## Assuming Graph DB Architechture to be
The following heading each corresponds to a different entity in the database. We document here the attributes and the 
relationship ids for each.

### D Recommender
We are using keywords for a community:
- Design
- Product design
- Computer aided design
- Surveys
- Humans
- Friction stir welding
- Machine design


### Article Nodes
it will have these attributes:
- article_no
- title
- year
- 
### Keyword Nodes
- index_keywords

## Depricated section


## Architecture/ Schema of the Graph For DBLP
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

query_string='''
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/output/output_article_2.csv' 
        AS row FIELDTERMINATOR ';'
    WITH row.article as article,
    row.cite AS cite,
    row["cite-label"] AS cite_label,
    row["editor"] AS editor
    return * LIMIT 30 ;
    '''
# Research Paper Grap Modeling
![Current Version](https://img.shields.io/badge/version-v0.1-blue)
![GitHub contributors](https://img.shields.io/github/contributors/abroniewski/IdleCompute-Data-Management-Architecture)
![GitHub stars](https://img.shields.io/github/stars/abroniewski/IdleCompute-Data-Management-Architecture?style=social)

The goal of this project is to explore the use of neo4j as a graph database management system, understand how the data storage impacts query performance and make use of build in algorithms.

## Table of contents
  - [Getting Started](#getting-started)
    - [Tools Required](#tools-required)
    - [Installation](#installation)
  - [Data Source](#data-source)
  - [Development](#development)
    - [Architecture Modeling](#architecture-modeling)
    - [Data Generation](#data-generation)
    - [Data Loading](#data-loading)
    - [Query Performance](#query-performance)
    - [Evolving the Graph](#evolving-the-graph)
    - [Queryies](#queryies)
    - [Algorithms](#algorithms)
    - [Review Recommender](#review-recommender)
  - [Authors](#authors)
  - [License](#license)
    - [Links](#links)

## Getting Started

This project has a single branch: `main`

The project is small and will follow the structure below:

```
	IdelCompute-Data-Management-Architecture
	├── README.md
	├── .gitignore
	└── src
		├── all executbale script files
	└── docs
		├── support documentation and project descriptions
	└── data
		├── raw
		└── processed
```

### Tools Required

You would require the following tools to develop and run the project:

* neo4j desktop client

### Installation

...

## Data Source
Data being used is the BYU Engineering Publications in Scopus 2017-2021. The dataset is available 
[on kaggle here](https://www.kaggle.com/dpixton/byu-engineering-publications-in-scopus-201721/version/1)

## Development

### Architecture Modeling

This architecture for the graph database was chosen to ensure queries being completed take advantage of the graph database linked lists file storage properties. All category information that is needed to match, filter, or aggregate for anticipated queries is placed in the node and edge labels. Repeating information like the year of publication or when a proceeding took place was also stored outside of individual nodes to improve database consistency. This way, errors can be more easily found by visualizing all existing nodes or relationships of a given category.

Queries performance is optimized with the year and journal/proceeding as a node as it quickly eliminates nodes that are not relevant to a query, which improves overall performance. For this type of database, we are looking to optimize on these types of groupings (year, collection type, etc.).

### Data Generation

Data being used is the BYU Engineering Publications in Scopus 2017-2021. The dataset is available on [Kaggle](https://www.kaggle.com/dpixton/byu-engineering-publications-in-scopus-201721/version/1). All data and script to reproduce the database can be found in this git repository. Pre-processing included the following:
- Renaming attributes Article and Conference Paper to Journal and Proceeding
  - Assume: No papers are incorrectly duplicated in years or Journals and Proceedings. 
- Standardizing attribute names with lower case and underscores
- Creating a random set of reviewers and review groups for each paper
  - Assume: reviewers selected from authors in existing data. Review groups all contain 3 reviewers assigned to a review group ID matching the paper ID with no regard for communities, collections, journals, or keywords.
- Creating a unique ID for each paper
- Creating a list of cited papers for each paper
  - Assume: 1-10 citations randomly generated from papers in data.

Attributes not needed for initialization were removed. The pre-processing output was exported to the local repository and the neo4j project import folder. Error checking on the raw data was not done. All data was assumed to be complete and correct.

### Data Loading

Data is all loaded into the database using the LOAD CSV clause. The first query uses the MERGE clause in the order of Year -> document_type -> Paper -> ReviewGroup -> Author. The intention is to limit the number of matches each insertion must check against as it travels down this insertion “branch”, and complete insertion with UNWIND of the authors list in each row of the data. MERGE is used to MATCH or CREATE nodes and edges as needed without duplication.

The document_type node temporary and contains a property with the document_type value (i.e. Journal, Procedure etc.). This node is later relabelled, and the property is dropped in a future query. This approach was used as it is not possible to set label names of nodes or edges dynamically, and there was only a small set of labels to select from. We later discovered the possibility to use the APOC library for dynamic label setting. Since the query involves a search through a small set of different properties in a node, an index is not used for this node.

Citations were generated with a MATCH on each paper in the csv, an UNWIND on the cited papers and a MATCH to create the edges. As CSV LOAD treats all incoming data as a string, numerical data was inputted using toInteger(), and strings had whitespace removed using trim().

A similar approach is followed for all other initiations of nodes and edges. To remain scalable, multiple CSV LOAD calls were completed to manage memory as each neo4j transaction are held in memory until committed . For a larger dataset, or memory constrained machines, we would also include USING PERIODIC COMMIT.

### Query Performance

There are 890 rows of data loaded into the database. Loading performance could be significantly improved by using neo4j-admin import tool through command line . This would require additional pre-processing of the datafiles to ensure the headers are in the correct format for implementation. The performance of graph queries is best when using node or edge pathways, so data that can be used to filter out large numbers of nodes was not loaded into attributes (i.e. the year of publication or when a conference was held).

Creating keywords was initially the most time intensive aspect of the load (13.1s, Table A 1). Using new4j’s PROFILE clause showed a node by label scan was being used (Figure A 1). To optimize performance, a UNIQUE CONSTRAINT was added on keyword which reduced the initialization time to 0.43s (a 29x performance improvement, Table A 2). PROFILE was used on other queries to optimize performance (see Appendix A).

### Evolving the Graph

To explore the functionalities of graph database, the dataset will be evolved to include a review and review decision for each paper as well as an affiliation for each author.

To include the review text and review decision of each paper as well as each authors affiliation the data was added in a nested formatted into the original csv used to initialize the database. The data was then iterated through directly with individual queries called for each instance creation. This caused significant performance issues, as the load was limited by the connection between python and the neo4j instance. If nested data is received this way, the optimized method to load it is by first flattening the data, creating a new csv, and then batch loading the csv using LOAD CSV instead of a nested for loop that establishes a new connection with the database for each insertion. The method used in the python script would never be used in the future, and we learned a lot from making this mistake.

The reviewer comments and decisions were included in the IN_REVIEW_GROUP edge between the review group node and the author to make it possible to query the unique review information for each paper and where the information came from. Affiliation data for each author was included directly in the Author’s node. Including it as a property in the relationship makes it possible maintain the relevant connections. The reviewer comments and decisions were not deemed to be likely candidates for query filtering, and the information is unlikely to change. 

Changes to author affiliation was deemed, in this case, to be infrequent and could be managed easily by modifying specific author nodes. If a database has many authors that share affiliations, affiliation data should be stored in a node instead of as a property.

### Queryies

Some basic queries that can be run are all documented [here in /src/queries](src/cypher_queries.txt)

These queries include:
* Top 3 Cited Papers of Each Conference
* Find the Community of Each Conference
* Calcualte the Impact Factors of Journals
* Calculate the H-indexes of Authors

### Algorithms

Some build in algorithms weer used to test the power and ease of use of neo4j. The algorithm implementation is documentded also found [here in /src/queries](src/cypher_queries.txt)

#### Article Rank
Article Rank was chosen as it shows the relative importance of an article while considering the importance of other articles citing it. In our case, the result shows a ranking of articles, and it successfully provides a differentiation of article importance where the articles have the same number of citations. 

#### Louvain
We chose Louvain algorithm because we wanted to find communities of authors inside the graph. The algorithm finds communities based on how densely the nodes are connected in the graph. In our case it would find the authors that are part of the same community based on the kinds of paper the authors are producing.

### Review Recommender
The review reocmmneder finds the most suitable authors to review other jounrals in a community. The queries complete the following steps:
1) Define Research Communities
2) Find Journals Related to Community
3) Identify Top Papers from Journals in Community
4) Find Top Authors for Community Review

## Authors

#### Adam Broniewski
* [GitHub](https://github.com/abroniewski)
* [LinkedIn](https://www.linkedin.com/in/abroniewski/)
* [Website](https://adambron.com)

#### Mohammed Ismail Tirmizi
* [GitHub](https://github.com/herozero777)

## License

`IdleCompute Data Management Architecture` is open source software [licensed as MIT][license].

### Links
Another project from previous years.
https://iprapas.github.io/posts/neo4j-recommender/

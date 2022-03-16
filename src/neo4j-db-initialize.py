from utils import Neo4jConnection

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")

query_delete_all_existing_nodes = '''
    MATCH (n) DETACH DELETE n
'''
conn.query(query_delete_all_existing_nodes, db='neo4j')

query_create_author_paper_collection_year = '''
// CREATE NODES FOR AUTHORS AND PAPERS + EDGES FOR CONTRIBUTION
// This works by using LOAD CSV to connect to the locally available .csv in the default /import folder of neo4j
// Using MERGE, we check to see is a node called "paper" already exsits. If so, we will add the info, if not
// we will create a new node
// We then UNWIND the array of authors, and again use MERGE to create a node for each authoer (if it doesn't exist)
// Finally, we create an edge connecting each author to the current paper
// NOTE: Using MERGE allows us to make sure we are not creating duplicate nodes for an author that has contributed
//   to multiple papers.
// LEARNING: We cannot create labels for nodes or edges dynamically

    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MERGE (y:Year {year:row.publication_year})
    MERGE (collection:document_type {title:row.source_title, document_type:row.document_type})
    WITH y, collection, row
    MERGE (collection)-[:IN_YEAR]->(y)
    MERGE (p:Paper {name: row.paper, article_no: toInteger(row.article_no)})
    MERGE (p)-[:PUBLISHED_IN]->(y)
    MERGE (p)-[e:IN_COLLECTION]->(collection)
    WITH p, row
    UNWIND split(row.authors, ',') AS author
    MERGE (a:Author {name: author})
    MERGE (a)-[r:CONTRIBUTED]->(p)
    '''
conn.query(query_create_author_paper_collection_year, db='neo4j')

# To have the correct names for Proceeding and Journal nodes, we will use the previously
# created node properties to set the label. This can be done easily with a few queries
# because we have a small set of collection types. We start by setting an index on the
# property "document_type" to improve performance as we will be cycling through properties
# instead of nodes and relations. We then SET the node label for each type of collection we
# have, and REMOVE the previous label and temporary "document_type" property.
query_set_document_type_index = '''
// We will need to cycle through all of the document_type nodes we created to pull the attribute 
// document_type out of the node and label the node with it. 
// We start by creating an INDEX on that property cycling through properties instead of taking 
// advantage of graph database ability to move through relationships is expensive.

CREATE INDEX ON :document_type(document_type)
'''
query_update_proceeding_node_labels = '''
MATCH (n:document_type {document_type:'Proceeding'})
SET n:Proceeding
REMOVE n:document_type
REMOVE n.document_type
'''
query_update_journal_node_labels = '''
MATCH (n:document_type {document_type:'Journal'})
SET n:Journal
REMOVE n:document_type
REMOVE n.document_type
'''
query_update_other_node_labels = '''
// Because this is the last node relabelling query being called, the only remaining nodes with this label
// are those that have not already been renamed. These ones will all be named "Other".
MATCH (n:document_type)
SET n:Other
REMOVE n:document_type
REMOVE n.document_type
'''

#conn.query(query_set_document_type_index, db='neo4j')
conn.query(query_update_proceeding_node_labels, db='neo4j')
conn.query(query_update_journal_node_labels, db='neo4j')
conn.query(query_update_other_node_labels, db='neo4j')

query_create_citations_edges = '''
// CREATE CITATIONS
// We will MATCH on existing papers where the article name is the same as the article name
// for the incoming row of data. Once matched, we will UNWIND the array of citations
// in the "cited_by" column. We then MATCH on nodes that have the same article_no as the
// paper from where the citation is originating. The last WITH statement only calls our
// two matched papers and adds a [CITED] edge between them.
// NOTE: When we create or MERGE, anything that has not already been matched will be created
//   as a new object. So we need to do all of our MATCHES before our MERGE and then we can pull
//   in the found objects using their aliases.
    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MATCH (p:Paper {name: row.article})
    WITH p, row
    UNWIND split(row.cited_by, ',') AS cited_by
    MATCH (p2:Paper {article_no: toInteger(cited_by)})
    WITH p, p2
    MERGE (p)<-[r:CITED]-(p2)
    '''
conn.query(query_create_citations_edges, db='neo4j')

query_to_create_keywords_nodes = """
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/keywords.csv'
    AS row FIELDTERMINATOR ','
    CREATE (k:Keyword {keyword: row.keyword,
                       keyword_id:  toInteger(row.keyword_id) })
    return * ;
"""
#conn.query(query_to_create_keywords_nodes, db='neo4j')

#query_connect_article_to_keywords = """
#LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/keyword_mapping.csv'
#AS row FIELDTERMINATOR ','
#MATCH (a:Article {article_no: toInteger(row.article_no)} )
#MATCH (k:Keyword {keyword_id: toInteger(row.keyword_id)})
#CREATE (a)-[:has_keyword]->(k)
#RETURN a, k;
#"""
#conn.query(query_connect_article_to_keywords, db='neo4j')

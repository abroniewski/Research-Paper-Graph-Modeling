from utils import Neo4jConnection

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")

query_delete_all_existing_nodes = '''
    MATCH (n) DETACH DELETE n
'''

# TODO: remove the first MATCH DELETE statement, or leave it in if we are starting with this initialization first.

query_create_author_and_papers_nodes = '''
// CREATE NODES FOR AUTHORS AND PAPERS + EDGES FOR CONTRIBUTION
// This works by using LOAD CSV to connect to the locally available .csv in the default /import folder of neo4j
// Using MERGE, we check to see is a node called "paper" already exsits. If so, we will add the info, if not
// we will create a new node
// We then UNWIND the array of authors, and again use MERGE to create a node for each authoer (if it doesn't exist)
// Finally, we create an edge connecting each author to the current paper
// NOTE: Using MERGE allows us to make sure we are not creating duplicate nodes for an author that has contributed
//   to multiple papers.

    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MERGE (p:paper {name: row.article, article_no: toInteger(row.article_no)})
    WITH p, row
    UNWIND split(row.authors, ',') AS author
    MERGE (a:author {name: author})
    MERGE (a)-[r:CONTRIBUTED]->(p)
    '''
conn.query(query_create_author_and_papers_nodes, db='neo4j')

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
    MATCH (p:paper {name: row.article})
    WITH p, row
    UNWIND split(row.cited_by, ',') AS cited_by
    MATCH (p2:paper {article_no: toInteger(cited_by)})
    WITH p, p2
    MERGE (p)<-[r:CITED]-(p2)
    '''
conn.query(query_create_citations_edges, db='neo4j')

# TODO: Figure out how to add node connection from paper to journal or proceeding based on type. Was using FOREACH
#  syntax, case would not work...
query_create_edges_from_paper_to_collection = '''
// CREATE PROCEEDINGS
    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MATCH (p:paper {name: row.article})
    FOREACH(ignoreMe IN CASE WHEN row.document_type = 'Proceeding' THEN [1] ELSE [] END | 
        MERGE (type:proceeding {name: row.source_title})
    )
    FOREACH(ignoreMe IN CASE WHEN row.document_type = 'Journal' THEN [1] ELSE [] END | 
    MERGE (p)-[:IN_COLLECTION]->(:journal {name: row.source_title})
    )
    FOREACH(ignoreMe IN CASE WHEN row.document_type <> 'Journal' OR row.document_type <> 'Proceeding' THEN [1] ELSE [] 
    END | 
    MERGE (p)-[:IN_COLLECTION]->(:other {name: row.source_title})
    )
    MERGE (p)-[:IN_COLLECTION]->(type)
    '''
conn.query(query_create_edges_from_paper_to_collection, db='neo4j')

# test query, delete later
query_match_and_return_in_collection_nodes = '''
// Match and return nodes
MATCH (p:paper {article_no:18})-[e:IN_COLLECTION]->(collection:Proceeding)-[:IN_DATE]->(y:Year)
RETURN p,collection,y
'''
conn.query(query_match_and_return_in_collection_nodes, db='neo4j')

query_string_to_create_article_nodes = """
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/article.csv'
    AS row FIELDTERMINATOR ','
    CREATE (a:Article {article_no: toInteger(row.article_no),
                       title: row.title,
                       year: row.year })
    return *;
"""
conn.query(query_string_to_create_article_nodes, db='neo4j')

query_to_create_keywords_nodes = """
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/keywords.csv'
    AS row FIELDTERMINATOR ','
    CREATE (k:Keyword {keyword: row.keyword,
                       keyword_id:  toInteger(row.keyword_id) })
    return * ;
"""
conn.query(query_to_create_keywords_nodes, db='neo4j')

#query_connect_article_to_keywords = """
#LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/keyword_mapping.csv'
#AS row FIELDTERMINATOR ','
#MATCH (a:Article {article_no: toInteger(row.article_no)} )
#MATCH (k:Keyword {keyword_id: toInteger(row.keyword_id)})
#CREATE (a)-[:has_keyword]->(k)
#RETURN a, k;
#"""
#conn.query(query_connect_article_to_keywords, db='neo4j')

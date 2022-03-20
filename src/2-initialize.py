from utils import Neo4jConnection
import time

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")


def delete_all_existing_nodes():
    print(f"Deleting all existing nodes and edges.")
    tic = time.perf_counter()
    query_delete_all_existing_nodes = '''
        MATCH (n) DETACH DELETE n
    '''
    conn.query(query_delete_all_existing_nodes, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def create_author_paper_collection_year():
    print(f"Creating authors, papers, collections and years.")
    tic = time.perf_counter()
    query_create_author_paper_collection_year = '''
    // CREATE NODES FOR AUTHORS AND PAPERS + EDGES FOR CONTRIBUTION
    // This works by using LOAD CSV to connect to the locally available .csv in the default /import folder of neo4j
    // Using MERGE, we check to see is a node called "paper" already exists. If so, we will add the info, if not
    // we will create a new node
    // We then UNWIND the array of authors, and again use MERGE to create a node for each authoer (if it doesn't exist)
    // Finally, we create an edge connecting each author to the current paper
    // NOTE: Using MERGE allows us to make sure we are not creating duplicate nodes for an author that has contributed
    //   to multiple papers.
    // LEARNING: We cannot create labels for nodes or edges dynamically
    // LEARNING: trim() removes whitespace before and after
    // LEARNING: NEVER FORGET!!! You should be creating csv files for your nodes and your edges. Using pure CYPHER for
    // your loading is like using SQL on something that Python can to simply. It's not worth it.... Here we needed
    // to deal with multiple UNWINDs, resulting in CYPHER challenges we would not have encountered working in Python.
    
    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MERGE (y:Year {year:row.publication_year})
    MERGE (collection:document_type {title:row.source_title, document_type:row.document_type})
    WITH y, collection, row
    MERGE (collection)-[:IN_YEAR]->(y)
    MERGE (p:Paper {name: row.paper, article_no: toInteger(row.article_no)})
    MERGE (p)-[:PUBLISHED_IN]->(y)
    MERGE (p)-[e:IN_COLLECTION]->(collection)
    MERGE (rg:ReviewGroup {group_id: toInteger(row.review_group)})
    MERGE (p)-[:REVIEWED_BY]->(rg)
    WITH p, row
    UNWIND split(row.authors, ',') AS author
    MERGE (a:Author {name: trim(author)})
    MERGE (a)-[r:CONTRIBUTED]->(p)
    '''
    conn.query(query_create_author_paper_collection_year, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc-tic:0.4f} seconds\n")


def add_peer_review_group_authors():
    print(f"Creating peer review groups with authors.")
    tic = time.perf_counter()
    query_add_peer_review_group_authors = '''
        LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
        MATCH (rg:ReviewGroup {group_id: toInteger(row.review_group)})
        WITH row, rg
        UNWIND split(row.reviewers, ',') AS reviewer
        MATCH (a:Author {name: trim(reviewer)})
        CREATE (a)-[:IN_REVIEW_GROUP]->(rg)
    '''
    conn.query(query_add_peer_review_group_authors, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc-tic:0.4f} seconds\n")


def update_document_type_node_labels():
    # To have the correct names for Proceeding and Journal nodes, we will use the previously
    # created node properties to set the label. This can be done easily with a few queries
    # because we have a small set of collection types. We start by setting an index on the
    # property "document_type" to improve performance as we will be cycling through properties
    # instead of nodes and relations. We then SET the node label for each type of collection we
    # have, and REMOVE the previous label and temporary "document_type" property.
    print(f"Updating document type node labels.")
    tic = time.perf_counter()
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
    query_drop_document_type_index = '''
    // Removing index for no longer required document_type
        DROP INDEX ON :document_type(document_type)
    '''
    conn.query(query_set_document_type_index, db='neo4j')
    conn.query(query_update_proceeding_node_labels, db='neo4j')
    conn.query(query_update_journal_node_labels, db='neo4j')
    conn.query(query_update_other_node_labels, db='neo4j')
    conn.query(query_drop_document_type_index, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc-tic:0.4f} seconds\n")


def create_citations_edges():
    print(f"Creating citation relationships.")
    tic = time.perf_counter()
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
        MATCH (p:Paper {name: row.paper})
        WITH p, row
        UNWIND split(row.cited_by, ',') AS cited_by
        MATCH (p2:Paper {article_no: toInteger(cited_by)})
        WITH p, p2
        MERGE (p)<-[r:CITED]-(p2)
        '''
    conn.query(query_create_citations_edges, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc-tic:0.4f} seconds\n")


def create_keywords_from_index_nodes():
    #TODO: This keyword long is expensive. Can it be made faster by using a keyword index and matching on the index
    # instead of on the string?
    print(f"Creating keywords.")
    tic = time.perf_counter()
    query_create_keywords_from_index_nodes = '''
    // LEARNING: when matching on indexes, always add toInteger as CSV LOAD reads everything in as a string.
    
        LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
        WITH row
        UNWIND split(row.index_keywords, ';') AS kw
        MERGE (k:Keyword {keyword: trim(kw)})
        WITH row, k
        MATCH (p:Paper {article_no: toInteger(row.article_no)})
        MERGE (p)-[r:TOPIC]->(k)
        '''
    conn.query(query_create_keywords_from_index_nodes, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc-tic:0.4f} seconds\n")


##################################
# Main Program Run
##################################

if __name__ == '__main__':
    print(f"\n**** Starting neo4j database initialization ****\n")
    main_tic = time.perf_counter()

    delete_all_existing_nodes()
    create_author_paper_collection_year()
    add_peer_review_group_authors()
    update_document_type_node_labels()
    create_keywords_from_index_nodes()

    main_toc = time.perf_counter()
    print(f"*** Initialization Complete. Total time: {main_toc - main_tic:0.4f} seconds ****")
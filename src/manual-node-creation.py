# COPY PASTE the code below to create nodes

# TODO: add an edge that connects a paper to the year it participated in a conference

query_create_dummy_proceeding_and_journal_nodes = '''
// Cypher Queries to create dummy values for proceeding and Journal

MATCH (p:Paper {article_no:11})
MERGE (collection:Proceeding {title:'Optical Fiber Technology'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:12})
MERGE (collection:Proceeding {title:'Optical Fiber Technology'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2020}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:13})
MERGE (collection:Journal {title:'Journal 1'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:14})
MERGE (collection:Proceeding {title:'Proceeding A'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:15})
MERGE (collection:Proceeding {title:'Proceeding A'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:16})
MERGE (collection:Proceeding {title:'Optical Fiber Technology'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);

MATCH (p:Paper {article_no:17})
MERGE (collection:Proceeding {title:'Optical Fiber Technology'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (collection)-[:IN_DATE]->(y:Year {year:2022});

MATCH (p:Paper {article_no:18})
MERGE (collection:Proceeding {title:'Proceeding A'})
MERGE (p)-[e:IN_COLLECTION]->(collection)
WITH collection
MERGE (y:Year {year:2021}) 
MERGE (collection)-[:IN_DATE]->(y);
'''
conn.query(query_create_dummy_proceeding_and_journal_nodes, db='neo4j')

'''
MATCH (p:Paper {article_no:17})-->(c:Proceeding)-->(y:Year)
RETURN p,c,y;
'''
from utils import Neo4jConnection

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")


# TODO: Here we are forced to UNWIND 3 columns at once -> reviewer, reviews, and decisions. This is a complex
#   if we try to do it in Cypher. Use Pietro approach instead with dynamic variables in python.
query_add_peer_review_group_details = '''

    LOAD CSV WITH HEADERS FROM 'file:///publications_processed_evolution.csv' AS row FIELDTERMINATOR ','
    MATCH (group:ReviewGroup {group_id: toInteger(row.review_group)})
    WITH row, group
    UNWIND split(row.reviews, ',') AS review
    MATCH (r:Author {author_id: toInteger(reviewer_id)})
    MERGE (group)-[:REVIEWED_WITH]-(r)
    CREATE (p)-[:REVIEWED_BY]->(group)


reviews
decision
    '''
conn.query(query_add_peer_review_group_details, db='neo4j')
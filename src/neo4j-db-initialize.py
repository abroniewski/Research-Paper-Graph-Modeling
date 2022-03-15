from neo4j import GraphDatabase
import logging
import sys
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import csv
from os.path import join

# This python script is used to intialize the database and create all nodes and edges

# link between python and Neo4j (Ismail)

# Authors and Citations (Adam)

# CREATE NODES FOR AUTHORS AND PAPERS + EDGES FOR CONTRIBUTION
# This works by using LOAD CSV to connect to the locally available .csv in the default /import folder of neo4j
# Using MERGE, we check to see is a node called "paper" already exsits. If so, we will add the info, if not
# we will create a new node
# We then UNWIND the array of authors, and again use MERGE to create a node for each authoer (if it doesn't exist)
# Finally, we create an edge connecting each author to the current paper
# NOTE: Using MERGE allows us to make sure we are not creating duplicate nodes for an author that has contributed
#   to multiple papers.

# TODO: remove the first MATCH DELETE statement, or leave it in if we are starting with this initialization first.

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")
query_string = '''
    MATCH (n) DETACH DELETE n;
    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MERGE (p:paper {name: row.article, article_no: toInteger(row.article_no)})
    WITH p, row
    UNWIND split(row.authors, ',') AS author
    MERGE (a:author {name: author})
    MERGE (a)-[r:CONTRIBUTED]->(p)
    WITH p, row
    MERGE (type:proceeding {name: row.source_title})
    MERGE (p)-[:IN_COLLECTION]->(type)
    
    MATCH p = ()-[]->()
    RETURN *
    '''

# CREATE CITATIONS
# We will MATCH on existing papers where the article name is the same as the article name
# for the incoming row of data. Once matched, we will UNWIND the array of citations
# in the "cited_by" column. We then MATCH on nodes that have the same article_no as the
# paper from where the citation is originating. The last WITH statement only calls our
# two matched papers and adds a [CITED] edge between them.
# NOTE: When we create or MERGE, anything that has not already been matched will be created
#   as a new object. So we need to do all of our MATCHES before our MERGE and then we can pull
#   in the found objects using their aliases.
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")
query_string = '''
    MATCH ()-[r:CITED]->() DELETE r;
    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MATCH (p:paper {name: row.article})
    WITH p, row
    UNWIND split(row.cited_by, ',') AS cited_by
    MATCH (p2:paper {article_no: toInteger(cited_by)})
    WITH p, p2
    MERGE (p)<-[r:CITED]-(p2)

    MATCH p = ()-[:CITED]->()
    RETURN *
    '''


# CREATE PROCEEDINGS
# TODO: Figure out how to add node connection from paper to journal or proceeding based on type. Was using FOREACH
#  syntax, case would not work...
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")
query_string = '''
    MATCH (n:paper) DETACH DELETE n;
    MATCH (n:proceeding) DETACH DELETE n;
    MATCH (n:other) DETACH DELETE n;

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
    

    MATCH p = (:paper)-[:IN_COLLECTION]->()
    RETURN p
    '''

# Cypher Queries to create dummy values for proceeding and Journal
'''
MATCH (p:paper {article_no:0})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Advances in Intelligent Systems and Computing'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:1})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Lecture Notes in Electrical Engineering'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:2})
MERGE (p)-[e:IN_COLLECTION]->(:Review {title:'Journal of Hydraulic Engineering'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:3})
MERGE (p)-[e:IN_COLLECTION]->(:Journal {title:'Journal of Computing and Information Science in Engineering'})-[
:IN_DATE]->(:Year {year:2020});
MATCH (p:paper {article_no:4})
MERGE (p)-[e:IN_COLLECTION]->(:Journal {title:'Telematics and Informatics'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:5})
MERGE (p)-[e:IN_COLLECTION]->(:Journal {title:'Telematics and Informatics'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:6})
MERGE (p)-[e:IN_COLLECTION]->(:Journal {title:'Telematics and Informatics'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:7})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Lecture Notes in Electrical Engineering'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:8})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Lecture Notes in Electrical Engineering'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:9})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'IEEE Robotics and Automation Letters'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:10})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'IEEE Robotics and Automation Letters'})-[:IN_DATE]->(
:Year {year:2020});
MATCH (p:paper {article_no:11})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Optical Fiber Technology'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:12})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Optical Fiber Technology'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:13})
MERGE (p)-[e:IN_COLLECTION]->(:Journal {title:'Journal 1'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:14})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Proceeding A'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:15})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Proceeding A'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:16})
MERGE (p)-[e:IN_COLLECTION]->(:Proceeding {title:'Optical Fiber Technology'})-[:IN_DATE]->(
:Year {year:2021});
MATCH (p:paper {article_no:17})
MERGE (p)-[e:IN_COLLECTION]->(collection:Proceeding {title:'Optical Fiber Technology'})
WITH collection
MERGE (collection)-[:IN_DATE]->(:Year {year:2021});

MATCH (p:paper {article_no:18})
MERGE (p)-[e:IN_COLLECTION]->(collection:Proceeding {title:'Proceeding A'})
WITH collection
MERGE (collection)-[:IN_DATE]->(:Year {year:2021});

# Match and return nodes
MATCH (p:paper {article_no:18})-[e:IN_COLLECTION]->(collection:Proceeding)-[:IN_DATE]->(y:Year)
RETURN p,collection,y

# Delete all IN_COLLECTION edges
MATCH (p:Proceeding)-[:IN_DATE]->(y:Year) DETACH DELETE p,y;
'''

### Articles and Journals (Ismail)
##################################################
# Global Variables
##################################################
NUMBER_OF_LINES = 20


##################################################
# Helper
##################################################
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def clean_header_str(header_file_path):
    with open(header_file_path, 'r') as abfile:
        header = csv.reader(abfile, delimiter=';')
        header_list = next(header)
        # print( header_list )
        heading_clean = [heading.split(':')[0] for heading in header_list]
        heading_str = ';'.join(heading_clean)
        print(f'hdr_str: {heading_str}')
        # so that next lines in the file starts from next line and not from the end of header_str
        return heading_str + '\n'


def prepare_entity_n_truncate(project_dir, entity_file, entity_header, entity_out_name_name, num_lines=NUMBER_OF_LINES):
    """
    This reads header line from header file & clean it. Creates a new file with header and places specified lines from
     entity file below it.
    :param str project_dir:
    :param str entity_file:
    :param str entity_header:
    :param str entity_out_name_name:
    :param int num_lines:
    :return:
    """
    heading_str = clean_header_str(entity_header)
    with open(entity_out_name_name, 'w') as file_handle_out:
        file_handle_out.write(heading_str)
        with open(entity_file, 'r') as contents:
            for i, line in enumerate(contents):
                file_handle_out.write(line)
                if i == NUMBER_OF_LINES:
                    break

    return True


# Python script for pre-processing checks
project_dir = "/home/teemo/.config/Neo4j Desktop/Application/relate-data/projects/project-ec569d0a-1cfc-4569-8aa8-cf7729f3de61/output/"
article_og = join(project_dir, "output_article.csv")
article_header = join(project_dir, "output_article_header.csv")
article_out = join(project_dir, "article_20.csv")

a = prepare_entity_n_truncate(project_dir, entity_file=article_og, entity_header=article_header,
                              entity_out_name_name=article_out)

print(a)

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")

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

query_connect_article_to_keywords = """
LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/keyword_mapping.csv'
AS row FIELDTERMINATOR ','
MATCH (a:Article {article_no: toInteger(row.article_no)} )
MATCH (k:Keyword {keyword_id: toInteger(row.keyword_id)})
CREATE (a)-[:has_keyword]->(k)
RETURN a, k;
"""
conn.query(query_connect_article_to_keywords, db='neo4j')

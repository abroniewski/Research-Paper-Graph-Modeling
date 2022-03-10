from neo4j import GraphDatabase
import logging
import sys
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import csv
from os.path import join
# This python script is used to intialize the database and create all nodes and edges

# link between python and Neo4j (Ismail)


#file location naming convention -> f"{name_directory}/output_school.csv"
output_author.csv

# Authors and Citations (Adam)

# Creating nodes for authors

# TODO: add split/UNWIND? to create a node for each name in a row

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")
query_string='''
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-b7855507-1cee-4692-8ff3-f3e64ffe6e1a/scopusBYUEngr17_21.csv' 
        AS row FIELDTERMINATOR ','
    CREATE (:Author {name: row.authors})
    return * LIMIT 30 ;
    '''

conn.query(query_string, db='neo4j')


LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-b7855507-1cee-4692-8ff3-f3e64ffe6e1a/output_author_small.csv' AS line FIELDTERMINATOR ';'
CREATE(:Author {id: toInteger(line.id), name: line.author})

#Creating citation csv for all authors that are currently in output_author_small


# write Cypher query to create nodes and edges

# Python script for pre-processing checks




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

print( a )

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

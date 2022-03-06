from neo4j import GraphDatabase
import logging
import sys
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import csv
# This python script is used to intialize the database and create all nodes and edges

# link between python and Neo4j (Ismail)



# directory definition

processed_data_directory = "data/processed/dblp-to-csv"
ismail_directory = ""
adam_directory ="http://localhost:11001/project-b7855507-1cee-4692-8ff3-f3e64ffe6e1a"
#file location naming convention -> f"{name_directory}/output_school.csv"
output_author.csv

# Authors and Citations (Adam)

# Creating nodes for authors
LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-b7855507-1cee-4692-8ff3-f3e64ffe6e1a/output_author_small.csv' AS line FIELDTERMINATOR ';'
CREATE(:Author {id: toInteger(line.id), name: line.author})

#Creating citation csv for all authors that are currently in output_author_small


# write Cypher query to create nodes and edges

# Python script for pre-processing checks




### Articles and Journals (Ismail)

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


# Python script for pre-processing checks

main_file = "/home/teemo/.config/Neo4j Desktop/Application/relate-data/projects/project-ec569d0a-1cfc-4569-8aa8-cf7729f3de61/output/output_article.csv"

with open("/home/teemo/.config/Neo4j Desktop/Application/relate-data/projects/project-ec569d0a-1cfc-4569-8aa8-cf7729f3de61/output/output_article_header.csv", 'r') as abfile:
    header = csv.reader(abfile, delimiter=';')
    header_list = next(header)
    # print( header_list )
    heading_clean = [ heading.split(':')[0] for heading in header_list ]
    heading_str = ';'.join(heading_clean)
    print(heading_str)

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

line_prepender(main_file, heading_str)

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")
query_string='''
    LOAD CSV WITH HEADERS FROM 'http://localhost:11001/project-2aaa90a6-9ff2-437b-960f-e170f1a570de/output/output_article_2.csv' 
        AS row FIELDTERMINATOR ';'
    WITH row.article as article,
    row.cite AS cite,
    row["cite-label"] AS cite_label,
    row["editor"] AS editor
    return * LIMIT 30 ;
    '''

conn.query(query_string, db='neo4j')

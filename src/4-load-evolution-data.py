from utils import Neo4jConnection
import pandas as pd
import time
from tqdm import tqdm

##################################
# Global Variable
##################################
PROCESSED_DIR = "../data/processed/publications_processed_evolution.csv"
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")


def query_add_peer_review_group_details(df):
    print(f"Starting function to load peer review group details.")
    tic = time.perf_counter()
    df = df.reset_index()
    for df_index, row in tqdm(df.iterrows(), total=len(df)):
        group = row['review_group']
        for review_index, person in enumerate(row['reviewers'].split(",")):
            author = person
            review = row['reviews'].split(",")[review_index]
            decision = row['decisions'].split(",")[review_index]
            query = f'''
                MATCH (group:ReviewGroup {{group_id: toInteger({group})}})<-[r:IN_REVIEW_GROUP]-(reviewer:Author 
                {{name: "{author}"}})
                SET r.ReviewText="{review}"
                SET r.Decision="{decision}"
                    '''
            conn.query(query, db='neo4j')

    toc = time.perf_counter()
    print(f"Total time for query was: {toc-tic:0.4f} seconds\n")


def query_add_author_affiliation(df):
    print(f"\nStarting query to add affiliation to each author.")
    tic = time.perf_counter()
    df = df.reset_index()
    counter = 0
    for df_index, row in tqdm(df.iterrows(), total=len(df)):
        author_list = row['authors'].split(",")
        affiliation_list = row['authors_with_affiliations'].split(";")
        if len(author_list) == len(affiliation_list):
            for aff_index, affiliation in enumerate(affiliation_list):
                author = author_list[aff_index]
                query = f'''
                    MATCH (a:Author {{name: "{author}"}})
                    SET a.Affiliation="{affiliation}"
                        '''
                conn.query(query, db='neo4j')
        else:
            for author in enumerate(author_list):
                counter += 1
                query = f'''
                    MATCH (a:Author {{name: "{author}"}})
                    SET a.Affiliation= "Affiliation information not available"
                        '''
                conn.query(query, db='neo4j')

    toc = time.perf_counter()
    print(f"There were {counter} authors that did not have an affiliation added.")
    print(f"Total time for query was: {toc-tic:0.4f} seconds\n")

##################################
# Main Program Run
##################################

if __name__ == '__main__':
    print(f"\n**** Starting neo4j data evolution load ****\n")
    main_tic = time.perf_counter()

    df = pd.read_csv(PROCESSED_DIR)
    query_add_peer_review_group_details(df)
    query_add_author_affiliation(df)

    main_toc = time.perf_counter()
    print(f"*** Evolution load complete. Total time: {main_toc - main_tic:0.4f} seconds ****")
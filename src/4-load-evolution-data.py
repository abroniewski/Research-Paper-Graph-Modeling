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
    print(f"Total time was: {toc-tic:0.4f} seconds")

##################################
# Main Program Run
##################################

if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_DIR)
    query_add_peer_review_group_details(df)
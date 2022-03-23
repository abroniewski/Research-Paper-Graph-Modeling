import pandas as pd
from os.path import join
import configparser
from utils import Neo4jConnection
import time
from tqdm import tqdm


##################################
# Global Variable
##################################
# Here we add a local project import directory specific to each local neo4j instance
config = configparser.RawConfigParser()
config.read('local.config')
details_dict = dict(config.items('PROJECT_DIR'))
PROJECT_IMPORT_PATH = details_dict["dir_path"]
PROCESSED_DIR = "../data/processed/"
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")


##################################
# Create publication reviews
##################################

def generate_publication_review_data():
    """
    Creates a list of dummy data for reviews of a publication based
    on the length of the input dataframe. Because it is dummy data,
    it is not semantically correct. The reviewers are not chosen from
    the same pubication as that of the submitted journal, and there is
    a potential for a reviewer to be the author that wrote the paper.

    :param pd.DataFrame df:
    :return: pd.DataFrame

    """
    df = pd.read_csv("../data/processed/publications_processed.csv")
    list_of_reviews = []
    list_of_decisions = []
    for i in range(len(df)):
        reviews = []
        decision = []
        for h in range(3):
            reviews.append(f"This is review #{h+1} of the paper. It was a great read!")
            decision.append(f"reviewer #{h+1} has approved")
        list_of_reviews.append(reviews)
        list_of_decisions.append(decision)
    df["reviews"] = [','.join(map(str, l)) for l in list_of_reviews]
    df["decisions"] = [','.join(map(str, l)) for l in list_of_decisions]

    df.to_csv(join(PROCESSED_DIR, "publications_processed_evolution.csv"), index=False)
    df.to_csv(join(PROJECT_IMPORT_PATH, "publications_processed_evolution.csv"), index=False)
    return df


def create_review_group_unique_constraint():
    query_create_review_group_unique_constraint = '''
    CREATE CONSTRAINT ON (n:ReviewGroup) ASSERT n.group_id IS UNIQUE
    '''
    conn.query(query_create_review_group_unique_constraint, db='neo4j')


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
    df = generate_publication_review_data()
    create_review_group_unique_constraint()
    query_add_peer_review_group_details(df)
    query_add_author_affiliation(df)
import numpy as np
import pandas as pd
from random import choice, choices
from os.path import join
import configparser
import requests

##################################
# Global Variable
##################################
PROCESSED_DIR = "../data/processed/"
OUTPUT_FILE_PATH = "../data/processed/kaggle_v2.csv"

# Here we add a local project import directory specific to each local neo4j instance
config = configparser.RawConfigParser()
config.read('local.config')
details_dict = dict(config.items('PROJECT_DIR'))
PROJECT_IMPORT_PATH = details_dict["dir_path"]


##################################
# Create publication reviews
##################################

def create_publication_review(df):
    """
    Creates a list of dummy data for reviews of a publication based
    on the length of the input dataframe

    :param pd.DataFrame df:
    :return: pd.DataFrame

    """
    list_of_reviews = []
    list_of_decisions = []
    for i in range(len(df)):
        reviews = []
        decision = []
        for h in range(choice([1, 3, 5])):
            reviews.append("This is a review of the paper. It was a great read!")
            decision.append("approved")
        list_of_reviews.append(reviews)
        list_of_decisions.append(decision)
    df["reviews"] = [','.join(map(str, l)) for l in list_of_reviews]
    df["decision"] = [','.join(map(str, l)) for l in list_of_decisions]
    return df


##################################
# Main Program Run
##################################

if __name__ == '__main__':
    df = pd.read_csv("../data/processed/publications_processed.csv")

    df = create_publication_review(df)
    df.to_csv(join(PROCESSED_DIR, "publications_processed_evolution.csv"), index=False)

    # TODO: Remove this code below. Being used to load into local neo4j directory.
    df.to_csv(join(PROJECT_IMPORT_PATH, "publications_processed_evolution.csv"), index=False)
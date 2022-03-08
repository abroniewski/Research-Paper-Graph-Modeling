from neo4j import GraphDatabase
import logging
import sys
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
from random import choice
import csv
from os.path import join

##################################
# Global Variable
##################################
OUTPUT_FILE_PATH = "../data/processed/kaggle_v1.csv"

# This python script is used to intialize the database and create all nodes and edges

def set_index_as_article_number(df):
    """
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # Makes the index a column in df, which we can use as article_no
    df = df.reset_index()
    # We want to rename the index column, but since that is difficult (cuz I no Google)
    # we are copying index col to create a new article_no col
    df["article_no"] = df["index"]
    # Now we need to drop this index named col
    df = df.drop("index", axis=1)
    return df


def create_cited_by_column(df):
    """

    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # Way 1
    # df["cited_by"] = [ choice(range(len(df))) for i in range(len(df)) ]

    # Way 2 (more clear)
    list_of_cited_by = []
    for i in range(len(df)):
        # choice function randomly samples from the provided list
        list_of_cited_by.append( choice( df["article_no"] ) )

    df["cited_by"] = list_of_cited_by
    return df


if __name__ == '__main__':
    df = pd.read_csv("../data/raw/scopusBYUEngr17_21.csv")

    df = set_index_as_article_number(df)
    df = create_cited_by_column(df)

    df.to_csv(OUTPUT_FILE_PATH, index=False )

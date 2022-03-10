from typing import List, Any

import numpy as np
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
PROCESSED_DIR = "../data/processed/"
OUTPUT_FILE_PATH = "../data/processed/kaggle_v1.csv"

# This python script is used to intialize the database and create all nodes and edges

##################################
# Pre-process Columns
##################################
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


def extract_keyword_n_give_ids_to_them(df):
    """
    This function extract all the unique keywords from the dataset and gives them all a unique ID.
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # splits string using '|' separator
    keywords_list = []
    for keywords_str in df.index_keywords:
        try:
            if keywords_str is not np.nan:
                keywords_list.extend( keywords_str.split('|') )
        except Exception as err:
            print(f'error: {err}')
            print(keywords_str)
            break

    # kw_list = [kw.strip() for kw in keywords_list]
    kw_list: list[str] = []
    for kw in keywords_list:
        kw_list.append( kw.strip )
    unique_keywords_list = set(kw_list)
    df_kw = pd.DataFrame(unique_keywords_list, columns=["keyword"])
    df_kw = df_kw.reset_index()
    df_kw["keyword_id"] = df_kw["index"]
    df_kw = df_kw.drop("index", axis=1)
    # We assume here a csv of keyword -> id mapping is created.
    return df_kw


def maps_article_no_keyword_id(df, keywords_dict):
    """
    Trying to separate out keyword list and create a connection file for a specific article to keyword_id
    e.g. Article_no -> Keyword_id
    :param pd.DataFrame df:
    :param dict keywords_dict:
    :return:
    """
    list_of_references = []
    for _, row in df.iterrows():
        if row.index_keywords is np.nan:
            continue
        kw_list = row.index_keywords.split('|')
        kw_list = [kw.strip() for kw in kw_list]
        for kw in kw_list:
            print( keywords_dict[kw] )
            list_of_references.append((row.article_no, keywords_dict[kw]))

    # Now we can create CSV
    df_mapping = pd.DataFrame( list_of_references, columns=["article_no", "keyword_id"] )
    return df_mapping


if __name__ == '__main__':
    df = pd.read_csv("../data/raw/scopusBYUEngr17_21.csv")

    df = set_index_as_article_number(df)
    df = create_cited_by_column(df)

    df = extract_keyword_n_give_ids_to_them(df)
    df.to_csv(join(PROCESSED_DIR, "keywords.csv"), index=False)

    # we load that info in a dictionary
    keywords_dict = dict(zip(df.keyword, df.keyword_id))

    df = maps_article_no_keyword_id(df, keywords_dict)

    df.to_csv(join(PROCESSED_DIR, "keyword_mapping.csv"), index=False )




import numpy as np
import pandas as pd
from random import choice, choices
from os.path import join
import configparser

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
# Pre-process Data
##################################

def rename_dataset_variables(df):
    """
    Rename article to journal in column "document type"
    Rename conference paper to proceeding
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # rename columns to remove spaces, case and special characters
    df.rename(
        columns={'Authors': 'authors', 'Author(s) ID': 'authors_id', 'Title': 'paper', 'Year': 'publication_year',
                 'Source title': 'source_title', 'Volume': 'volume', 'Issue': 'issue', 'Art. No.': 'article_no',
                 'Cited by': 'cited_by', 'Author Keywords': 'author_keywords', 'Index Keywords': 'index_keywords',
                 'Document Type': 'document_type'}, inplace=True)
    df.loc[(df['document_type'] == "Article", 'document_type')] = "Journal"
    df.loc[(df['document_type'] == "Conference Paper", 'document_type')] = "Proceeding"
    df = df.drop(['Page start', 'Page end', 'Page count', 'DOI', 'Link', 'Affiliations', 'Authors with affiliations',
                  'Abstract', 'Publication Stage', 'Access Type', 'Source', 'EID'], axis='columns')
    return df


def set_index_as_article_number(df):
    """
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # Makes the index a column in df, which we can use as article_no
    df = df.reset_index()
    # We want to rename the index column, but since that is difficult (cuz I no want to Google)
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
        # will add a random number of citations (min:0, max:10)
        list_of_cited_by.append(choices(df["article_no"], k=choice(range(1, 10))))

    # this line of code adds the generated citations into the cited_by column
    # TODO: Adam needs to learn what the map function does and how this line works
    # Pulled from here on stack overflow:
    # https://stackoverflow.com/questions/45306988/column-of-lists-convert-list-to-string-as-a-new-column
    df["cited_by"] = [','.join(map(str, l)) for l in list_of_cited_by]
    return df


def extract_keyword_and_set_keyword_id(df):
    """
    This function extracts all the unique keywords from the dataset and gives them all a unique ID.
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """
    # splits string using ';' separator
    keywords_list = []
    for keywords_str in df.index_keywords:
        try:
            if keywords_str is not np.nan:
                keywords_list.extend(keywords_str.split(';'))
        except Exception as err:
            print(f'error: {err}')
            print(keywords_str)
            break

    # kw_list = [kw.strip() for kw in keywords_list]
    kw_list: list[str] = []
    kw_list = []
    for kw in keywords_list:
        kw_list.append(kw.strip().lower())
    unique_keywords_list = set(kw_list)

    df_kw = pd.DataFrame(unique_keywords_list, columns=["keyword"])
    df_kw = df_kw.reset_index()
    # We want to rename the index column, but since that is difficult (cuz I no want to Google)
    # we are copying index col to create a new article_no col
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
            print(keywords_dict[kw])
            list_of_references.append((row.article_no, keywords_dict[kw]))

    # Now we can create CSV
    df_mapping = pd.DataFrame(list_of_references, columns=["article_no", "keyword_id"])
    return df_mapping


def get_user_input_for_test_run():
    user_input = input("Do you want to create test data? (y/n)")
    if user_input == "y":
        input_csv = "../data/raw/scopusBYUEngr17_21.csv"
    else:
        input_csv = "../data/raw/scopusBYUEngr17_21-unedited.csv"
    return input_csv


##################################
# Main Program Run
##################################

if __name__ == '__main__':
    df = pd.read_csv(get_user_input_for_test_run())

    df = rename_dataset_variables(df)
    df = set_index_as_article_number(df)
    df = create_cited_by_column(df)

    df_kw = extract_keyword_and_set_keyword_id(df)
    df_kw.to_csv(join(PROCESSED_DIR, "keywords.csv"), index=False)

    # we load that info in a dictionary
    keywords_dict = dict(zip(df_kw.keyword, df_kw.keyword_id))

    # df = maps_article_no_keyword_id(df, keywords_dict)

    df.to_csv(join(PROCESSED_DIR, "publications_processed.csv"), index=False)

    # TODO: Remove this code below. Being used to load into local neo4j directory.
    df.to_csv(join(PROJECT_IMPORT_PATH, "publications_processed.csv"), index=False)

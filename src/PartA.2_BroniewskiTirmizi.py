
import numpy as np
import pandas as pd
from random import choice, choices
from os.path import join
import configparser
from utils import Neo4jConnection
import time

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

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="lab1ml")

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
                 'Document Type': 'document_type', 'Authors with affiliations': 'authors_with_affiliations'},
        inplace=True)
    df.loc[(df['document_type'] == "Article", 'document_type')] = "Journal"
    df.loc[(df['document_type'] == "Conference Paper", 'document_type')] = "Proceeding"
    df = df.drop(['Page start', 'Page end', 'Page count', 'DOI', 'Link', 'Affiliations',
                  'Abstract', 'Publication Stage', 'Access Type', 'Source', 'EID'], axis='columns')
    return df


def create_review_group(df):
    """
    Creates a list of dummy data for reviews of a publication based
    on the length of the input dataframe. Because it is dummy data,
    it is not semantically correct. The reviewers are not chosen from
    the same publication as that of the submitted journal, and there is
    a potential for a reviewer to be the author that wrote the paper.
    The review group is set to a unique id, in this case it is just
    copying the paper ID.

    :param pd.DataFrame df:
    :return: pd.DataFrame

    """
    list_of_reviewers = []
    list_of_reviewers_id = []
    for i in range(len(df)):
        reviewers = []
        reviewer_id = []
        for h in range(3):
            random_reviewer = choice(range(len(df)))
            reviewers.append(df["authors"][random_reviewer].split(', ')[0])
            reviewer_id.append(df["authors_id"][random_reviewer].split(';')[0])
        list_of_reviewers.append(reviewers)
        list_of_reviewers_id.append(reviewer_id)
    df["reviewers"] = [','.join(map(str, l)) for l in list_of_reviewers]
    df["reviewers_id"] = [','.join(map(str, l)) for l in list_of_reviewers_id]
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
    df["review_group"] = df["index"]
    # Now we need to drop this index named col
    df = df.drop("index", axis=1)
    return df


def create_cited_by_column(df):
    """
    :param pd.DataFrame df:
    :return: pd.DataFrame
    """

    list_of_cited_by = []
    for i in range(len(df)):
        # choice function randomly samples from the provided list
        # will add a random number of citations (min:0, max:10)
        list_of_cited_by.append(choices(df["article_no"], k=choice(range(1, 10))))

    # this line of code adds the generated citations into the cited_by column
    df["cited_by"] = [','.join(map(str, l)) for l in list_of_cited_by]
    return df


def extract_keyword_and_set_keyword_id(df):
    """
    Deprecated function.
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
    # we are copying index col to create a new article_no col
    df_kw["keyword_id"] = df_kw["index"]
    df_kw = df_kw.drop("index", axis=1)
    # We assume here a csv of keyword -> id mapping is created.
    return df_kw


def maps_article_no_keyword_id(df, keywords_dict):
    """
    Deprecated function.
    Trying to separate out keyword list and create a connection file for a specific article to
    keyword_id
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


def delete_all_existing_nodes():
    print(f"Deleting all existing nodes and edges.")
    tic = time.perf_counter()
    query_delete_all_existing_nodes = '''
        MATCH (n) DETACH DELETE n
    '''
    query_drop_keyword_constraint = '''
        DROP CONSTRAINT ON(n:Keyword) ASSERT n.keyword IS UNIQUE
        '''
    query_drop_author_constraint = '''
        DROP CONSTRAINT ON (n:Author) ASSERT n.name IS UNIQUE
        '''
    query_drop_paper_unique_constraint = '''
        DROP CONSTRAINT ON (n:Paper) ASSERT n.article_no IS UNIQUE
        '''

    conn.query(query_delete_all_existing_nodes, db='neo4j')
    conn.query(query_drop_keyword_constraint, db='neo4j')
    conn.query(query_drop_author_constraint, db='neo4j')
    conn.query(query_drop_paper_unique_constraint, db='neo4j')

    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def create_author_unique_contraint():
    query_create_unique_author_constraint = '''
    CREATE CONSTRAINT ON (n:Author) ASSERT n.name IS UNIQUE
    '''
    conn.query(query_create_unique_author_constraint, db='neo4j')


def create_paper_unique_constraint():
    # We will need to cycle through all of the papers for future queries. An index an paper will
    # significantly improve performance of all these future queries.
    query_create_unique_paper_constraint = '''
    CREATE CONSTRAINT ON (n:Paper) ASSERT n.article_no IS UNIQUE
    '''
    conn.query(query_create_unique_paper_constraint, db='neo4j')


def create_keyword_unique_constraint():
    query_create_keyword_unique_constraint = '''
    CREATE CONSTRAINT ON(n:Keyword) ASSERT n.keyword IS UNIQUE
    '''
    conn.query(query_create_keyword_unique_constraint, db='neo4j')


def create_author_paper_collection_year():
    print(f"Creating authors, papers, collections and years.")
    tic = time.perf_counter()

    query_create_author_paper_collection_year = '''
    // CREATE NODES FOR AUTHORS AND PAPERS + EDGES FOR CONTRIBUTION
    // This works by using LOAD CSV to connect to the locally available .csv in the default /import folder of neo4j
    // Using MERGE, we check to see is a node called "paper" already exists. If so, we will add the info, if not
    // we will create a new node
    // We then UNWIND the array of authors, and again use MERGE to create a node for each authoer (if it doesn't exist)
    // Finally, we create an edge connecting each author to the current paper
    // NOTE: Using MERGE allows us to make sure we are not creating duplicate nodes for an author that has contributed
    //   to multiple papers.
    // LEARNING: We cannot create labels for nodes or edges dynamically
    // LEARNING: trim() removes whitespace before and after
    // LEARNING: NEVER FORGET!!! You should be creating csv files for your nodes and your edges. Using pure CYPHER for
    // your loading is like using SQL on something that Python can to simply. It's not worth it.... Here we needed
    // to deal with multiple UNWINDs, resulting in CYPHER challenges we would not have encountered working in Python.

    LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
    MERGE (y:Year {year: toInteger(row.publication_year)})
    MERGE (collection:document_type {title:row.source_title, document_type:row.document_type})
    WITH y, collection, row
    MERGE (collection)-[:IN_YEAR]->(y)
    MERGE (p:Paper {name: row.paper, article_no: toInteger(row.article_no)})
    MERGE (p)-[:PUBLISHED_IN]->(y)
    MERGE (p)-[e:IN_COLLECTION]->(collection)
    MERGE (rg:ReviewGroup {group_id: toInteger(row.review_group)})
    MERGE (p)-[:REVIEWED_BY]->(rg)
    WITH p, row
    UNWIND split(row.authors, ',') AS author
    MERGE (a:Author {name: trim(author)})
    MERGE (a)-[r:CONTRIBUTED]->(p)
    '''
    conn.query(query_create_author_paper_collection_year, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def add_peer_review_group_authors():
    print(f"Creating peer review groups with authors.")
    tic = time.perf_counter()
    query_add_peer_review_group_authors = '''
        LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
        MATCH (rg:ReviewGroup {group_id: toInteger(row.review_group)})
        WITH row, rg
        UNWIND split(row.reviewers, ',') AS reviewer
        MATCH (a:Author {name: trim(reviewer)})
        CREATE (a)-[:IN_REVIEW_GROUP]->(rg)
    '''
    conn.query(query_add_peer_review_group_authors, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def update_document_type_node_labels():
    # To have the correct names for Proceeding and Journal nodes, we will use the previously
    # created node properties to set the label. This can be done easily with a few queries
    # because we have a small set of collection types. We start by setting an index on the
    # property "document_type" to improve performance as we will be cycling through properties
    # instead of nodes and relations. We then SET the node label for each type of collection we
    # have, and REMOVE the previous label and temporary "document_type" property.
    print(f"Updating document type node labels.")
    tic = time.perf_counter()

    query_update_proceeding_node_labels = '''
    MATCH (n:document_type {document_type:'Proceeding'})
    SET n:Proceeding
    REMOVE n:document_type
    REMOVE n.document_type
    '''
    query_update_journal_node_labels = '''
    MATCH (n:document_type {document_type:'Journal'})
    SET n:Journal
    REMOVE n:document_type
    REMOVE n.document_type
    '''
    query_update_other_node_labels = '''
    // Because this is the last node relabelling query being called, the only remaining nodes with this label
    // are those that have not already been renamed. These ones will all be named "Other".
    MATCH (n:document_type)
    SET n:Other
    REMOVE n:document_type
    REMOVE n.document_type
    '''

    conn.query(query_update_proceeding_node_labels, db='neo4j')
    conn.query(query_update_journal_node_labels, db='neo4j')
    conn.query(query_update_other_node_labels, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def create_citations_edges():
    print(f"Creating citation relationships.")
    tic = time.perf_counter()
    query_create_citations_edges = '''
    // CREATE CITATIONS
    // We will MATCH on existing papers where the article name is the same as the article name
    // for the incoming row of data. Once matched, we will UNWIND the array of citations
    // in the "cited_by" column. We then MATCH on nodes that have the same article_no as the
    // paper from where the citation is originating. The last WITH statement only calls our
    // two matched papers and adds a [CITED] edge between them.
    // NOTE: When we create or MERGE, anything that has not already been matched will be created
    //   as a new object. So we need to do all of our MATCHES before our MERGE and then we can pull
    //   in the found objects using their aliases.
        LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
        MATCH (p:Paper {name: row.paper})
        WITH p, row
        UNWIND split(row.cited_by, ',') AS cited_by
        MATCH (p2:Paper {article_no: toInteger(cited_by)})
        WITH p, p2
        MERGE (p)<-[r:CITED]-(p2)
        '''
    conn.query(query_create_citations_edges, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def create_keywords_from_index_nodes():
    # TODO: This keyword long is expensive. Can it be made faster by using a keyword index and matching on the index
    #   instead of on the string?
    print(f"Creating keywords.")
    tic = time.perf_counter()

    query_create_keywords_from_index_nodes = '''
    // LEARNING: when matching on indexes, always add toInteger as CSV LOAD reads everything in as a string.

        LOAD CSV WITH HEADERS FROM 'file:///publications_processed.csv' AS row FIELDTERMINATOR ','
        WITH row
        UNWIND split(row.index_keywords, ';') AS kw
        MERGE (k:Keyword {keyword: toLower( trim(kw) )})
        WITH row, k
        MATCH (p:Paper {article_no: toInteger(row.article_no)})
        MERGE (p)-[r:TOPIC]->(k)
        '''
    conn.query(query_create_keywords_from_index_nodes, db='neo4j')
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds\n")


def run_preprocess():
    df = pd.read_csv(get_user_input_for_test_run())

    print(f"\n**** Starting data pre-processing ****\n")
    preprocess_tic = time.perf_counter()

    df = rename_dataset_variables(df)
    df = create_review_group(df)
    df = set_index_as_article_number(df)
    df = create_cited_by_column(df)

    # Deprecated. Keyword extraction occurs directly in Cypher.
    # df_kw = extract_keyword_and_set_keyword_id(df)
    # df_kw.to_csv(join(PROCESSED_DIR, "keywords.csv"), index=False)
    # keywords_dict = dict(zip(df_kw.keyword, df_kw.keyword_id))
    # df = maps_article_no_keyword_id(df, keywords_dict)

    df.to_csv(join(PROCESSED_DIR, "publications_processed.csv"), index=False)
    df.to_csv(join(PROJECT_IMPORT_PATH, "publications_processed.csv"), index=False)
    preprocess_toc = time.perf_counter()
    print(f"*** Pre-processing complete. Total time: {preprocess_toc - preprocess_tic:0.4f} seconds ****")


def run_db_initialize():

    print(f"\n**** Starting neo4j database initialization ****\n")
    main_tic = time.perf_counter()

    delete_all_existing_nodes()
    create_author_unique_contraint()
    create_paper_unique_constraint()
    create_keyword_unique_constraint()
    create_author_paper_collection_year()
    add_peer_review_group_authors()
    update_document_type_node_labels()
    create_citations_edges()
    create_keywords_from_index_nodes()

    main_toc = time.perf_counter()
    print(f"*** Initialization Complete. Total time: {main_toc - main_tic:0.4f} seconds ****")

##################################
# Main Program Run
##################################

if __name__ == '__main__':

    run_preprocess()
    run_db_initialize()

import pandas as pd

df = pd.read_csv("../data/processed/dblp-to-csv/output_author.csv")
print(df.head(2000).to_csv("output_author_small.csv"))
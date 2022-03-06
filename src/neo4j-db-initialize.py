# This python script is used to intialize the database and create all nodes and edges

# link between python and Neo4j (Ismail)



# directory definition

processed_data_directory = "data/processed/dblp-to-csv"
ismail_directory = ""
adam_directory ="http://localhost:11001/project-b7855507-1cee-4692-8ff3-f3e64ffe6e1a"
#file location naming convention -> f"{name_directory}/output_school.csv"


# Authors and Citations (Adam)



LOAD CSV FROM f"{adam_directory}/output_school.csv" AS line
CREATE (:Artist {name: line[1], year: toInteger(line[2])})
# write Cypher query to create nodes and edges

# Python script for pre-processing checks




### Articles and Journals (Ismail)
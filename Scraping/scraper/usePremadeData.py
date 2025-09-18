from databaseConn import databaseConn
import pandas as pd

"""
The purpose of this file is to directly upload the csv of sample data to the database.
"""

with open("Sample.csv", "r") as file:
    content = pd.read_csv(file)

conn = databaseConn()
conn.sendData(content)
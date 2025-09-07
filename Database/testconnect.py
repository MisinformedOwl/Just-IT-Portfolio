"""
Just a simple script i was using to test if i could connect to the database during early production.
"""

import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="myuser",
    password="mypassword",
    database="mydb"
)

print("Connected:", conn.is_connected())
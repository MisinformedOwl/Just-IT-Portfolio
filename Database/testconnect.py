import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="myuser",
    password="mypassword",
    database="mydb"
)

print("Connected:", conn.is_connected())
from sqlalchemy import create_engine, text
import pandas as pd

class databaseConn:

    host = 'localhost'
    user = "myuser"
    password = "mypassword"
    database = "mydb"
    connected = False

    def __init__(self):
        """
        When the class starts establish the connection to the database.
        If it fails the connected flag will remain set to false.
        When it comes to inputting the data, if the flag is false it will eb send to a CSV instead.
        """
        try:
            self.engine = self.get_connection()
            print("Successfully connected to database")
            self.connected = True
        except Exception as ex:
            print(f"There was an error connecting, data will be sent to CSV file instead: {ex}")

    def get_connection(self):
        """
        Created the engine to interact with the database.

        Returns: The engine to interact with database.
        """
        return create_engine(url=f"mysql+pymysql://{self.user}:{self.password}@{self.host}:3307/{self.database}")
    
    def sendCommands(self, conn, data:pd.DataFrame):
        print("Starting transaction...")
        conn.execute(text("START TRANSACTION;"))

        for index, row in data.iterrows():
            pass

        print("Commiting to database...")
        conn.execute(text("COMMIT;"))

    def clearDuplicates(self, conn, data:pd.DataFrame):
        rowsToDrop = []
        for index, row in data.iterrows():
            res = conn.execute(text(f"SELECT count(1) FROM Job\
                                    WHERE URL = {row["URL"]}"))
            if res.scalar() == 1: #Collecting indexs of suplicates in the database
                rowsToDrop.append(index)
        
        data.drop(rowsToDrop,inplace=True)

        return data

    def sendData(self, data):
        if not self.connected:
            self.writeToCSV(data)
            return
        
        conn = self.engine.connect()
        print("Using database LinkedInScrape")
        conn.execute(text("USE LinkedInScrape;"))

        self.clearDuplicates(conn, data)
        self.sendCommands(conn, data)

    def writeToCSV(self, data):
        pass
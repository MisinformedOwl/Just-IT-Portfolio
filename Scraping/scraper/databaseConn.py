from sqlalchemy import create_engine, text
import pandas as pd
import datetime

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

        ### Returns
            The engine to interact with database.
        """
        return create_engine(url=f"mysql+pymysql://{self.user}:{self.password}@{self.host}:3307/{self.database}")
    
    def sendCommands(self, conn, data:pd.DataFrame):
        """
        This script is designed to start and end the transaction.

        ### Parameters
            conn: The connection to the database which is used to send SQL commands.
            data: The dataframe containing the collected content.
        """
        print("Starting transaction...")
        conn.execute(text("START TRANSACTION;"))

        for index, row in data.iterrows():
            pass # To be added when i have sql transaction code locked in.

        print("Commiting to database...")
        conn.execute(text("COMMIT;"))

    def clearDuplicates(self, conn, data:pd.DataFrame) -> pd.DataFrame:
        """
        This function clears the duplicates found in the frame.
        It detects duplicates by testing it's job code against the contents of the database.
        If the database count = 1. it's index is kept for a mass drop at the end.

        ### Parameters
            conn: The connection to the database, used to send SQL commands.
            data: the dataframe of collected content.
        
        ### Returns
            The dataframe with it's duplicates cleared.
        """
        rowsToDrop = []
        for index, row in data.iterrows():
            res = conn.execute(text(f"SELECT count(1) FROM Job\
                                    WHERE URL = {row["URL"]}"))
            if res.scalar() == 1: #Collecting indexs of suplicates in the database
                rowsToDrop.append(index)
        
        data.drop(rowsToDrop,inplace=True)

        return data

    def sendData(self, data: pd.DataFrame):
        """
        This is the starting script. 
        It is responcible for sending the data to the correct functions for processing. 
        And then initiating the sending of SQL insertion commands.

        ### Parameters
            data: The dataframe of content to be send to the SQL Server.
        """
        if not self.connected:
            self.writeToCSV(data)
            return
        
        conn = self.engine.connect()
        print("Using database LinkedInScrape")
        conn.execute(text("USE LinkedInScrape;"))

        self.clearDuplicates(conn, data)
        self.sendCommands(conn, data)

    def writeToCSV(self, data):
        """
        In the event the SQl server is unreachable the data is then stored in a CSV file so it is not lost and can be inserted at a later date.

        ### Parameters
            data: The dataframe of content.
        """
        data.to_csv(f"CollectedData {datetime.datetime.now().strftime("%Y/%m/%d")}.csv", index=False)
from sqlalchemy import create_engine, text
import pandas as pd
import datetime
import logging

class databaseConn:
    """
    This class is responcible for connecting to, 
    and interacting with the database once the data has been collected.
    """

    host = 'localhost'
    user = "myuser"
    password = "mypassword"
    database = "mydb"
    connected = False

    #===============================Insertion===========================================

    def __init__(self):
        """
        When the class starts establish the connection to the database.
        If it fails the connected flag will remain set to false.
        When it comes to inputting the data, if the flag is false it will eb send to a CSV instead.
        """
        logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    filename="Logs.log")
        self.logger = logging.getLogger("databaseConn")

        try:
            self.engine = self.get_connection()
            self.logger.info("Successfully connected to database")
            self.connected = True
        except Exception as ex:
            self.logger.warning(f"There was an error connecting, data will be sent to CSV file instead: {ex}")

    def get_connection(self):
        """
        Created the engine to interact with the database.

        ### Returns
            The engine to interact with database.
        """
        return create_engine(url=f"mysql+pymysql://{self.user}:{self.password}@{self.host}:3307/{self.database}")
    
    def insertJob(self, conn, row):
        """
        This function is responcible for inserting the data into the job table.
        Using what I have been told is industry standard methods.

        ### Parameters
            conn: The database connection which is sent commands.
            row: The current row in the dataframe which is being inserted.
        """
        jobInsertion = text("""
        INSERT INTO Job (Name, Business, Location, Salary, JobType, WorkType, Duration, URL) 
        VALUES (:name, :business, :location, :salary, :jobtype, :worktype, :duration, :url);
        """)

        conn.execute(jobInsertion, 
            {
            "name":     row.NameOfJob, \
            "business": row.NameOfBusiness, \
            "location": row.Location, \
            "salary":   row.Salary, \
            "jobtype":  row.JobType, \
            "worktype": row.WorkType, \
            "duration": row.Duration, \
            "url":      row.URL
            })

    def insertSkillLink(self,conn, row, id:int):
        """
        This is responsible for inserting the data into the linking table.
        This is ran after job insertion in order to get the job id.

        ### Parameters
            conn: the connection to the database which is sent commands.
            row: The current row being inserted.
            id: The job ID in the database.
        """

        skillInsert = text(
        """
        INSERT INTO SkillsLink (JobID, SkillID) VALUES ( :jobid , :skill );
        """
        )

        skillSelectID = text(
        """
        SELECT SkillID FROM Skills
        WHERE Skill = :skill;
        """
        )

        for skill in row.Skills:
            conn.execute(
                skillInsert,
                {
                    "jobid": id,
                    "skill": conn.execute(
                        skillSelectID,
                        {"skill": skill}
                    ).scalar()
                }
            )

    #==============================Prepping=============================================

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
        rowscurrently = data.shape[0]
        data.drop_duplicates(subset=['URL'], inplace=True)
        self.logger.info(f"Dropped {rowscurrently-data.shape[0]}")
        
        rowsToDrop = []
        for index, row in data.iterrows():
            findCommand = text(
            """
            SELECT count(1) FROM Job
            WHERE URL = :url;
            """
            )
            res = conn.execute(findCommand, {
                "url" : row.URL
            })
            if res.scalar() == 1: #Collecting indexs of suplicates in the database
                rowsToDrop.append(index)
        
        self.logger.info(f"Dropping {len(rowsToDrop)} duplicates from the dataframe.")
        data.drop(rowsToDrop,inplace=True)
        self.logger.info(f"{data.shape[0]} inserts remain.")

        return data

    def insertRows(self, conn, frame:pd.DataFrame):
        """
        Firstly, we will just insert the data for the Job table.
        This is because we need the jobID to be able to populate the linking table.

        ### Parameters
            conn: The engine usedto send commands to the SQl server.
            frame: The pandas dataframe containing a sample dataset.
        """
        for row in frame.itertuples(index=False):
            self.insertJob(conn,row)

            jobID = conn.execute(text("SELECT LAST_INSERT_ID();")).scalar()

            self.insertSkillLink(conn, row, jobID)

    def sendCommands(self, conn, data:pd.DataFrame):
        """
        This script is designed to start and end the transaction.

        ### Parameters
            conn: The connection to the database which is used to send SQL commands.
            data: The dataframe containing the collected content.
        """
        self.logger.info("Starting transaction...")
        conn.execute(text("START TRANSACTION;"))

        self.insertRows(conn, data)

        self.logger.info("Commiting to database...")
        conn.execute(text("COMMIT;"))

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
        conn.execute(text("USE LinkedInScrape;"))
        self.logger.info("Using database LinkedInScrape")

        self.clearDuplicates(conn, data)
        if data.shape[0] == 0:
            self.logger.warning("All data collected were duplicates.")
        self.sendCommands(conn, data)

    def writeToCSV(self, data:pd.DataFrame):
        """
        In the event the SQl server is unreachable the data is then stored in a CSV file so it is not lost and can be inserted at a later date.

        ### Parameters
            data: The dataframe of content.
        """
        try:
            data.to_csv(f"CollectedData {datetime.datetime.now().strftime("%Y/%m/%d")}.csv", index=False)
        except Exception as ex:
            self.logger.critical("CSV BACKUP FAILED. DATA LOST.")
            self.logger.critical(ex)

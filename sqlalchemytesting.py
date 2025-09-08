from sqlalchemy import create_engine, text, event
import pandas as pd

#=============================================================================================

host     = 'localhost'
user     = "myuser"
password = "mypassword"
database = "mydb"

#=============================================================================================

def get_connection():
    """
    Created the engine to interact with the database.

    Returns: The engine to interact with database.
    """
    return create_engine(url=f"mysql+pymysql://{user}:{password}@{host}:3307/{database}")

def executeTestCommands(conn):
    """
    This function just holds the test commands to be executed.
    First we use the database.
    """
    print("Using database")
    conn.execute(text("USE LinkedInScrape;"))
    print("Starting transaction")
    conn.execute(text("START TRANSACTION;"))
    print("Inserting skills")
    conn.execute(text("INSERT INTO Skills (Skill) VALUES ('TESTING');"))
    print("Commiting")
    conn.execute(text("COMMIT;"))



#frame = pd.DataFrame(columns=["NameOfJob", "NameOfBusiness", "Location", "JobType", "Salary", "Skills", "WorkType", "Duration", "URL"])

def insertJob(conn,row):
    """
    Thius function is responcible for inserting the data into the job table.
    Using what I have been told is industry standard methods.

    Parameters:
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

def insertSkillLink(conn, row, id):
    """
    This is responsible for inserting the data into the linking table.
    This is ran after job insertion in order to get the job id.

    Parameters:
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

def insertRows(conn,frame):
    """
    Firstly, we will just insert the data for the Job table.
    This is because we need the jobID to be able to populate the linking table.

    Parameters:
        frame: The pandas dataframe containing a sample dataset.
    """
    for row in frame.itertuples(index=False): # Apparently this is industry standard
        conn.execute(text("USE LinkedInScrape;"))

        insertJob(conn,row)

        jobID = conn.execute(text("SELECT LAST_INSERT_ID();")).scalar()

        insertSkillLink(conn, row, jobID)

def testInsertJobs(conn):
    """
    This function is responcible for creating a sample set of data to insert into the database for testing.
    it then begins the transaction and runs the insertion functions.
    Finally closing and commiting the data once finished.

    Parameters:
        conn: The connection to the database which is sent commands.
    """

    d = {
        'NameOfJob' : ["Data base analyst", "Programmer", "Junior Python dev"],
        'NameOfBusiness' : ["Samsung", "Google", "Apple"],
        'Location' : ["Jarrow", "London", "Stanford"],
        'JobType' : ["Data Analyst", "Software Engineer", "DevOps"],
        'Salary' : [20000,40000,2000],
        'Skills' : [["Python", "R"], ["C", "C++", "Python"], ["TensorFlow"]],
        'WorkType' : ["Remote", "On-site", "Hybrid"],
        'Duration' : ["Full Time", "Part Time", "Full Time"],
        'URL' : ["URL1", "URL2", "URL3"]
    }
    frame = pd.DataFrame(d)
    conn.execute(text("START TRANSACTION;"))
    insertRows(conn, frame)
    conn.execute(text("COMMIT;"))
    

#=============================================================================================

if __name__ == "__main__":
    try:
        engine = get_connection()
        conn = engine.connect()
        print("Successfully connected to database")
    except Exception as ex:
        print(f"There was an error connecting: {ex}")
        quit()
    

    #executeTestCommands(conn)
    testInsertJobs(conn)

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, 
 cursor, statement, params, context, executemany):
    if executemany:
        cursor.fast_executemany = True
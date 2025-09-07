from sqlalchemy import create_engine, text

#=============================================================================================

host = 'localhost'
user = "myuser"
password = "mypassword"
database = "mydb"

#=============================================================================================

def get_connection():
    return create_engine(url=f"mysql+pymysql://{user}:{password}@{host}:3307/{database}")

def executeTestCommands(conn):
    print("Using databse")
    conn.execute(text("USE LinkedInScrape;"))
    print("Starting transaction")
    conn.execute(text("START TRANSACTION;"))
    print("Inserting skills")
    conn.execute(text("INSERT INTO Skills (Skill) VALUES ('TESTING');"))
    print("Commiting")
    conn.execute(text("COMMIT;"))

#=============================================================================================

if __name__ == "__main__":
    try:
        engine = get_connection()
        print("Successfully connected to databse")
    except Exception as ex:
        print(f"There was an error connecting: {ex}")
        quit()
    
    conn = engine.connect()

    executeTestCommands(conn)
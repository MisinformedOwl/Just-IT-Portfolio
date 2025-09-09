from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import configparser
from time import sleep
from keyboard import is_pressed as pressed
import pandas as pd
import os
from keywords import findKWords as keywords
from databaseConn import databaseConn

#==============================================================================================================

content = {}

jobNames = ["Data Analyst", "Software Engineer", "Data Scientist"]

#==============================================================================================================

def setupSalary(button) -> int:
    """
    This function is responcible for processing the salary information
    As an example, linkedin salaries are displayed as £40k/yr - £45k/yr
    This should be a number for comparison aswell as using it for mathematical formulas in power BI

    ### parameters:
        Button: The html content which holds the salary data

    ### Returns
        The processed salary in the form of a integer.
    """
    daily = False
    text = button.text
    text = text.replace(text[0], "") #Remove whatever currency marker there is.
    text = text.replace("K", "000") # Transform the representation of thousands into the actual number.
    
    #Check if it's daily earnings
    if text.split(" ")[-1] == "daily":
        text.replace(" daily", "")
        daily = True
    else:
        text = text.replace(f"/{text.split("/")[-1]}", "")

    text = text.split(" - ")
    text = [int(text[0]), int(text[1])]

    if daily == True: # Looked up the average amount of days a data analyst works and used that to even out the daily value to be comparable to yearly.
        text = text*260
    
    return text[0] + int(text[1] - text[0])/2

def inputLogginDetails(driver):
    """
    This is where the user is logged in.
    Currently i am using my own account details which is stored in a config file.

    ### Parameters
        driver: The selenium driver used for navigation

    ### Returns
        The driver
    """
    config = configparser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

    sleep(5)
    print("Starting login.")

    search = driver.find_element(By.ID, "username")
    search.send_keys(config["Linkedin details"]["Name"])
    search = driver.find_element(By.ID, "password")
    search.send_keys(config["Linkedin details"]["Pass"])
    search.send_keys(Keys.RETURN)
    sleep(6)
    return driver

def checkSuccessfulLogin(driver):
    """
    This checks to see if the user has successfully logged in. If unsuccessful. 
    Stores the html file for examination.

    ### Parameters
        driver: The selenium driver used for navigation
    
    ### Returns
        The driver, or None if failed.
    """
    try:
        search = driver.find_element(By.XPATH, "//a[starts-with(@id, 'ember')]")
        print("No Issues")
        return driver
    except Exception:
        with open("html source Error.txt", "w") as file:
            file.write(driver.page_source)
        return None

def login(driver):
    """
    This is the hub where loggin in occours. Firstly, it inputs the details into the login page, then checks to see if it was successful.
    IF it was not successful, this function will return None.

    ### Parameters
        driver: The selenium driver used for navigation
    
    ### Returns
    # The driver, or None if failed.
    """
    print("Waiting for page to load before logging in")
    sleep(6)

    driver = inputLogginDetails(driver)

    driver = checkSuccessfulLogin(driver)
    
    return driver

def setupDevice():
    """
    This sets the basic configuration settings of the driver
    Including setting it to headless, and making sure the browser is recognised by Linked In to avoid being flagged for botting.

    ### Returns
        The selenium driver fully configured.
    """
    config = configparser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

    ops = Options()
    ops.add_argument("--headless")
    ops.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0")
    service = wd.FirefoxService(executable_path="/usr/local/bin/geckodriver")

    if config['Settings']['Debug'] == "True":
        print("Launching in debug mode.")
        driver = wd.Firefox()
    else:
        driver = wd.Firefox(service=service, options=ops)
    
    return driver

def navigateToJobs(driver):
    """
    This function is responcible for logging in and getting into position to scrape the data

    ### Parameters
        driver: The selenium driver used for navigation
    
    ### Returns
        The driver
    """
    driver.get("https://www.linkedin.com/login")
    driver = login(driver)

    if driver == None:
        print("Unsuccessful login. Cancelling todays operations to avoid account flagging.")
        quit()

    driver.get("https://www.linkedin.com/login")
    sleep(4)

    driver.get("https://www.linkedin.com/jobs/collections/recommended/")
    sleep(4)

    return driver

def collectName(driver, content: dict) -> dict:
    """
    This function is designed to collect the title of the job
    and put it into the content dictionary

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        A dictionary with the newly added content
    """
    name = driver.find_element(By.XPATH, f"//a[starts-with(@id, 'ember') and contains(@class, 'ember-view')]")
    content.update({"NameOfJob": [name.text]})
    return content

def collectBusiness(driver, content: dict) -> dict:
    """
    This fucntion collects the business name
    and inserts it into the dictionary.

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        A dictionary with the newly added content
    """
    name = driver.find_elements(By.XPATH, f"//div[@class='t-14' and @tabindex='-1']//a")[1]
    content.update({"NameOfBusiness" : [name.text]})
    return content

def collectLocation(driver, content: dict) -> dict:
    """
    This function collects the location of the job
    it also splits the data so that it collects the city in the UK.

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        A dictionary with the newly added content
    """
    loc = driver.find_element(By.XPATH, "//div[@class='t-14' and @tabindex='-1']//div[@class='job-details-jobs-unified-top-card__primary-description-container']")
    loc = loc.text.split(", ")
    content.update({"Location": [loc[0]]})
    return content

def collectJobType(job, content: dict) -> dict:
    """
    This fucntion inputs the job type which is being searched for into the dictionary.

    ### Parameters
        job (string): the current job type being searched for
    
    ###Returns
        A dictionary with the newly added content
    """
    content.update({"JobType" : [job]})
    return content

def collectSkills(driver, content: dict) -> dict:
    """
    This function collects the job description then sends it to an external script which i have made.
    If there was an issue with this job description during processing.
    It saves it in a file that gets overwritten to save space as an example to be examined.

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        A dictionary with the newly added content
    """
    jobDesc = driver.find_element(By.ID, "job-details")
    kw = keywords()
    try: # In the event that a description causes an error, write it in an error file so it can be tested directly in keywords.py
        skills = kw.detect(jobDesc.text)
        content.update({"Skills" : [skills]})
    except Exception as ex:
        print(f"Problem with job description, saving it to file for examination: {ex}")
        with open("ErrorDesc.txt", "w") as file:
            file.write(jobDesc.text)

    return content

def collectkeyDetails(driver, content: dict) -> dict:
    """
    On linked in the salary is bundled with 3 other pieces of information.
    The work duration (full-time)
    The work type (Remote)
    And of course the salary.

    What i found from examination was that duration always appeared. But also that the salary never appeared unless there was a work type.
    So to avoid having to examine each piece of information to check if it was the salary. I decided to work in reverse order as you can see in stages.

    If the salary is detected it is sent for processing in setupSalary.

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        a dictionary with the newly added content
    """
    buttons = driver.find_elements(By.XPATH, "//button[@class='artdeco-button artdeco-button--secondary artdeco-button--muted']//Strong")
    stages = ["Duration", "WorkType", "Salary"]
    buttons.reverse()
    for button, stage in zip(buttons, stages):
        if stage == "Salary":
            print("SALARY DETECTED")
            content.update({stage: setupSalary(button)})
            break

        content.update({stage: [button.text]})
    return content

def collectJobCode(driver, content: dict) -> dict:
    """
    This function collects the URL of the job, to use as a unique identifier for the database.
    It also needs to strip the url of it's usless content and just grab the "Currentjob" code.

    ### Parameters
        driver: The selenium web driver used to navigate the page.
        content: The dictionary of content to be added to the dataframe.
    
    ### Returns
        The content dictionary with more content
    """
    url = driver.current_url.split("=")[1]
    url = url.split("&")[0]
    content.update({"URL": url})
    return content

def insertDataIntoFrame(frame, content):
    """
    This function manages inserting the data into the pandas dataframe.
    By first creating a new frame to transform the data from dictionary to dataframe.
    It then uses concat as the original method of appending was depricated.

    ### Parameters
        content: The fully completed content to be inserted

    ### Returns
        The updated pandas dataframe.\
    """
    newframe = pd.DataFrame(content)
    frame = pd.concat([frame, newframe], ignore_index=True)
    return frame

def scrapeJobs(driver) -> pd.DataFrame:
    """
    This is the core script responcible for initially creating the dataframe and navigating over the jobs page.
    It then goes through every job in the list and collects the data and puts it into a dictionary,
    which is when inserted into the main dataframe.

    When the end of the page is finished, it selects the next page. Waits for it to load, and does it again.
    This is done for 10 pages per job. Until it's finally inserted into the database.

    ### Parameters
        driver: The selenium driver used to navigate
    """

    print("Creating dataframe")
    frame = pd.DataFrame(columns=["NameOfJob", "NameOfBusiness", "Location", "JobType", "Salary", "Skills", "WorkType", "Duration", "URL"])

    for job in jobNames:
        page = 1
        #Search in the search bar.
        try:
            navigation = driver.find_element(By.XPATH, "//input[starts-with(@id, 'jobs-search-box-keyword-id-ember')]")
            navigation.send_keys(job)
            navigation.send_keys(Keys.RETURN)
        except:
            print("CRITICAL ERROR: Unable to search for job type.")
            quit()
        sleep(3)
        while page < 10:
            page+=1
            try:
                scrollbar = driver.find_elements(By.TAG_NAME, "ul")[3]
                scrollbar = scrollbar.find_elements(By.XPATH, f"//li[starts-with(@id, 'ember')]")
            except Exception as ex:
                print("CRITICAL ERROR: Unable to locate scrollbar for jobs.")
            ammount = len(scrollbar)
            print(f"There are {ammount} of jobs displayed")
            for s in range(ammount):
                try:
                    scrollbar[s].click()
                except StaleElementReferenceException as ex:
                    print(f"Attempting to interact with a job that is uninteractable. Continuing with next job.")
                    continue
                sleep(1.4)
                content = dict()

                content = collectName(      driver, content)
                content = collectBusiness(  driver, content)
                content = collectLocation(  driver, content)
                content = collectJobType(      job, content)
                content = collectkeyDetails(driver, content)
                content = collectSkills(    driver, content)
                content = collectJobCode(   driver, content)

                sleep(1)

                #Being able to insert was depricated in 1.6. What is the point man.
                frame = insertDataIntoFrame(frame, content)
                del content
        
        try: # If it reaches the end, move onto next job type
            driver.find_element(By.XPATH, f"//button[@class='jobs-search-pagination__indicator-button ' and @aria-label='Page {page}']").click()
        except Exception as ex:
            print(f"{ex}")
            break
        
        sleep(1)
    return frame

#============================================================================================================

def emergencyCSVfileAdd(frame):
    """
    A temporary solution for saving the data as a csv file.
    """
    frame.to_csv("data.csv",index=False)

if __name__ == "__main__":
    driver = setupDevice()
    driver = navigateToJobs(driver)
    frame = scrapeJobs(driver)
    try:
        conn = databaseConn()
        conn.sendData(frame)
    except Exception as ex: #Incase something totally unforeseen happens, no data is lost.
        print(f"The exceptional happened: {ex}")
        emergencyCSVfileAdd(frame)
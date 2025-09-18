from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options


import configparser
from time import sleep
import pandas as pd
import os
from keywords import findKWords
from databaseConn import databaseConn
from ScrapeExceptions import AttemptFails, NullIndex
import logging
from random import random

#============================================Logger============================================================

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s',
                    filename="Logs.log")
logger = logging.getLogger("Scraper")

#======================================Selenium Navigation=====================================================

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

    sleep(4+random()*2)
    logger.info("Starting login.")

    search = driver.find_element(By.ID, "username")
    search.send_keys(config["Linkedin details"]["Name"])
    search = driver.find_element(By.ID, "password")
    search.send_keys(config["Linkedin details"]["Pass"])
    search.send_keys(Keys.RETURN)
    sleep(5+random()*2)
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
        logger.info("No Issues logging in")
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
        The driver, or None if failed.
    """
    logger.info("Waiting for page to load before logging in")
    actions = ActionChains(driver)
    actions.send_keys(Keys.F12).perform()
    sleep(5+random()*2)

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
    ops.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0")

    if config['Settings'].getboolean("Debug"):
        service = FirefoxService()
        logger.info("Launching in debug mode.")
    else:
        try:
            service = FirefoxService('/usr/local/bin/geckodriver')
        except Exception as ex:
            print(f"ERRROROR: {ex}")
        ops.add_argument('--headless')
        ops.add_argument('--no-sandbox')
        ops.add_argument('--disable-dev-shm-usage')
        ops.add_argument('--disable-gpu')
        ops.add_argument('--width=1920')
        ops.add_argument('--height=1080')
        ops.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0')
        ops.set_preference('dom.webdriver.enabled', False)
        ops.set_preference('useAutomationExtension', False)
        ops.set_preference("marionette.enabled", False)
        logger.info("Launched in production mode.")

    service.log_path = "geckodriver.log"
    service.log_level = "INFO"

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
        logger.critical("Unsuccessful login. Cancelling todays operations to avoid account flagging.")
        driver.quit()
        quit()

    driver.get("https://www.linkedin.com/login")
    sleep(3+random()*2)

    driver.get("https://www.linkedin.com/jobs/collections/recommended/")
    sleep(3+random()*2)

    return driver

#======================================Content Collection=======================================================

def setupSalary(text:str) -> int:
    """
    This function is responcible for processing the salary information
    As an example, linkedin salaries are displayed as £40k/yr - £45k/yr
    This should be a number for comparison aswell as using it for mathematical formulas in power BI

    ### parameters:
        text: The salary of the job as displayed.

    ### Returns
        The processed salary in the form of a integer.
    """
    daily = False
    monthly = False
    text = text.replace(text[0], "") #Remove whatever currency marker there is.
    text = text.replace("K", "000") # Transform the representation of thousands into the actual number.
    
    #Check if it's daily earnings

    text = text.split(" - ")

    for t in range(len(text)):
        if text[t].split(" ")[-1] == "daily":
            text[t] = text[t].replace(" daily", "")
            daily = True
        
        elif text[t].split(" ")[-1] == "monthly":
            text[t] = text[t].replace(" monthly", "")
            daily = True
        else:
            text[t] = text[t].replace(f"/{text[t].split("/")[-1]}", "")

    #Check for any .5's
    for t in range(len(text)):
        text[t].replace(",","")
        if text[t].__contains__("."):
            text[t] = text[t].replace(".", "")
            text[t] = text[t][:-1]

    if len(text) > 1:
        text = [int(text[0]), int(text[1])]
    else:
        text = [int(text[0])]

    if daily: # Looked up the average amount of days a data analyst works and used that to even out the daily value to be comparable to yearly.
        text = text*260
    elif monthly:
        text = text*12
    
    if len(text) > 1:
        return text[0] + int(text[1] - text[0])/2
    else:
        return text[0]

def collectName(driver, content: dict) -> dict:
    """
    This function is designed to collect the title of the job
    and put it into the content dictionary

    ### Parameters
        driver: The selenium driver used in navigation
    
    ### Returns
        A dictionary with the newly added content
    """

    name = driver.find_element(By.XPATH, f"//div[@class='t-14' and @tabindex='-1']//h1[@class='t-24 t-bold inline']")
    print(name.text)
    content.update({"NameOfJob": [name.text[:50]]}) # 50 is the column limit
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
    name = driver.find_elements(By.XPATH, f"//div[@class='t-14' and @tabindex='-1']//div[@class='job-details-jobs-unified-top-card__company-name']")[0]
    nametext = name.text.replace("\n", " ")
    print(nametext[:50])
    content.update({"NameOfBusiness" : [nametext[:50]]})
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
    try:
        loc = driver.find_elements(By.XPATH, "//div[@class='t-14' and @tabindex='-1']//div[@class='job-details-jobs-unified-top-card__primary-description-container']//span[@class='tvm__text tvm__text--low-emphasis']")[0]
    except Exception as ex:
        logger.critical(f"This critical error occoured when looking for a location: {ex}")
    loc = loc.text.split(", ")
    loc = loc[0]
    content.update({"Location": [loc]})
    print(f"location: {loc}")
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
    try: # In the event that a description causes an error, write it in an error file so it can be tested directly in keywords.py
        skills = keyWords.detect(jobDesc.text)
        content.update({"Skills" : [skills]})
    except Exception as ex:
        logger.warning(f"Problem with job description, saving it to file for examination: {ex}")
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

    if len(buttons) == 0: # I cant believe i've found one that doesn'thave any buttons...
        content.update({"WorkType" : ["empty"], "Salary" : [0], "Duration" : ["Non specified"]})
        return content

    if buttons[-1].text[-5:].lower() == "match": # Sometimes it shows skills match on new accounts that have not been calibrated to
        buttons = buttons[:-1]
    stages = ["Duration", "WorkType", "Salary"]
    buttons.reverse()

    for button, stage in zip(buttons, stages):
        if stage == "Salary" or button.text[0] == "£" or button.text[0] == "$":
            content.update({stage: [setupSalary(button.text)]})
            break
        content.update({stage: [button.text]})

    if len(buttons) == 1: # Only Duration
        content.update({"WorkType" : ["empty"], "Salary" : [0]}) # Need to use empty to prevent crashes when uploading to database.
    elif len(buttons) == 2: # Missing Salary
        content.update({"Salary" : [0]})
    
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
    print(url)
    content.update({"URL": url})
    return content

#=======================================Looking Over Jobs=====================================================

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

def scrollJobs(driver, scrollitems:list, scrollbar, index):
    """
    This function is desgiend to manage scrolling jobs.
    Originally it was part of the main script,
    however due to the errors attempting to be caught here.
    I need to escape 2 loops, therefore throwing exceptions back up the chain is the best solution here.

    ### Parameters:
        driver: The selenium driver for navigation
        scollitems: A list of jobs in the form of html elements
        scrollbar: The container containing the jobs
        index: The current scroll index
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView();", scrollitems[index])
        sleep(0.5+random()*2)
        scrollitems[index].click()
    except StaleElementReferenceException as ex:
        raise NullIndex("Null index discovered", index)
    except IndexError:
        logger.warning("Reaching for jobs that dont exist. Moving to next page...")
        moveOn = True
        raise IndexError
    except Exception as ex:
        logger.warning(f"Unexpected exception occoured: {ex}")
        raise Exception
    
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
    jobNames = ["Data Analyst", "Software Engineer", "Data Scientist", "Machine Learning Engineer"]
    logger.info("Creating dataframe")
    frame = pd.DataFrame(columns=["NameOfJob", "NameOfBusiness", "Location", "JobType", "Salary", "Skills", "WorkType", "Duration", "URL"])

    for job in jobNames:
        page = 1
        #Search in the search bar.
        try:
            navigation = driver.find_element(By.XPATH, "//input[starts-with(@id, 'jobs-search-box-keyword-id-ember')]")
            navigation.clear()
            navigation.send_keys(job)
            navigation.send_keys(Keys.RETURN)
        except:
            logger.critical("Unable to search in search bar")
            driver.quit()
            quit()
        logger.info(f"Collecting from {job}")
        sleep(2+random()*2)
        totalJobs = 0
        while page <= 9:
            logger.info(f"Page {page}")
            page+=1
            try:
                scrollbar = driver.find_element(By.CLASS_NAME, "scaffold-layout__list ")
                scrollitems = scrollbar.find_elements(By.XPATH, f"//li[starts-with(@id, 'ember')]")
            except NoSuchElementException as ex:
                logger.critical("Unable to locate scrollbar for jobs.")
                driver.quit()
                quit()
            except Exception as ex:
                logger.critical(f"Unknown critical error: {ex}")
            
            amount = len(scrollitems)
            totalJobs += amount
            logger.info(f"There are {amount} of jobs displayed")
            if amount > 25:
                logger.warning("There are anomalous results.")
            for s in range(amount):
                try:
                    scrollbar = driver.find_element(By.CLASS_NAME, "scaffold-layout__list ")
                    scrollitems = scrollbar.find_elements(By.XPATH, f"//li[starts-with(@id, 'ember')]")
                    scrollJobs(driver,scrollitems, scrollbar, s)
                except IndexError as ex:
                    break
                except AttemptFails as attempts:
                    logger.warning(f"Ran out of attempts to find stale element after {attempts.attempts} attempts")
                    break
                except NullIndex as nullindex:
                    logger.warning(f"Found an anomalous result moving onto the next...")
                    continue
                except Exception as ex:
                    logger.critical(f"Unexpected error caught: {ex}")

                sleep(1+random()*2)
                content = dict()

                content = collectJobCode(   driver, content)
                content = collectName(      driver, content)
                content = collectBusiness(  driver, content)
                content = collectLocation(  driver, content)
                content = collectJobType(      job, content)
                content = collectkeyDetails(driver, content)
                content = collectSkills(    driver, content)

                sleep(1+random()*2)

                #Being able to insert was depricated in 1.6. What is the point man.
                frame = insertDataIntoFrame(frame, content)
                del content
        
            try: # If it reaches the end, move onto next job type
                scrollbar = driver.find_element(By.CLASS_NAME, "scaffold-layout__list ")
                scrollbar = scrollbar.find_elements(By.TAG_NAME, "div")[0]
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollbar)
                driver.find_element(By.XPATH, f"//button[@class='jobs-search-pagination__indicator-button ' and @aria-label='Page {page}']").click()
            except Exception as ex:
                logger.warning(f"Problem with selecting new page: {ex}")
                logger.warning(f"Going by link instead...")
                try:
                    driver.get(f"https://www.linkedin.com/jobs/search/?keywords={job}&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true&start={totalJobs+2}") #+2 to ensure im in the next page.
                    sleep(2+random()*2)
                except Exception as ex:
                    logger.critical(f"A new error occoured when going through the link... {ex}")
        
        sleep(1+random()*2)
    return frame

#=================================Data Insertion & Main=======================================================

def emergencyCSVfileAdd(conn, frame):
    """
    A temporary solution for saving the data as a csv file.
    """
    try:
        logger.info("Data loaded into csv file")
        conn.writeToCSV(frame)
    except Exception as ex:
        logger.critical("Total failure to input data.")
        raise AttemptFails

try:
    keyWords = findKWords()
except FileNotFoundError as ex:
    logger.critical("Key words file was not found. Please create a new one or ensure it's in the correct location next to keywords.py")
    quit()
except Exception as ex:
    logger.critical(f"Unknown error occoured: {ex}")
    quit()


if __name__ == "__main__":
    driver = setupDevice()
    driver = navigateToJobs(driver)
    frame = scrapeJobs(driver)
    try:
        conn = databaseConn()
        conn.sendData(frame)
        logger.info("Successfully added data to database!")
    except AttemptFails as ex:
        driver.quit()
        quit()
    except Exception as ex: #Incase something totally unforeseen happens, no data is lost.
        logger.warning(f"An issue occoured when uploading to the database.")
        emergencyCSVfileAdd(conn, frame)
    driver.quit()
    quit()

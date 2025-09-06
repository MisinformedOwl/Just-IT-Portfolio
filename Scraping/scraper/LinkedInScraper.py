from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import configparser
from time import sleep
from keyboard import is_pressed as pressed
from keyboard import wait
import pandas as pd
import os
from keywords import findKWords as keywords

content = {}

jobNames = ["Data Analyst", "Software Engineer", "Data Scientist"]

#==============================================================================================================

def setupSalary(button) -> int:
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

def Login():
    print("Waiting for page to load before logging in")
    sleep(6)
    print("Starting.")
    search = driver.find_element(By.ID, "username")
    search.send_keys(config["Linkedin details"]["Name"])
    search = driver.find_element(By.ID, "password")
    search.send_keys(config["Linkedin details"]["Pass"])
    search.send_keys(Keys.RETURN)
    sleep(6)

    try:
        search = driver.find_element(By.XPATH, "//a[starts-with(@id, 'ember')]")
        print("No Issues")
    except Exception:
        with open("html source Error.txt", "w") as file:
            file.write(driver.page_source)
            return None
    
    return driver

#============================================================================================================

#%% Config
config = configparser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

#%% Driver

ops = Options()
ops.add_argument("--headless")
ops.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0")
service = wd.FirefoxService(executable_path="/usr/local/bin/geckodriver")
if config['Settings']['Debug'] == "True":
    print("Launching in debug mode.")
    driver = wd.Firefox()
else:
    driver = wd.Firefox(service=service, options=ops)
driver.get("https://www.linkedin.com/login")

while driver != None:
    driver = Login()
    sleep(10)

sleep(4)

driver.get("https://www.linkedin.com/jobs/collections/recommended/")

sleep(4)

page = 1

print("Creating dataframe")
frame = pd.DataFrame(columns=["NameOfJob", "NameOfBusiness", "Location", "JobType", "Salary", "Skills", "WorkType", "Duration", "URL"])

for job in jobNames:
    #Search in the search bar.
    navigation = driver.find_element(By.XPATH, "//input[starts-with(@id, 'jobs-search-box-keyword-id-ember')]")
    navigation.send_keys(job)
    navigation.send_keys(Keys.RETURN)
    sleep(3)
    while page < 10:
        page+=1
        scrollbar = driver.find_elements(By.TAG_NAME, "ul")[3]
        scrollbar = scrollbar.find_elements(By.XPATH, f"//li[starts-with(@id, 'ember')]")
        ammount = len(scrollbar)
        print(f"There are {ammount} of jobs displayed")
        for s in range(ammount):
            scrollbar[s].click()
            
            sleep(1.4)
            
            content = dict()
            #Go over all of the
            #Name
            name = driver.find_element(By.XPATH, f"//a[starts-with(@id, 'ember') and contains(@class, 'ember-view')]")
            content.update({"NameOfJob": [name.text]})
            del name

            #Name of the business
            name = driver.find_elements(By.XPATH, f"//div[@class='t-14' and @tabindex='-1']//a")[1]
            content.update({"NameOfBusiness" : [name.text]})
            del name

            #Location
            loc = driver.find_element(By.XPATH, "//div[@class='t-14' and @tabindex='-1']//div[@class='job-details-jobs-unified-top-card__primary-description-container']")
            loc = loc.text.split(", ")
            content.update({"Location": [loc[0]]})
            del loc

            #Type
            content.update({"JobType" : [job]})

            #Salary
            buttons = driver.find_elements(By.XPATH, "//button[@class='artdeco-button artdeco-button--secondary artdeco-button--muted']//Strong") #-= This needs to be cleaned up so it holds the extra information. Back to front
            stages = ["Duration", "WorkType", "Salary"]
            buttons.reverse()
            for button, stage in zip(buttons, stages):
                if stage == "Salary":
                    print("SALARY DETECTED")
                    content.update({stage: setupSalary(button)})
                    break

                content.update({stage: [button.text]})
            del buttons
            del stages

            #Skills
            jobDesc = driver.find_element(By.ID, "job-details")
            kw = keywords()
            
            try: # In the event that a description causes an error, write it in an error file so it can be tested directly in keywords.py
                skills = kw.detect(jobDesc.text)
                content.update({"Skills" : [skills]})
            except Exception:
                with open("ErrorDesc.txt", "w") as file:
                    file.write(jobDesc.text)
            
            del jobDesc
            
            #URL
            content.update({"URL", driver.current_url})
            sleep(1)

            #Being able to insert was depricated in 1.6. What is the point man.
            newframe = pd.DataFrame(content)
            frame = pd.concat([frame, newframe], ignore_index=True)
            print(frame.head(25))
            del content
            
            if pressed("q"):
                break
            sleep(0.6)
        
        if pressed("q"):
            break
    
    
    try:
        driver.find_element(By.XPATH, f"//button[@class='jobs-search-pagination__indicator-button ' and @aria-label='Page {page}']").click()
    except Exception:
        break
    
    sleep(1)
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import configparser
from time import sleep
from keyboard import is_pressed as pressed
import pandas as pd
from keywords import findKWords as keywords
import sys

content = {}

jobNames = ["Data Analyst", "Software Engineer", "Programmer", "Data Scientist"]

def Login():
    print("Waiting for page to load before logging in")
    sleep(6)
    print("Starting.")
    search = driver.find_element(By.ID, "username")
    search.send_keys(config["Linkedin details"]["Name"])
    search = driver.find_element(By.ID, "password")
    search.send_keys(config["Linkedin details"]["Pass"])
    search.send_keys(Keys.RETURN)
    sleep(3)
    
    try:
        search = driver.find_element(By.XPATH, "//a[starts-with(@id, 'ember')]")
        print("No captcha")
    except Exception:
        input("Waiting for clearance")
    
    return driver

#%% Config
config = configparser.RawConfigParser()
config.read("config.ini")

#%% Driver

ops = Options()
ops.add_argument("--headless")

driver = wd.Firefox(options=ops)
driver.get("https://www.linkedin.com/login")

driver = Login()

sleep(2)

driver.get("https://www.linkedin.com/jobs/collections/recommended/")

sleep(3)

page = 1

print("Creating dataframe")
frame = pd.DataFrame(columns=["NameOfJob", "Location", "JobType", "Salary", "Skills"])

for job in jobNames:
    #Search in the search bar.
    navigation = driver.find_element(By.XPATH, "//input[starts-with(@id, 'jobs-search-box-keyword-id-ember')]")
    navigation.send_keys(job)
    navigation.send_keys(Keys.RETURN)
    sleep(2)
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

            #Location
            loc = driver.find_element(By.XPATH, "//div[@class='t-14' and @tabindex='-1']//div[@class='job-details-jobs-unified-top-card__primary-description-container']//span[@class='tvm__text tvm__text--low-emphasis']")
            loc = loc.find_elements(By.XPATH, "//span[contains(@class, 'tvm__text tvm__text--low-emphasis')]")[0]
            content.update({"Location": [loc.text]})
            del loc

            #Type
            content.update({"JobType" : [job]})
            
            #Salary
            salary = driver.find_elements(By.XPATH, "//button[@class='artdeco-button artdeco-button--secondary artdeco-button--muted']//Strong")[0] #-= This needs to be cleaned up so it holds the extra information. Back to front
            content.update({"Salary": [salary.text]})
            del salary

            #Skills
            jobDesc = driver.find_element(By.ID, "job-details")
            kw = keywords()
            
            try: # In the event that a description causes an error, write it in an error file so it can be tested directly in keywords.py
                skills = kw.detect(jobDesc.text)
            except Exception:
                with open("ErrorDesc.txt", "w") as file:
                    file.write(jobDesc.text)

            content.update({"Skills" : [skills]})
            del jobDesc
            sleep(1)

            #Being able to insert was depricated in 1.6. What is the point man.
            newframe = pd.DataFrame(content)
            frame = pd.concat([frame, newframe], ignore_index=True)
            print(frame.head())
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

#%%

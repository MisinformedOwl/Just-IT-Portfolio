# Just IT Portfolio Project

## The Linked In Scraping Tool 

When i first left university I of course started looking for jobs. However what i found was that many of those jobs required skills which were not taught in university. Docker, node.js etc. This was the first time i had heard about these tools. Therefore, I applied my knowledge of python. To do a bit of problem solving.

[I scraped](https://github.com/MisinformedOwl/LinkedInMissingSkills) the recommended jobs page of linked in, and acquired all of the missing skills. Once i believe i had scraped enough, i would end the process. Where it would then rank the skills from the most in demand to the least (It was node.js). This allowed me to confidently plan ahead for what skills i am missing.

Since then i took on a bootcamp at Just-IT which taught me a variety of new tools such as tableu and power BI. However, it also taught me more about Azure and databases. Which is where this project focuses.

## Aim of the project
This project looks to do similar to the previous linked in scraper, however. Instead of simply collecting missing skills, it will collect a much more broad range of data such as the job title. The business' name as well as What the salary is in the form of a number.

Now, for those who clicked on the link, you will have noticed that the previous repo is now out of commision. This is because linked in has changed how they organise the job page. And instead of displaying the missing skills there in the job. They require you to use their built in AI to find what skills you are missing. So to solve this problem i decided to simply take the job description, tokenise the content and then find the keywords myself as can be found in [keywords.py](https://github.com/MisinformedOwl/Just-IT-Portfolio/blob/main/Scraping/scraper/keywords.py)

## The Database
To host the database i started by creating a docker container. This will be what hosts it locally, however this image will be uploaded to azure so that the database can remain up and available.

The database has a fairly simply schema to it.

![Image](https://media.discordapp.net/attachments/184325486422392843/1418191246677119046/image.png?ex=68cd3905&is=68cbe785&hm=ca5386ae452755d0a936673495d8d82d1b4874bb835ae3ae71dcbc483f9e0cf5&=&format=webp&quality=lossless)

## Why like this?
Well i wish i could have had 1 table, it would have made my life certainly alot easier. However, many jobs can have many skills  and vice versa. It had created a many to many connection. Prompting me to use a linking table.

For the [full database setup script](https://github.com/MisinformedOwl/Just-IT-Portfolio/blob/main/Database/01-setup.sql) Simply click this link.

## How to run it

Well, it's actually extreamly simple to run...

## Installation

Firstly clone this repository by downloading the files. After unpacking the files in a directory of your choosing ensure you have at minimum python 3.12.10.

After completing this step, you will also need to ensure firefox is installed on your computer. 

Also ensure you have docker installed, as otherwise you will not be able to make use of the MySQL database.

Finally after all of this is installed. Make sure you have all of the required libraries by using this command.

```
pip install -r requirements.txt
```

This will download all requirements at once.

## Running

### Demo

There is a demo available using pre collected data.

firstly open a console and navigate into the database file. Then, enter the command

```
docker-compose up --build
```

This will launch the database locally and build the tables aswell as populate the skills table with all tracked skills.

Next open a new console and navigate to Scraping/scraper file and run the command

```
python usePremadeData.py
```

This will insert the sample.csv data into the database for use in applications such as power BI. However should you wish to connect directly to the database to use sql commands simply run the command...

```
docker exec -it database-database-1 mysql -umyuser -pmypassword mydb
```

### MAKE SURE TO TYPE use LinkedInScrape; ONCE INSIDE

For power BI you simply get data from other source and then select MySQL. Then enter the details...

```
localhost:3307

LinkedInScrape
```

you may need to enter your details too. The default for this is 

```
username: myuser

password: mypassword
```

Im well aware this is insecure however this is purely for demonstration purposes.

### Running the real thing

So, assuming you will be using your local database and not the one i host on Azure as that will be removed by the 17th of october.

You will first need to with docker open the database by again, navigating to the Database file and typing in

```
docker-compose up --build
```

Next, in another console navigate to Scraping/Scraper and enter the config.ini file.

Enter your linked in details, or whatever linked in account details you have and make sure debug is set to true. When debug is not set to true you will not be able to see the process of the scraper.

Once this is done, simply use the command

```
python LinkedInScraper.py
```

kick back and relax as it collects the linked in content on your recommended jobs pages.

This process can take quite a while, this is by design to simulate human interaction so it's less likely to be caught.

But once this is finished, you will find that your database is populated. If there was an issue at all when commiting to the database, there is a failsafe to create a csv file instead. Which you can then upload by using the demo method.

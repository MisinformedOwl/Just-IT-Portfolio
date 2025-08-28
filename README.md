# Currently broken
Linked in has changed the way they have done things. In the process of fixing.

# LinkedInMissingSkills
Webscraping application using selenium to find out what skills you are missing.

## Setup
You will need to be able to use pip. I recommend installing anaconda. It's a good environment management source. and it gives you all the tools needed.

In the project files there is a requirement.txt file. To install the requirements type in the below in a command console whilst being in the correct directory.

```
pip install -r requirements.txt
```

## Using the script.
You must enter your account details in the config.ini file, this allows the script to log in and check your recommended jobs.

After you do this. Simply type

```
python WhatAmIMissing.py
```

And the application will open a webbrowser and go through linked in. Easy.

In the event a captcha appears, the program should stop itself and wait until you hit enter on the console.

import os

class findKWords:
    kWords = set()
    punctuation = set([".", ",", ";", ":", "@", "'", "#", "~", "{", "}", "[", "]", "-", "_", "!", "*", "^", "(", ")", "&", "%", '"', "\n"])
    def __init__(self):
        self.kWords = self.getKeyWords()

    def cleanData(self, tokens: list[str]) -> list:
        for t in range(len(tokens)):
            if len(tokens[t]) < 1 or tokens[t] == "\n":
                continue
            tokens[t].lower()   #Decapitalise
            tokens[t].lstrip()  #Remove white space on the left
            tokens[t].rstrip()  #Remove white space on the right
            if len(tokens[t]) <= 1:
                continue
            if tokens[t][-2:] == "\n":
                tokens = tokens[t][:-1]
            if tokens[t][0] in self.punctuation:
                tokens[t] = tokens[t][1:]
            if tokens[t][-1] in self.punctuation:
                tokens[t] =tokens[t][:-1]  #If theres a comma or a full stop at the end remove it.
        return tokens


    def getKeyWords(self) -> set:
        with open(os.path.join(os.path.dirname(__file__), "keywords.txt"), "r") as file:
            words = file.readline().lower().split(",")
            words[-1] = words[-1][:-1]
        return words

    def detect(self, words) -> list:
        #Get tokens for the job description
        words = words.lower()
        tokens = words.split(" ")
        tokens = self.cleanData(tokens)
        p1,p2= 0,1
        keywordsFound = set()
        #print("KEYS")
        for x in range(1,len(tokens)+1):
            for y in range(3):
                #firstly we merge the words so they can be compared
                key = " ".join(tokens[x:x+y])
                if key in self.kWords:
                    #print(f"KEYWORD IN KEY: {key}")
                    keywordsFound.add(key)
        
        return list(keywordsFound)

data = """About the job
This job is sourced from a job board.

Data Analyst

Peterborough, UK

This role supports the operational performance of the production plant by delivering actionable insights, streamlining data processes, and enabling data-driven decision-making across manufacturing, quality, maintenance, and continuous improvement functions.

Main Responsibilities

    Monitor and analyze key operational metrics (e.g., OEE, downtime, scrap rates, throughput) to identify trends and improvement opportunities.
    Develop and maintain real-time dashboards and reports to support production management and shift leaders.
    Collaborate with operations, engineering, and maintenance teams to identify root causes of performance issues and support corrective actions.
    Automate data collection and reporting processes using tools such as Power BI, SQL, or Python.
    Support continuous improvement initiatives (Lean, Six Sigma) with data analysis and visualization.
    Conduct variance analysis on production output, labor utilization, and equipment performance.
    Provide ad hoc analysis to support operational decision-making and strategic planning.

Candidate Profile

    Advanced Excel and intermediate Power BI
    Strong analytical thinking, attention to detail, and ability to communicate insights to non-technical stakeholders.
    Bachelor's degree in Data Analytics, Industrial Engineering, Operations Management, or related field.
    Familiarity with SQL queries, MES/SCADA systems and SAP ERP systems.

Company

At McCormick, we bring our passion for flavor to work each day. We encourage growth, respect everyone's contributions and do what's right for our business, our people, our communities and our planet. Join us on our quest to make every meal and moment better.

Founded in Baltimore, MD in 1889 in a room and a cellar by 25-year-old Willoughby McCormick with three employees, McCormick is a global leader in flavour. With over 14,000 employees around the world and more than $6 Billion in annual sales., the Company manufactures, markets and distributes spices, seasoning mixes, condiments and other flavourful products to the entire food industry, retail outlets, food manufactures, food service businesses and consumers.

While our global headquarters are in the Baltimore, Maryland, USA area, McCormick operates and serves customers from nearly 50 locations in 27 countries and 135 markets in Asia-Pacific, China, Europe, Middle East and Africa, and the Americas, including North, South and Central America with recognized brands including Schwartz.

At McCormick, we have over a 100-year legacy based on our Power of People principle. This principle fosters an unusually dedicated workforce requiring a culture of respect, recognition, inclusion and collaboration based on the highest ethical values.

Agencies: McCormick as needed will work with external recruitment vendors through our Agency Portal. Unless previously contacted, McCormick does not accept unsolicited resumes from external recruiting agencies.

McCormick & Company is an equal opportunity/affirmative action employer. All qualified applicants will receive consideration for employment without regard to sex, gender identity, sexual orientation, race, colour, religion, national origin, disability, protected veteran status, age, or any other characteristic protected by law.

As users of the disability confident scheme, we guarantee to interview all disabled applicants who meet the minimum criteria for the vacancy/ies.

LNKD1_UKTJ
"""

kw = findKWords()
print(kw.detect(data))
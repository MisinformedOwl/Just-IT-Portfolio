import os
import logging

class findKWords:
    """
    This object is designed to handle all processing of the job description.
    Firstly it takes the keywords from the file keywords.txt.
    Then it tokenises the job description into n-grams of 3.
    It then compares the contents to the set of keywords.
    Any matches are added to a set which is then returned.
    """

    kWords = set()
    punctuation = set([".", ",", ";", ":", "@", "'", "#", "~", "{", "}", "[", "]", "-", "_", "!", "*", "^", "(", ")", "&", "%", '"', "\n", "?", "|", "\\", "£", "$"])
    nGram = 3

    def __init__(self):
        """
        Simply start off my setting the current list of keywords from file.
        Also initialises the logger for key words.
        """
        self.kWords = self.getKeyWords()
        logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(level)s] - %(message)s',
                    filename="Logs.log")
        self.logger = logging.getLogger("findKeyWords")

    def removePunctuation(self,tokens: list[str]) -> list[str]:
        """
        This function is responcible for removing \n from the center of some tokens.
        Example of why this was made: 'Learning\n\n\nLocation:'
        I would send in the token itself. However i need to manipualte the list itself during runtime.

        ### Parameters
            tokens: A list of tokenised strings
        
        ### Returns
            The tokens with a new set of cleaned tokens..
        """
        cleaned_tokens = []

        for token in tokens:
            if token in self.kWords:
                cleaned_tokens.append(token)
                continue
            #Create new token that is clean of punctuation to be split via ' '
            cleaned = ''.join(c if 'a' <= c <= 'z' \
                                else ' ' \
                                for c in token.lower())
            
            #Remove the '' parts by checking if part has any characters
            split_parts = [part for part in cleaned.split(" ") if part]
            cleaned_tokens.extend(split_parts)

        return cleaned_tokens

    def cleanData(self, tokens: list[str]) -> list:
        """
        This function goes through all collected tokens and cleans them so theres no...
        Punctuation, capital letters, white spaces.
        
        ### Parameters
            tokens: The tokens to be cleansed.
        
        ### Returns
            List of cleaned tokens
        """
        t = 0 # If i used 0 it would get caught by the guard clause and never exit in some bits of data.
        while t < len(tokens):
            if len(tokens[t]) <= 1 or tokens[t] == "\n":
                del tokens[t]
                continue
            
            #At the end of paragraphs there tends to be alot of new lines attached to the word.
            while len(tokens[t]) > 0 and tokens[t][-1] == "\n":
                tokens[t] = tokens[t][:-1]

            tokens[t] = tokens[t].lower()   #Decapitalise
            tokens[t] = tokens[t].lstrip()  #Remove white space on the left
            tokens[t] = tokens[t].rstrip()  #Remove white space on the right

            t+=1
        
        tokens = self.removePunctuation(tokens)

        return tokens

    def getKeyWords(self) -> set:
        """
        Gets the keywords from the file and splits them by the delimeter ,

        ### Returns
            List of key words/phrases.
        """
        try:
            with open(os.path.join(os.path.dirname(__file__), "keywords.txt"), "r") as file:
                words = file.readline().lower().split(",")
                words[-1] = words[-1][:-1] # Removes /n from the end of the set of words.
        except FileNotFoundError as ex:
            self.logger.critical("NO KEY WORDS FOUND")
            raise FileNotFoundError
        return set(words)

    def detect(self, words) -> list:
        """
        Main detection script. Sends the data into cleaning after being split.
        Then goes through the list of tokens given the n-gram range of 3 currently.

        ### Parameters
            words: The job description to be checked for key words
        
        ### Returns
            A list of key words which were detected
        """
        tokens = words.split(" ")
        tokens = self.cleanData(tokens)
        self.logger.info("Successfully cleaned Job Description.")
        keywordsFound = set()
        for x in range(1,len(tokens)+1):
            for y in range(self.nGram):
                key = " ".join(tokens[x:x+y])
                if key in self.kWords:
                    keywordsFound.add(key)
        
        if len(keywordsFound) == 0:
            self.logger.warning("0 Skills found in job")
        else:
            self.logger.info(f"Finished finding key words. Found {len(keywordsFound)}")

        return list(keywordsFound)

#This is used in testing erroneous job descriptions.

# data = """value":"About the job\nData Analyst | Tech-Driven Transformation Project | Remote (UK)\n\U0001f4b0 �35,000 � �50,000 | \U0001f3e1 Fully Remote | \U0001f9e0 Career-Defining Opportunity\n\nAre you ready to join a company on the brink of transformation � one that�s shifting from legacy operations into a tech-first, customer-led business model? Think of it as becoming the Amazon of the tool hire world � and data is at the heart of that journey.\n\nWe�re looking for a Data Analyst to support this exciting transformation and help shape the future of a brand-new digital platform. You�ll work alongside a forward-thinking data and marketing team, using customer insights to drive smarter decisions, more targeted campaigns, and long-term growth.\n\nThis is not your average entry-level analyst role. You�ll be part of a high-impact customer retention project, working with real business data, informing strategic decisions, and helping to bring a traditional industry into the future through technology.\n\nYou can be a recent graduate or someone who has a few years commerical experience under your belt, really we are looking for the right mentality coupled with technical prowess.\n\n\U0001f527 About the transformation\nThe business has split from its legacy operations and is now focused solely on building a modern, tech-led platform. The aim? To become an industry-first digital leader, where customer experience, automation, and intelligent data use sit at the centre of everything.\nThis is your chance to contribute to a full business transformation project � where your analysis will influence product, marketing, operations, and more.\n\n\U0001f4c8 What you�ll be doing\nAnalyzing customer data to uncover retention drivers, purchasing patterns, sales trends, and customer segments\nPartnering with marketing to deliver insight-driven campaigns and track their effectiveness\nSupporting the customer retention and growth project, offering data that guides business decisions\nIdentifying opportunities in the marketplace and spotting behavioural trends to gain a competitive edge\nBuilding dashboards and visualisations to report on KPIs and campaign results\nWorking cross-functionally with marketing, sales, data science and leadership to support the transformation journey\nHelping to forecast sales and customer behaviour using exploratory techniques\nCleaning, preparing, and validating data to ensure accuracy and trustworthiness in reporting\n\n\U0001f9e0 You might be a great fit if you...\n\nHave a numerical, analytical or programming degree � or equivalent experience\nUnderstand SQL and can use it to extract data from databases\nHave experience or are open to learning Python for data exploration and basic modelling\nAre familiar with (or willing to learn) data visualisation tools like Power BI, Tableau, or Metabase\nAre naturally curious � you want to ask questions, test assumptions, and explore trends\nCan communicate clearly and translate data insights into actionable business ideas\nHave experience with marketplace or SaaS businesses (a bonus, not a must)\nAre self-motivated and thrive in a remote, flexible working environment\n\n\U0001f30d The offer\n\U0001f4b0 �35,000 � �50,000, depending on experience and Python capability\n\U0001f3e1 Fully remote (UK-based) � any face-to-face travel will be covered\n\U0001f553 Flexible working � meetings on Monday & Friday, the rest is up to you\n\U0001f334 25 days holiday + bank holidays\n\U0001f9d3 Pension + 2x Life Insurance\n\U0001f393 Chance to work on an industry-first transformation\n\u2728 Direct access to decision-makers � your insights will make an impact fast"""

# kw = findKWords()
# print(kw.detect(data))

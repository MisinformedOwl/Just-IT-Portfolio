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
        logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s',
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

# data = """About the job\nWe are looking for a Scientific Research Officer, who will play a critical role in the development and drafting of both written and video content on breast cancer risk factors, with a specific focus on environmental chemicals. This content will used on our website and social media channels, aimed at a lay audience. The role will also support the current science programme including grant funding, campaign support and conference organisation and delivery.\n\nWhat we are looking for ? \nHonours degree or equivalent in biological, chemical, medical or environmental science.\nResearch experience in a scientific discipline such as biological, chemical, medical or environmental science.\nExperience of scientific writing, including writing for a scientific audience and the general public.\nAble to quickly understand and communicate scientifically complex issues to a lay audience.\nA firm understanding of chemical risk/hazard assessment.\nSome experience of research grant applications and grant funding.\nGood verbal and written communication skills, including the ability to write accurately about complex or technical topics in simple English.\nConfidence in communicating in a variety of formats with a wide range of people including experts, the public, academics and members of other charities.\nFor the full Job description please download our recruitment pack from our website.\n\nWhat we can offer \nTo be part of a fantastic supportive team.\nWork for an organisation that values a positive and inclusive culture.\nFully remote working.\nCompetitive salary £31,171 – £37,340 PA (depending on experience)\n29.5 Days Annual Leave Plus Bank Holidays.\nOption for full time colleagues to compress hours and work a 9 day fortnight.\nHealthcare cover and employee assistance programme.\nEnhanced Sickness, Maternity and Paternity pay.\nGreat supportive culture with generous professional training and development programmes.\nFor full details see our Recruitment Pack\n\nTO apply for the role you must be UK based and have the right to work in the UK\n\nApplication Process:\nThe closing date for applications is Monday 15th September at 5pm \nTo apply for this position please complete the application form found here. \n\nThe full Job Description can be found in the recruitment Pack downloadable from our website\n\nInterviews\nInterviews will be held virtually W/C 29th September 2025. If shortlisted for interview you will be asked to prepare a task/presentation.  \nIf you require any further details on the role or the process, drop us an email at recruitment@breastcanceruk.org.uk"""

# kw = findKWords()
# print(kw.detect(data))

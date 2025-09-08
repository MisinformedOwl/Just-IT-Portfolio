import os

class findKWords:
    """
    This object is designed to handle all processing of the job description.
    Firstly it takes the keywords from the file keywords.txt.
    Then it tokenises the job description into n-grams of 3.
    It then compares the contents to the set of keywords.
    Any matches are added to a set which is then returned.
    """

    kWords = set()
    punctuation = set([".", ",", ";", ":", "@", "'", "#", "~", "{", "}", "[", "]", "-", "_", "!", "*", "^", "(", ")", "&", "%", '"', "\n"])
    nGram = 3

    def __init__(self):
        """
        Simply start off my setting the current list of keywords from file.
        """
        self.kWords = self.getKeyWords()

    def removePunctuation(self, tokens: list, index: int):
        """
        This removes punctuation from the token.
        This is so that there can be direct comparison between the token and the keyword set.

        ### Parameters
            tokens: A list of tokens which will be compared.
            index: the current index in the tokens list to be cleaned
        """
        if tokens[index][-2:] == "\n":
                tokens = tokens[index][:-1]
        if tokens[index][0] in self.punctuation:
            tokens[index] = tokens[index][1:]
        if tokens[index][-1] in self.punctuation:
            tokens[index] =tokens[index][:-1]  #If theres a comma or a full stop at the end remove it.

    def cleanData(self, tokens: list[str]) -> list:
        """
        This function goes through all collected tokens and cleans them so theres no...
        Punctuation, capital letters, white spaces.
        
        ### Parameters
            tokens: The tokens to be cleansed.
        
        ### Returns
            List of cleaned tokens
        """
        for t in range(len(tokens)):
            if len(tokens[t]) < 1 or tokens[t] == "\n":
                continue

            tokens[t].lower()   #Decapitalise
            tokens[t].lstrip()  #Remove white space on the left
            tokens[t].rstrip()  #Remove white space on the right

            if len(tokens[t]) <= 1:
                continue

            self.removePunctuation(tokens, t)

        return tokens


    def getKeyWords(self) -> set:
        """
        Gets the keywords from the file and splits them by the delimeter ,

        ### Returns
            List of key words/phrases.
        """
        with open(os.path.join(os.path.dirname(__file__), "keywords.txt"), "r") as file:
            words = file.readline().lower().split(",")
            words[-1] = words[-1][:-1] # Removes /n from the end of the set of words.
        return words

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
        keywordsFound = set()
        for x in range(1,len(tokens)+1):
            for y in range(self.nGram):

                key = " ".join(tokens[x:x+y])
                if key in self.kWords:
                    keywordsFound.add(key)
        
        return list(keywordsFound)

#This is used in testing.
#data = """"""

#kw = findKWords()
#print(kw.detect(data))
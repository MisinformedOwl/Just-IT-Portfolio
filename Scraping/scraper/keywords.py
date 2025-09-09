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
    punctuation = set([".", ",", ";", ":", "@", "'", "#", "~", "{", "}", "[", "]", "-", "_", "!", "*", "^", "(", ")", "&", "%", '"', "\n", "?", "|", "\\", "£", "$"])
    nGram = 3

    def __init__(self):
        """
        Simply start off my setting the current list of keywords from file.
        """
        self.kWords = self.getKeyWords()

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
            while tokens[t][-1] == "\n":
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
        with open(os.path.join(os.path.dirname(__file__), "keywords.txt"), "r") as file:
            words = file.readline().lower().split(",")
            words[-1] = words[-1][:-1] # Removes /n from the end of the set of words.
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
        keywordsFound = set()
        for x in range(1,len(tokens)+1):
            for y in range(self.nGram):
                key = " ".join(tokens[x:x+y])
                if key in self.kWords:
                    keywordsFound.add(key)
        
        return list(keywordsFound)


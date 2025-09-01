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

#data = """"""

#kw = findKWords()
#print(kw.detect(data))
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
            if len(tokens[t]) <= 1 or tokens[t] == "\n":
                continue
            splitTokens = tokens[t].split("\n")
            if len(splitTokens) > 1:
                del tokens[t]
                for token in range(len(splitTokens)-1,-1,-1):
                    if len(splitTokens[token]) > 0:
                        tokens.insert(t, splitTokens[token])

            tokens[t] = tokens[t].lower()   #Decapitalise
            tokens[t] = tokens[t].lstrip()  #Remove white space on the left
            tokens[t] = tokens[t].rstrip()  #Remove white space on the right

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
        print(tokens)
        for x in range(1,len(tokens)+1):
            for y in range(self.nGram):
                key = " ".join(tokens[x:x+y])
                if key[0:4] == "mach":
                    print(len(key))
                if key in self.kWords:
                    if key[0:4] == "mach":
                        print("seen?")
                    keywordsFound.add(key)
        
        return list(keywordsFound)

#This is used in manual testing.

data = """

About the job

Graduate Software Developer – AI & Machine Learning


Location: Remote (UK-based applicants preferred)


Contract: Full-Time, Permanent


The Role

We’re offering an exciting opportunity for a recent graduate eager to explore the fast-moving world of artificial intelligence and natural language technologies. This role is ideal for someone looking to gain hands-on experience with Large Language Models (LLMs) and help bring intelligent features into real-world applications.


Responsibilities

    Develop and integrate AI-powered functionality into digital platforms and tools.
    Work with APIs from leading LLM providers to create solutions such as chat interfaces, automation workflows, or text analytics.
    Contribute to prototypes, testing cycles, and the improvement of AI-driven features.
    Research the latest trends in generative AI and share findings with the team.
    Produce clear, well-structured, and maintainable code.


What You’ll Need

    A degree in Computer Science, Software Engineering, or a related discipline.
    Programming knowledge in Python, JavaScript, or a comparable language.
    Some exposure to AI libraries or APIs (e.g. Hugging Face, OpenAI, LangChain).
    A solid grasp of how LLMs can be applied in practice.
    Strong problem-solving skills and enthusiasm for continuous learning.


Bonus Skills

    Experience using Git, building RESTful APIs, or working with cloud platforms.
    Academic or personal projects demonstrating interest in AI or generative technologies.


What’s on Offer

This is a chance to start your career in a rapidly growing area of technology, with the opportunity to work on innovative projects, learn from experienced developers, and grow your technical skills in a supportive environment.
"""

kw = findKWords()
print(kw.detect(data))

import unittest
import keywords
from LinkedInScraper import setupSalary

class TestKeywordDetection(unittest.TestCase):
    kwords = keywords.findKWords()
    
    def test_keywords_cleaning(self):
        """
        This test is designed to see if the code is capable of properly cleaning data. 
        This assertion data was taken from a real case of problematic cleaning.
        """
        cleanedData = ['about', 'the', 'job', 'graduate', 'software', 'developer', 'ai', 'machine', 'learning', 'location', 'remote', 'uk', 'based', 'applicants', 'preferred']
        result = self.kwords.cleanData(['\nAbout', 'the', 'job\n\nGraduate', 'Software', 'Developer', '–', 'AI', '&', 'Machine', 'Learning\n\n\nLocation:', 'Remote', '(UK-based', 'applicants', 'preferred)\n\n\n'])
        self.assertEqual(result, cleanedData)

    def test_keywords_punctuationRemoval(self):
        wordsToClean = [
            "!!!hello!!!",           # excessive punctuation
            "“quoted”",              # smart quotes
            "emoji🙂word!",          # emoji + punctuation
            "email@example.com",     # should it clean this?
            "end-of-line;",          # hyphenated + semicolon
            "《brackets》",           # non-ASCII brackets
            "word…",                 # ellipsis
            "multi!!!punct!!!word",  # repeated internal punctuation
        ]

        cleaned = [
            "hello",
            "quoted",
            "emoji",
            "word",
            "email",
            "example",
            "com",
            "end",
            "of",
            "line",
            "brackets",
            "word",
            "multi",
            "punct",
            "word"
        ]


        wordsToClean = self.kwords.removePunctuation(wordsToClean)
        
        self.assertEqual(wordsToClean, cleaned)

    def test_keywords_keywordsIntact(self):
        kwords = list(self.kwords.getKeyWords())
        cleanedkWords = self.kwords.cleanData(kwords)

        self.assertEqual(kwords, cleanedkWords)

    def test_scraper_salaryDaily(self):
        self.assertEqual(setupSalary("£500 daily - £700 daily"), 600)
    
    def test_scraper_salaryYearlySingle(self):
        self.assertEqual(setupSalary("£40K/yr"), 40000)

    def test_scraper_salaryYearlyDouble(self):
        self.assertEqual(setupSalary("£35K/yr - £55K/yr"), 45000)

if __name__ == "__main__":
    unittest.main()
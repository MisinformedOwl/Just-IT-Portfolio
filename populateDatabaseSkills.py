if __name__ == "__main__":
    """
    The purpose of this script is to automatically refresh the insert skills sql file.
    If new skills are inputted, I dont want to rely on potentially making a mistake in the sql file.
    It's also alot of hard coding for something that could be done automatically like this.
    """
    with open("Database/02-insertSkills.sql", "w") as file:
        file.writelines(["USE `LinkedInScrape`;\n\n"])
        
        skills = []
        with open("Port/scraper/keywords.txt", "r") as skillFile:
            skills = skillFile.readline().split(",")
        
        file.write("START TRANSACTION;\n") # Start transaction as autocommit is 0.
        for skill in skills:
            skill = skill.strip()
            file.write(f"INSERT INTO `Skills` (Skill) VALUES ('{skill}');\n")
        file.write("COMMIT;\n")
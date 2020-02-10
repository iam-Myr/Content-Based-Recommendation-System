class UserProfile:
    def __init__(self, userid, keywords, authors, years):
        self.userid = userid
        self.keywords = keywords
        self.authors = authors
        self.years = years

    def getUserId(self):
        return self.userid

    def getKeyWords(self):
        return self.keywords

    def getAuthors(self):
        return self.authors

    def getYears(self):
        return self.years

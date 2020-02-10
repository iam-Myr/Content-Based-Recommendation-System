import pandas as pd
from UserProfile import UserProfile
from PreProcessor import PreProcessor

ratings = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding ="latin-1")

#Filter Data by Conditions
filterBooks = ratings[(ratings.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]
filterUsers = ratings[(ratings.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]

filteredRatings = pd.merge(filterBooks, filterUsers)

#Synchronize other dfs
users = pd.read_csv("data/BX-Users.csv", sep=";", encoding ="latin-1")
cond = ~users['User-ID'].isin(filteredRatings['User-ID']) == True
users.drop(users[cond].index, inplace = True)
users.reset_index(drop=True, inplace=True)

books = pd.read_csv("data/BX-Books.csv", encoding ="latin-1", sep=";", escapechar='\\')
cond = ~books['ISBN'].isin(filteredRatings['ISBN']) == True
books.drop(books[cond].index, inplace = True)
books.reset_index(drop=True, inplace=True)

#FIND KEYWORDS
preprocessor = PreProcessor()
bookTitles = books['Book-Title'].values

keywords = []
for title in bookTitles:
    keywords.append(preprocessor.preprocess(title, #PUN, DOUBLE, LOWER GO BEFORE TOKENIZE
                ["REMOVE_NUMB", "REMOVE_PUN", "REMOVE_DOUBLE", "LOWER", "TOKENIZE", "REMOVE_STOPWORDS"]))
books['KeyWords'] = keywords

def makeUserProfile(userid):
    userRatings = filteredRatings.loc[filteredRatings['User-ID'] == userid] \
        .sort_values(by='Book-Rating', ascending=False)

    favBooksISBN = userRatings["ISBN"].head(3).values.tolist()

    keywordsUnion = list()
    authors = list()
    years = list()
    for isbn in favBooksISBN:
        book = books.loc[books['ISBN'] == isbn]
        book.reset_index(drop=True, inplace=True)

        keywordsUnion.extend(book["KeyWords"][0]) #MAKE IT A UNION
        authors.extend(book["Book-Author"].values)
        years.extend(book["Year-Of-Publication"].values)

    return [userid, keywordsUnion, authors, years]

user = users["User-ID"].sample().values[0] #Select a random user
userProfiles = pd.DataFrame(columns=['User-ID', 'KeyWords', 'Authors', 'Years'])
userProfiles.loc[len(userProfiles)] = makeUserProfile(user)
print(userProfiles)

def DiceCoefficient(keywords1, keywords2):
    keywords1 = set(keywords1)
    keywords2 = set(keywords2)
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1) + len(keywords2)
    return 2 * intersection / union

def JaccardIndex(keywords1, keywords2):
    keywords1 = set(keywords1)
    keywords2 = set(keywords2)
    intersection = len(keywords1.intersection(keywords2))
    union = (len(keywords1) + len(keywords2)) - intersection
    return intersection / union

def findSimilarBooks(userProfiles, books):
    similarBooksJaccard = pd.DataFrame(columns=['ISBN', 'Similarity'])
    similarBooksDice = pd.DataFrame(columns=['ISBN', 'Similarity'])

    for ind in books.index:
        pass
        dice = DiceCoefficient(userProfile.getKeyWords(), books["KeyWords"][ind])
        jaccard = JaccardIndex(userProfiles["KeyWords"][0], books["KeyWords"][ind])

        authors = 0;  # FIND MATCHING AUTHOR
        for author in userProfiles["Authors"][0]:
            if author == books["Book-Author"][ind]:
                authors += 1

        min = 900000  # FIND MIN YEAR DIFFERENCE
        for year in userProfiles["Years"][0]:
            difference = 1 - (abs(year - books["Year-Of-Publication"][ind]) / 2005)
            if difference < min:
                min = difference

        similarityJaccard = jaccard * 0.2 + authors * 0.4 + difference * 0.4
        if similarityJaccard != 0:
            similarBooksJaccard = \
                similarBooksJaccard.append({'ISBN': books["ISBN"][ind], 'Similarity': similarityJaccard},
                                           ignore_index=True)

    similarBooksJaccard = similarBooksJaccard.sort_values("Similarity", ascending=False).head(10)
    similarBooksJaccard.reset_index(drop=True, inplace=True)
    print(similarBooksJaccard)

findSimilarBooks(userProfiles, books)











import pandas as pd
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

ratings = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding ="latin-1")

#FILTER BY CONDITIONS
filterBooks = ratings[(ratings.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]
filterUsers = ratings[(ratings.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]

filteredRatings = pd.merge(filterBooks, filterUsers)

users = pd.read_csv("data/BX-Users.csv", sep=";", encoding ="latin-1")
cond = ~users['User-ID'].isin(filteredRatings['User-ID']) == True
users.drop(users[cond].index, inplace = True)
users.reset_index(drop=True, inplace=True)

books = pd.read_csv("data/BX-Books.csv", encoding ="latin-1", sep=";", escapechar='\\')
cond = ~books['ISBN'].isin(filteredRatings['ISBN']) == True
books.drop(books[cond].index, inplace = True)
books.reset_index(drop=True, inplace=True)

#KEYWORDS
bookTitles = books['Book-Title'].values

def findKeyWords(text):
    text = text.translate(str.maketrans('', '', string.punctuation)) #Remove Punctuation
    text = re.sub(r'\d+', '', text)  #Remove Numbers
    text = re.sub(r'\b\w{1,3}\b', '', text) #Remove 1 and 2 letter words


    stopWords = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    tokens = word_tokenize(text) #Tokenize
    wordsFiltered = []
    for w in tokens:
        if w not in stopWords:
            w = w.lower() #Lowercase
            #w = lemmatizer.lemmatize(w) #Lemmatization
           # w = stemmer.stem(w) #Stemming
            wordsFiltered.append(w) #Filter Stopwords
    return wordsFiltered

keywords = []
for title in bookTitles:
    keywords.append(findKeyWords(title))

books['KeyWords'] = keywords

def makeUserProfile(userid):
    userProfile = [userid]

    userRatings = filteredRatings.loc[filteredRatings['User-ID'] == userid] \
        .sort_values(by='Book-Rating', ascending=False)

    favBooksISBN = userRatings["ISBN"].head(3).values.tolist()

    keywordsUnion = list()
    authors = list()
    years = list()
    for isbn in favBooksISBN:
        book = books.loc[books['ISBN'] == isbn]

        #FIX THIS PART PLEASE
        for keyword in book["KeyWords"].values:
            keywordsUnion.extend(keyword)

        authors.extend(book["Book-Author"].values)
        years.extend(book["Year-Of-Publication"].values)

    userProfile.append(keywordsUnion)
    userProfile.append(authors)
    userProfile.append(years)
    return userProfile

user = users["User-ID"].sample().values[0] #Select a random user
userProfile = makeUserProfile(user)
print(userProfile)


















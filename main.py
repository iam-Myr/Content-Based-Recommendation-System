import pandas as pd
import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer


ratings = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding ="ISO-8859-1")

filterBooks = ratings[(ratings.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]
filterUsers = ratings[(ratings.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]

filteredRatings = filterBooks.merge(filterUsers)

users = pd.read_csv("data/BX-Users.csv", sep=";", encoding ="ISO-8859-1")
cond = ~users['User-ID'].isin(filteredRatings['User-ID']) == True
users.drop(users[cond].index, inplace = True)

books = pd.read_csv("data/BX-Books.csv", encoding ="ISO-8859-1", low_memory=False)
books.drop(books.columns[[8, 9, 10, 11]], axis = 1, inplace = True) #Something weird with those columns
cond = ~books['ISBN'].isin(filteredRatings['ISBN']) == True
books.drop(books[cond].index, inplace = True)
books.reset_index(drop=True, inplace=True)

bookTitles = books['Book-Title'].values

def findKeyWords(text):
    text = text.translate(str.maketrans('', '', string.punctuation)) #Remove Punctuation
    text = re.sub(r'\d+', '', text)  #Remove Numbers

    stopWords = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    tokens = word_tokenize(text) #Tokenize
    wordsFiltered = []
    for w in tokens:
        if w not in stopWords:
            w = w.lower() #Lowercase
            w = lemmatizer.lemmatize(w) #Lemmatization
            w = stemmer.stem(w) #Stemming
            wordsFiltered.append(w) #Filter Stopwords
    return wordsFiltered

keywords = []
for title in bookTitles:
    keywords.append(findKeyWords(title))

books['KeyWords'] = keywords
print(books.head())













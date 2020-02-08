import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import string
import re

pass
class PreProcessor:
    pass

    def filterByConditions(df, cond1, cond2):
        filter1 = df[cond1]
        filter2 = df[cond2]

        return pd.merge(filter1, filter2)

    def synchronize(df1,df2,column):
        cond = ~df1[column].isin(df2[column]) == True
        df1.drop(df1[cond].index, inplace=True)
        df1.reset_index(drop=True, inplace=True)
        return df1

    def findKeyWords(text):
        text = text.translate(str.maketrans('', '', string.punctuation))  # Remove Punctuation
        text = re.sub(r'\d+', '', text)  #Remove Numbers

        stopWords = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        stemmer = PorterStemmer()

        tokens = word_tokenize(text)  #Tokenize
        wordsFiltered = []
        for w in tokens:
            if w not in stopWords:
                w = w.lower()  # Lowercase
                w = lemmatizer.lemmatize(w)  # Lemmatization
                w = stemmer.stem(w)  # Stemming
                wordsFiltered.append(w)  # Filter Stopwords
        return wordsFiltered
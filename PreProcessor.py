import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import string
import re

pass
class PreProcessor:

    def filterData(df, cond1, cond2):
        filter1 = df[cond1]
        filter2 = df[cond2]

        return pd.merge(filter1, filter2)

    def synchronize(df1,df2,column):
        cond = ~df1[column].isin(df2[column]) == True
        df1.drop(df1[cond].index, inplace=True)
        df1.reset_index(drop=True, inplace=True)
        return df1

    def findKeyWords(text):
        pass


    def removePunctuation(self, text):
        return text.translate(str.maketrans('', '', string.punctuation))

    def removeNumbers(self, text):
        return re.sub(r'\d+', '', text)

    def tokenize(self, text):
        return word_tokenize(text)

    def lemmatize(self, tokens):
        wordsFiltered = []
        for w in tokens:
            wordsFiltered.append(WordNetLemmatizer().lemmatize(w))
        return wordsFiltered

    def stem(self, tokens):
        wordsFiltered = []
        for w in tokens:
            wordsFiltered.append(PorterStemmer().stem(w))
        return wordsFiltered

    def stopWords(self, tokens):
        wordsFiltered = []
        stopWords = set(stopwords.words('english'))
        for w in tokens:
            if w not in stopWords:
                wordsFiltered.append(w)
        return wordsFiltered

    def makeLowercase(self, text):
            return  text.lower()

    def removeDouble(self, text):
        return re.sub(r'\b\w{1,3}\b', '', text)

    def preprocess(self, text, instructions): #Instructions is a list
        for instruction in instructions:
            if instruction == "REMOVE_NUMB":
                text = self.removeNumbers(text)
            elif instruction == "REMOVE_PUN":
                text = self.removePunctuation(text)
            elif instruction == "REMOVE_DOUBLE":
                text = self.removeDouble(text)
            elif instruction == "LOWER":
                text = self.makeLowercase(text)
            elif instruction == "TOKENIZE":
                tokens = self.tokenize(text)
            elif instruction == "REMOVE_STOPWORDS":
                tokens = self.stopWords(tokens)
            elif instruction == "LEMMATIZE":
                tokens = self.lemmatize(tokens)
            elif instruction == "STEM":
                tokens = self.stem(tokens)


        return tokens
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import string
import re

class PreProcessor:

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

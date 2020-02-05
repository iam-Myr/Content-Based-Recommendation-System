import pandas as pd

df = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding = "ISO-8859-1")

filterBooks = df[(df.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]
filterUsers = df[(df.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]

filtered3 = filterBooks.merge(filterUsers)
print (filtered3)
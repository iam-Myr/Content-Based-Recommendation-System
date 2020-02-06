import pandas as pd

ratings = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding ="ISO-8859-1")
print(ratings["ISBN"].value_counts())


filterBooks = ratings[(ratings.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]
filterUsers = ratings[(ratings.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]

filteredRatings = filterBooks.merge(filterUsers)
#print(filteredRatings)

users = pd.read_csv("data/BX-Users.csv", sep=";", encoding ="ISO-8859-1")
cond = ~users['User-ID'].isin(filteredRatings['User-ID']) == True
users.drop(users[cond].index, inplace = True)

books = pd.read_csv("data/BX-Books.csv", encoding ="ISO-8859-1", low_memory=False)
print(books)
cond = ~books['ISBN'].isin(filteredRatings['ISBN']) == True
books.drop(books[cond].index, inplace = True)




import pandas as pd
from PreProcessor import PreProcessor

#A Content Based Recommendation System
#Using data from Book Crossing
#http://www2.informatik.unifreiburg.de/~cziegler/BX/)
#Author: Myriam Kapon
#Date: 12/2/2020


def main():
    books = pd.read_csv("data/BX-Books.csv", encoding="latin-1", sep=";", escapechar='\\')
    ratings = pd.read_csv("data/BX-Book-Ratings.csv", sep=";", encoding="latin-1")
    users = pd.read_csv("data/BX-Users.csv", sep=";", encoding="latin-1")

    #Filter Data
    filterBooks = ratings[(ratings.groupby('ISBN')['Book-Rating'].transform('count') >= 10)]
    filterUsers = ratings[(ratings.groupby('User-ID')['Book-Rating'].transform('count') >= 5)]

    global filteredRatings
    filteredRatings = pd.merge(filterBooks, filterUsers)

    #Synchronize other dfs
    global filteredUsers
    filteredUsers = users[users["User-ID"].isin(filteredRatings["User-ID"])]
    filteredUsers.reset_index(drop=True, inplace=True)

    global filteredBooks
    filteredBooks = books[books["ISBN"].isin(filteredRatings["ISBN"])]
    filteredBooks.reset_index(drop=True, inplace=True)

    print("Data ready!")

    #Find Keywords
    preprocessor = PreProcessor()
    bookTitles = filteredBooks['Book-Title'].values

    keywords = []
    for title in bookTitles:
        #REMOVE_NUMB, REMOVE_PUN, REMOVE_DOUBLE, LOWER, TOKENIZE, REMOVE_STOPWORDS, LEMMATIZE, STEM
         keywords.append(preprocessor.preprocess(title,
                ["REMOVE_NUMB", "REMOVE_PUN", "REMOVE_DOUBLE", "LOWER", "TOKENIZE", "REMOVE_STOPWORDS", "LEMMATIZE"]))

    pd.options.mode.chained_assignment = None #Remove this to enable chained warning
    filteredBooks['KeyWords'] = keywords
    print("Keywords found!")

    #Make user profile
    userProfiles = pd.DataFrame(columns=['User-ID', 'KeyWords', 'Authors', 'Years'])
    for x in range(0, 5):
        user = filteredUsers["User-ID"].sample().values[0]  # Select a random user
        userProfiles.loc[len(userProfiles)] = makeUserProfile(user)
        print("\n-------User profile-------\n", userProfiles.iloc[x])

        #Get similar books
        print("\nFinding similar books...")
        similarBooksJaccard, similarBooksDice = findSimilarBooks(userProfiles.iloc[x])

        similarBooksJaccard.to_csv(r'results\user(%d)-jaccard.csv' % userProfiles["User-ID"].iloc[x], index=None, header=True)
        similarBooksDice.to_csv(r'results\user(%d)-dice.csv' % userProfiles["User-ID"].iloc[x], index=None, header=True)

        #Find golden standard
        golden = goldenSimilar(similarBooksJaccard, similarBooksDice)
        golden.to_csv(r'results\user(%d)-gold.csv' % userProfiles["User-ID"].iloc[x], index=None, header=True)

        #Overlap
        overlapDJ = calcOverlap(similarBooksJaccard["ISBN"].tolist(), similarBooksDice["ISBN"].tolist())
        print("Overlap of Dice and Jaccard: ", overlapDJ)
        overlapJG = calcOverlap(similarBooksJaccard["ISBN"].tolist(), golden["ISBN"].tolist())
        print("Overlap of Jaccard and Golden: ", overlapJG)
        overlapDG = calcOverlap(similarBooksDice["ISBN"].tolist(), golden["ISBN"].tolist())
        print("Overlap of Dice and Golden: ", overlapDG)

    userProfiles.to_csv(r'results\UserProfiles.csv', header=True)


def makeUserProfile(userid):
    #Find the user's ratings
    userRatings = filteredRatings.loc[filteredRatings['User-ID'] == userid] \
        .sort_values(by='Book-Rating', ascending=False)

    favBooksISBN = userRatings["ISBN"].head(3).values.tolist()

    keywordsUnion = set()
    authors = set()
    years = set()
    for isbn in favBooksISBN:
        book = filteredBooks.loc[filteredBooks['ISBN'] == isbn]
        book.reset_index(drop=True, inplace=True)

        keywordsUnion.update(book["KeyWords"].values[0])
        authors.update(book["Book-Author"].values)
        years.update(book["Year-Of-Publication"].values)

    userProfile = [userid, list(keywordsUnion), list(authors), list(years)]
    return userProfile


def DiceCoefficient(keywords1, keywords2):
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1) + len(keywords2)
    return 2 * intersection / union


def JaccardIndex(keywords1, keywords2):
    intersection = len(keywords1.intersection(keywords2))
    union = (len(keywords1) + len(keywords2)) - intersection
    return intersection / union


def findSimilarBooks(userProfiles):
    similarBooksJaccard = pd.DataFrame(columns=['ISBN', 'Similarity'])
    similarBooksDice = pd.DataFrame(columns=['ISBN', 'Similarity'])

    #Filter to remove already rated books
    alreadyRated = filteredRatings.loc[filteredRatings['User-ID'] == userProfiles["User-ID"]]
    alreadyRated.reset_index(drop=True, inplace=True)
    alreadyRatedFilter = filteredBooks["ISBN"].isin(alreadyRated["ISBN"])

    for ind in filteredBooks[~alreadyRatedFilter].index:
        # Find if there's a matching author
        authors = 0
        if (filteredBooks["Book-Author"][ind] in userProfiles["Authors"]):
            authors += 1

        # Find min year difference - Max is used because it's 1 - min
        maxDiff = -1
        for year in userProfiles["Years"]:
            difference = 1 - (abs(year - filteredBooks["Year-Of-Publication"][ind]) / 2005)
            if difference > maxDiff:
             maxDiff = difference

        #Jaccard variation
        jaccard = JaccardIndex(set(userProfiles["KeyWords"]), set(filteredBooks["KeyWords"][ind]))
        similarityJaccard = jaccard * 0.2 + authors * 0.4 + maxDiff * 0.4
        if similarityJaccard != 0:
            similarBooksJaccard = similarBooksJaccard\
                .append({'ISBN': filteredBooks["ISBN"][ind], 'Similarity': similarityJaccard}, ignore_index=True)

        #Dice variation
        dice = DiceCoefficient(set(userProfiles["KeyWords"]), set(filteredBooks["KeyWords"][ind]))
        similarityDice = dice * 0.5 + authors * 0.3 + maxDiff * 0.2
        if similarityDice != 0:
            similarBooksDice = similarBooksDice \
                .append({'ISBN': filteredBooks["ISBN"][ind], 'Similarity': similarityDice}, ignore_index=True)


    #Sorting
    similarBooksJaccard = similarBooksJaccard.sort_values("Similarity", ascending=False).head(10)
    similarBooksJaccard.reset_index(drop=True, inplace=True)
    similarBooksDice = similarBooksDice.sort_values("Similarity", ascending=False).head(10)
    similarBooksDice.reset_index(drop=True, inplace=True)

    print("Found!")
    return similarBooksJaccard, similarBooksDice


def calcOverlap(list1, list2):
    if len(list1) != len (list2):
        print("Cannot compare lists of different size!")
        return
    overlap = 0
    matches = 0
    for i in range(0, len(list1)):
        if list1[i] == list2[i]:
            matches += 1
        overlap += matches / (i+1)
    return overlap/len(list1)

def goldenSimilar(df1, df2):
    golden = pd.DataFrame(columns=['ISBN', 'Similarity', 'Count'])
    allSuggestions = list(set().union(df1["ISBN"].tolist(), df2["ISBN"].tolist()))

    for item in allSuggestions:
        count = 0
        avgsim = 0
        for x in range(0, len(df1)):
            if item == df1["ISBN"][x]:
                count +=1
                avgsim += df1["Similarity"][x]
            if item == df2["ISBN"][x]:
                count += 1
                avgsim += df2["Similarity"][x]
        avgsim = avgsim/2
        golden = golden \
            .append({'ISBN': item, "Similarity": avgsim, 'Count': count},  ignore_index=True)

    golden.sort_values(['Count', "Similarity"], ascending=False, inplace=True)
    golden.drop('Count', 1, inplace=True)

    return golden.head(10)

if __name__ == "__main__":
    main()




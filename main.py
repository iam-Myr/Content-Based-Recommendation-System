import csv

results = []
with open("data/BX-Book-Ratings.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader: # each row is a list
        results.append(row)
        print(row)
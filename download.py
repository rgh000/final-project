import os

for i in range(800):
	os.system("wget http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-1M-5gram-20090715-" + str(i) + ".csv.zip")

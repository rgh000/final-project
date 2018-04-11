import scipy
import scipy.sparse
import os
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr
import math
import random
import re
import numpy as np
import urllib2
import re
from bs4 import BeautifulSoup

#Load pre-trained word2ec vectors
from gensim.models import KeyedVectors
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)

def alpha(word):
	return re.sub('[^A-Za-z\']+', '', word.lower())

#load function word list, context word list, target word list
f = open('fwlist-277.txt', 'r')
lines4 = f.readlines()
f.close()
functions = []
for l in lines4:
	ls = l.split()
	functions.append(alpha(ls[0]))

f = open('lemma.al', 'r')
lines2 = f.readlines()
f.close()
targets = dict()
i = 0
for l in lines2:
	ls = l.split()
	if not ls[2] in targets:
		targets[ls[2]] = i
		i += 1


f = open('hunspell/en_US.dic', 'r')
lines3 = f.readlines()
f.close()
contexts = dict()
i = 0
for l in lines3:
	ls = l.split()[0].split('/')
	if alpha(ls[0]) == ls[0] and not ls[0] in contexts:
		contexts[ls[0]] = i
		i += 1


#Check if preloaded word2vec vector exists for word
def word2vec(word):
	try:
		a = model[alpha(word)]
		return True
	except:
		return False


#Reverse look up context word given its id
def revcont(n):
	for k,v in contexts.iteritems():
		if v == n:
			return k

#Load sparse matrices with context information from file
M_list = []
for i in range(20):
	M_list.append(scipy.sparse.load_npz('M_M' + str(i) + '.npz').tolil())












#Supply target word and decade (10 => 1800-1810, 11 => 1810-1820, ..., 19 => 1990-2000)
target_word = 'cell'
year = 19

lil = M_list[year][targets[target_word]].tolil()

#Scrape historical thesaurus and parse definitions
page = urllib2.urlopen('http://historicalthesaurus.arts.gla.ac.uk/category-selection/?qsearch=' + target_word)
soup = BeautifulSoup(page, 'html.parser')
box = soup.find_all('p', class_='catOdd') + soup.find_all('p', class_='catEven')
definitions = []
for b in box:
	if not 'Matching word' in b.text and b.text[-1:] == ')':
		definitions.append(re.sub('[0-9a-z| ]*\.', '', b.text).replace(u'\u2013', '-').replace('/', ' ').split(' :: '))

defv = []
definition_used = []
for d in definitions:
	if d[len(d)-1][-2:-1] == '-' and (d[len(d)-1][-4:-2] == 'OE' or (d[len(d)-1][-3:-2].isdigit() and d[len(d)-1][-4:-3].isdigit() and d[len(d)-1][-5:-4].isdigit() and d[len(d)-1][-6:-5].isdigit() and int(d[len(d)-1][-6:-2]) < (1809 + year * 10))):
		l = np.zeros(300)
		count = 0
		added = []
		for e in d:
			f = re.split(r'[ /]+', e)
			for g in f:
				if not alpha(g) == '' and not alpha(g) in functions and word2vec(g) and not alpha(g) in added:
					l += model[alpha(g)]
					added.append(alpha(g))
					count += 1
		exists = False
		for i in range(len(defv)):
			if cosine_similarity([defv[i], (l / (count + 1e-15))])[0][1] > 0.7:
				exists = True
		if not exists:
			defv.append(l / (count + 1e-15))
			definition_used.append(True)
		else:
			definition_used.append(False)
	else:
		definition_used.append(False)

cluster = []
prev = []
vectors = []
for d in defv:
	vectors.append([d])


#k-means clustering with upper bound of 10 iterations
for z in range(10):
	print z
	mean = []
	for v in vectors:
		mean.append(sum(v) / (1e-15 + len(v)))
	vectors = []
	cluster = []
	for d in defv:
		vectors.append([d])
		cluster.append([])
	for i, (row, data) in enumerate(zip(lil.rows, lil.data)):
		for j, val in zip(row, data):
			count = 0
			avg = np.zeros(300)
			fourth = j / (len(contexts)*len(contexts)*len(contexts))
			third = (j - fourth*len(contexts)*len(contexts)*len(contexts)) / (len(contexts)*len(contexts))
			second = (j - fourth*len(contexts)*len(contexts)*len(contexts) - third*len(contexts)*len(contexts)) / len(contexts)
			first = j - fourth*len(contexts)*len(contexts)*len(contexts) - third*(len(contexts)*len(contexts)) - second*len(contexts)
			if word2vec(revcont(fourth)) and alpha(revcont(fourth)) not in functions:
				avg = avg + model[alpha(revcont(fourth))]
				count += 1
			if word2vec(revcont(third)) and alpha(revcont(third)) not in functions:
				avg = avg + model[alpha(revcont(third))]
				count += 1
			if word2vec(revcont(second)) and alpha(revcont(second)) not in functions:
				avg = avg + model[alpha(revcont(second))]
				count += 1
			if word2vec(revcont(first)) and alpha(revcont(first)) not in functions:
				avg = avg + model[alpha(revcont(first))]
				count += 1
			if not count == 0:
				avg = avg / (count + 1e-15)
				maximum = -1000000
				maxi = -1000000
				for i in range(len(defv)):
					if cosine_similarity([avg, mean[i]])[0][1] > maximum:
						maximum = cosine_similarity([avg, mean[i]])[0][1]
						maxi = i
				for q in range(int(val)):
					cluster[maxi].append('{' + alpha(revcont(first)) + ' ' + alpha(revcont(second)) + ' ' + target_word + ' ' + alpha(revcont(third)) + ' ' + alpha(revcont(fourth)) + '}')
					vectors[maxi].append(avg)
	if cluster == prev:
		break
	else:
		prev = cluster


#Print clusters
i = -1
j = -1
for d in definitions:
	j += 1
	if definition_used[j]:
		i += 1
		print d
		print "Cluster: ", set(cluster[i])
		print ''


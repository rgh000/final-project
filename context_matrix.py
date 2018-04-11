import scipy
import scipy.sparse
import os
import re
import sys
#from sklearn.metrics.pairwise import cosine_similarity
#from scipy.stats import pearsonr

def alpha(word):
	return re.sub('[^A-Za-z\']+', '', word.lower())

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

M_list = []
for i in range(20):
	M_list.append(scipy.sparse.lil_matrix((len(targets), len(contexts) * len(contexts) * len(contexts) * len(contexts))))

for i in range(int(sys.argv[1]))[int(sys.argv[1])-50:]:
#for i in range(1):
	os.system("unzip *-" + str(i) + ".csv.zip -d ./M/")
	f = open('M/googlebooks-eng-1M-5gram-20090715-' + str(i) + '.csv', 'r')
	lines = f.readlines()
	f.close()
	os.system("rm M/googlebooks-eng-1M-5gram-20090715-" + str(i) + ".csv")
	for l in lines:
		ls = l.split()
		try:
			if alpha(ls[2]) in targets and alpha(ls[0]) in contexts and alpha(ls[1]) in contexts and alpha(ls[2]) in contexts and alpha(ls[4]) in contexts and int(ls[5]) >= 1800 and int(ls[5]) < 2000:
				M_list[(int(ls[5]) - 1800) / 10][targets[alpha(ls[2])], contexts[alpha(ls[0])] + contexts[alpha(ls[1])]*len(contexts) + contexts[alpha(ls[3])]*len(contexts)*len(contexts) + contexts[alpha(ls[4])]*len(contexts)*len(contexts)*len(contexts)] += int(ls[6])
		except:
			pass

for i in range(20):
	scipy.sparse.save_npz('M_M' + str(sys.argv[1]) + '_' + str(i) + '.npz', M_list[i].tocsr())

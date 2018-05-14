import scipy
import scipy.sparse
import os
import pickle

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


#list of context words from http://www-personal.umich.edu/~jlawler/wordlist
f = open('wordlist', 'r')
lines3 = f.readlines()
f.close()
contexts = dict()
i = 0
for l in lines3:
	ls = l.split()
	if not ls[0] in contexts:
		contexts[ls[0]] = i
		i += 1


M_list = []
for i in range(20):
	M_list.append(scipy.sparse.lil_matrix((len(targets), len(contexts)*len(contexts)*len(contexts)*len(contexts))))

for i in range(2):
	data_ = pickle.load(open('data' + str(i*5+4) + '.p', 'rb'))
	for k,v in data_.iteritems():
		try:
			if k[2] in targets and k[0] in contexts and k[1] and k[3] in contexts and k[4] in contexts and int(k[5]) >= 180 and int(k[5]) < 200:
				M_list[(int(k[5]) - 180)][targets[ls[0]], contexts[k[0]] + contexts[k[1]]*len(contexts) + contexts[k[3]]*len(contexts)*len(contexts) + contexts[k[4]]*len(contexts)*len(contexts)*len(contexts)] += int(v)
		except:
			pass


for i in range(20):
	scipy.sparse.save('M' + str(i) + '.pkl', M_list[i].tocsr())

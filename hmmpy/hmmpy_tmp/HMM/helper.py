import random
import numpy

class HMMHelper(object):
	def __init__(self, hiddenSeqs, observedSeqs, observationSeqs):
		self.hiddenSeqs = hiddenSeqs
		self.observedSeqs = observedSeqs
		self.observationSeqs = observationSeqs

	def initializeHMM(self):
		hiddenStates = []
		for s in self.hiddenSeqs:
			hiddenStates.extend(list(set(s)))

		observedStates = []
		for s in self.observedSeqs:
			observedStates.extend(list(set(s)))	
		
		'''
		Compute initial probabilities
		'''

		start = {}
		for h in hiddenStates:
			start[h] = 0
			for seq in self.hiddenSeqs:
				if seq[0] == h:
					start[h] += 1.0/len(hiddenSeqs)
		
		'''
		Compute next symbol probabilities
		'''

		go = {}
		for h1 in hiddenStates:
			for h2 in hiddenStates:
				go[(h1, h2)] = 0

		for seq in self.hiddenSeqs:
			for i in xrange(0, len(seq)-1):
				go[(seq[i], seq[i+1])] += 1.0

		i = 0
		total = {}
		for h1 in hiddenStates:
			total[h1] = 0
			for h2 in hiddenStates:
				total[h1] += go[(h1, h2)]
			for h2 in hiddenStates:
				go[(h1, h2)] = go[(h1, h2)]/total[h1]

		'''
		Compute emission probabilities
		'''
		
		out = {}
		total = {}
		for h in hiddenStates:
			total[h] = 0.0
		
		for observations in self.observationSeqs:
			aggr = Counter(observations)
			for h in hiddenStates:
				for o in observedStates:
					total[h] += aggr.get((h, o), 0)
		
		for h in hiddenStates:
			for o in observedStates:
				if total[h] == 0:
					out[(h, o)] = 0
				else:
					out[(h, o)] = aggr.get((h, o), 0)/total[h]

		return start, go, out

	def emissionSelector(self, out, h):
		L = []
		for k, v in out:
			if k == h:
				L.append((v, out[(k, v)]))

		L.sort(key=lambda tup: tup[1])
		
		P = []
		for e in L:
		    P.append(e[1])

		prob = numpy.array(P)
		cumprob = numpy.cumsum(prob)
		i = 0
		for i in xrange(0, len(L)):
		    L[i] = (L[i][0], cumprob[i])
		    i += 1
		r = random.randrange(0, 1000)/1000

		for i in xrange(0, len(L)):
		    if L[i][1]-r >= 0 and L[i][1] >= 0:
		        return L[i][0]
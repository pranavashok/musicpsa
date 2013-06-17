from hmmpy.HMM.calculator import HMM
from music21 import *
from pypsa.psa.LearnPSA import LearnPSA
from operator import itemgetter
import random
from collections import Counter
import numpy
import sys

def parseNotes(str):
	s = []
	sample = []
	for element in str.elements:
		if type(element).__name__ == 'Part':
			if element.hasElementOfClass('Note'):
				for e in element:
					if type(e).__name__ == 'Note':
						sample.append(e.nameWithOctave)
				if len(sample) > 10:
					s.append(sample)
				sample = []
	return s

def parseDurations(str):
	d = []
	duration = []
	for element in str.elements:
		if type(element).__name__ == 'Part':
			if element.hasElementOfClass('Note'):
				for e in element:
					if type(e).__name__ == 'Note':
						duration.append(e.duration.quarterLength.__str__())
				if len(duration) > 10:
					d.append(duration)
				duration = []
	return d

def parseNotesWithDurations(str):
	obs = []
	observationSeqs = []
	for element in str.elements:
		if type(element).__name__ == 'Part':
			if element.hasElementOfClass('Note'):
				for e in element:
					if type(e).__name__ == 'Note':
						obs.append((e.nameWithOctave, e.duration.quarterLength.__str__()))
				if len(obs) > 10:
					observationSeqs.append(obs)
				obs = []
	return observationSeqs

def initializeHMM(hiddenSeqs, observedSeqs, observationSeqs):
	hiddenStates = []
	for s in hiddenSeqs:
		hiddenStates.extend(list(set(s)))

	observedStates = []
	for s in observedSeqs:
		observedStates.extend(list(set(s)))	
	
	'''
	Compute initial probabilities
	'''

	start = {}
	for h in hiddenStates:
		start[h] = 0
		for seq in hiddenSeqs:
			if seq[0] == h:
				start[h] += 1.0/len(hiddenSeqs)
	
	'''
	Compute next symbol probabilities
	'''

	go = {}
	for h1 in hiddenStates:
		for h2 in hiddenStates:
			go[(h1, h2)] = 0

	for seq in hiddenSeqs:
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
	
	for observations in observationSeqs:
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

def emissionSelector(out, h):
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

str = []
for i in range(1 , len(sys.argv)):
	str.append(converter.parse(sys.argv[i]))

sampleNoteSeqs = []
for s in str:
	sampleNoteSeqs.extend(parseNotes(s))

uniqueNotes = []
for l in sampleNoteSeqs:
	uniqueNotes.append(list(set(l)))

N = []
for i in range(len(uniqueNotes)):
	n = LearnPSA(0.2, 10, 3, uniqueNotes[i])
	n.add_sample(" ".join(sampleNoteSeqs[i]))
	N.append(n)

notes = {}
for i in range(0, len(N)):
	N[i].generate_pst()
	states, transition, nextstate = N[i].generate_psa()
	notes[i] = []
	for j in range(0, 10):
		notes[i].append(N[i].generate_run(states, transition, nextstate, 440).split(" "))

sampleDurationSeqs = []
for s in str:
	sampleDurationSeqs.extend(parseDurations(s))

uniqueDurations = []
for l in sampleDurationSeqs:
	uniqueDurations.append(list(set(l)))

D = []
for i in range(len(uniqueDurations)):
	d = LearnPSA(0.2, 10, 3, uniqueDurations[i])
	d.add_sample(" ".join(sampleDurationSeqs[i]))
	D.append(d)

durations = {}
for i in range(0, len(D)):
	durations[i] = []
	D[i].generate_pst()
	states, transition, nextstate = D[i].generate_psa()
	for j in range(0, 10):
		durations[i].append(D[i].generate_run(states, transition, nextstate, 440).split(" "))
'''

observationSeqs = []
for s in str:
	observationSeqs.extend(parseNotesWithDurations(s))

start, go, out = initializeHMM(sampleNoteSeqs, sampleDurationSeqs, observationSeqs)
model = HMM(start, go, out)

learnSample = []
for s in sampleDurationSeqs:
	learnSample.append((s, 10))

model.generate(learnSample)

prev = 0
for i in xrange(0, 5):
	model.optimize()
	cur = model.likelyhood()
	print cur
	if round(prev, 2) == round(cur, 2):
		print cur
		break
	prev = cur
'''

for k in range(0, 10):
	parts = []
	full = stream.Stream()

	for i in xrange(0, len(notes)):
		part = stream.Stream()
		for j in xrange(0, len(durations[i])):
			d = duration.Duration(float(durations[i][k][j]))
			n = note.Note(notes[i][k][j])
			n.volume.velocity = 127
			n.duration = d
			part.append(n)
		parts.append(part)

	for part in parts:
		full.append(part)

	mf = midi.translate.streamToMidiFile(full)
	mf.open('o_'+sys.argv[1].replace("/", "_")+k.__str__()+'.mid', 'wb')
	mf.write()
	mf.close()
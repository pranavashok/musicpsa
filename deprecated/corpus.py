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
	for part in str.elements:
		if type(part).__name__ == 'Part':
			for measure in part.elements:
				if type(measure).__name__ == 'Measure':
					for note in measure.elements:
						if type(note).__name__ == 'Note':
							sample.append(note.nameWithOctave)
			s.append(sample)
			sample = []
	return s

def parseChords(str):
	s = []
	sample = []
	for element in str.elements:
		if element.hasElementOfClass('Chord'):
			for e in element:
				if type(e).__name__ == 'Chord':
					sample.append(" ".join(e.pitchNames))
			s.append(sample)
			sample = []
	return s

def parseDurations(str):
	d = []
	duration = []
	for part in str.elements:
		if type(part).__name__ == 'Part':
			for measure in part.elements:
				if type(measure).__name__ == 'Measure':
					for note in measure.elements:
						if type(note).__name__ == 'Note':
							duration.append(note.duration.quarterLength.__str__())
			d.append(duration)
			duration = []
	return d

def notesAndChords(str):
	N = {}
	for element in str.elements:
		if element.hasElementOfClass('Chord') or element.hasElementOfClass('Note'):
			for v in element:
				if type(v).__name__ == 'Chord':
					for n in str.elements:
						if n.hasElementOfClass('Note'):
							x = n.getElementAtOrBefore(v.offset)
							if type(x).__name__ == 'Note':
								N[v.offset] = (x.name, " ".join(v.pitchNames))
	return N

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

str = corpus.parse(sys.argv[1])

o = midi.translate.streamToMidiFile(str)
o.open(sys.argv[1].replace("/", "_")+'.mid', 'wb')
o.write()
o.close()

sampleNoteSeqs = []
sampleNoteSeqs.extend(parseNotes(str))

uniqueNotes = []
for l in sampleNoteSeqs:
	uniqueNotes.append(list(set(l)))

N = []
for i in range(len(uniqueNotes)):
	n = LearnPSA(0.2, 10, 3, uniqueNotes[i])
	n.add_sample(" ".join(sampleNoteSeqs[i]))
	N.append(n)

notes = []
for i in range(0, len(N)):
	N[i].generate_pst()
	states, transition, nextstate = N[i].generate_psa()
	notes.append(N[i].generate_run(states, transition, nextstate, 240).split(" "))

sampleDurationSeqs = []
sampleDurationSeqs.extend(parseDurations(str))

uniqueDurations = []
for l in sampleDurationSeqs:
	uniqueDurations.append(list(set(l)))

D = []
for i in range(len(uniqueDurations)):
	d = LearnPSA(0.2, 10, 3, uniqueDurations[i])
	d.add_sample(" ".join(sampleDurationSeqs[i]))
	D.append(d)

durations = []
for i in range(0, len(D)):
	D[i].generate_pst()
	states, transition, nextstate = D[i].generate_psa()
	durations.append(D[i].generate_run(states, transition, nextstate, 240).split(" "))
	
'''
sampleChordSeqs = []
for seq in parseChords("demo_001.mid"):
	sampleChordSeqs.append((seq, 10))

Initial, Next, E = initializeHMM(sampleNoteSeqs, sampleChordSeqs, uniqueNotes)
model = HMM(Initial, Next, E)

model.generate(sampleChordSeqs)

prev = 0
for i in xrange(0, 100):
	model.optimize()
	cur = model.likelyhood()
	print cur
	if round(prev, 2) == round(cur, 2):
		print cur
		break
	prev = cur
'''
parts = []
full = stream.Stream()
#instruments = ["Sitar", "Shehnai", "Flute", "Violin", "Oboe", "Viola", "Piano", "Piano", "Piano", "Piano", "Piano", "Piano", "Piano", "Piano", "Piano"]
for i in xrange(0, len(notes)):
	part = stream.Stream()
	#part.append(instrument.fromString(instruments[i]))
	for j in xrange(0, len(durations[i])):
		d = duration.Duration(float(durations[i][j]))
		n = note.Note(notes[i][j])
		n.volume.velocity = 127
		n.duration = d
		part.append(n)
	parts.append(part)

for part in parts:
	full.append(part)

mf = midi.translate.streamToMidiFile(full)
mf.open('o_'+sys.argv[1].replace("/", "_")+'.mid', 'wb')
mf.write()
mf.close()

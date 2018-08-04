from hmmpy.HMM.calculator import HMM
from music21 import *
from pypsa.psa.LearnPSA import LearnPSA
from operator import itemgetter
import random
from collections import Counter
import numpy

def parseNotes(midifile):
	str = converter.parse(midifile)
	sample = []
	part = str[1]
	for ele in part:
		if type(ele).__name__ == 'Note':
			sample.append(ele.name)
	return sample

def parseNotesChopin(str):
	s = []
	sample = []
	part = str[0]
	for ele in part:
		if type(ele).__name__ == 'Voice':
			for v in ele:
				if type(v).__name__ == 'Note':
					sample.append(v.name)
			s.append(sample)
			sample = []
	return s

def parseChords(midifile):
	str = converter.parse(midifile)
	sample = []
	part = str[0]
	for ele in part:
		if type(ele).__name__ == 'Chord':
			sample.append(" ".join(ele.pitchNames))
	return sample

def parseChordsChopin(str):
	s = []
	sample = []
	part = str[0]
	for ele in part:
		if type(ele).__name__ == 'Voice':
			for v in ele:
				if type(v).__name__ == 'Chord':
					sample.append(" ".join(v.pitchNames))
			s.append(sample)
			sample = []
	return s

def parseDurations(midifile):
	str = converter.parse(midifile)
	duration = []
	part = str[1]
	for ele in part:
		if type(ele).__name__ == 'Note':
			duration.append(ele.duration.quarterLength.__str__())
	return duration

def parseDurationsChopin(str):
	s = []
	sample = []
	part = str[0]
	for ele in part:
		if type(ele).__name__ == 'Voice':
			for v in ele:
				if type(v).__name__ == 'Note':
					sample.append(v.duration.quarterLength.__str__())
			s.append(sample)
			sample = []
	return s

def notesAndChords(midifile):
	N = {}
	s = converter.parse(midifile)
	for e in s[0]:
		if type(e).__name__ == 'Chord':
			n = s[1].getElementAtOrBefore(e.offset).name
			N[e.offset] = (n, " ".join(e.pitchNames))
	return N

def notesAndChordsChopin(str):
	N = {}
	part = str[0]
	for ele in part:
		if type(ele).__name__ == 'Voice':
			for v in ele:
				if type(v).__name__ == 'Chord':
					x = ele.getElementAtOrBefore(v.offset)
					if type(x).__name__ == 'Note':
						N[e.offset] = (x.name, " ".join(v.pitchNames))
	return N

def initializeHMM(sampleNoteSeqs, sampleChordSeqs, N):
	Initial = {}
	for n in N:
		Initial[n] = 0.0
		for seq in sampleNoteSeqs:
			if seq[0] == n:
				Initial[n] += 1.0/len(sampleNoteSeqs)
	Temp = {}
	Next = {}
	for n1 in N:
		for n2 in N:
			Temp[(n1, n2)] = 0

	for seq in sampleNoteSeqs:
		for i in xrange(0, len(seq)-2):
			Temp[(seq[i], seq[i+1])] += 1.0

	i = 0
	for n1 in N:
		total = 0.0
		for n2 in N:
			total += Temp[(n1, n2)]
		for n2 in N:
			Next[(n1, n2)] = Temp[(n1, n2)]/total

	NC1 = notesAndChordsChopin(str1)
	NC2 = notesAndChordsChopin(str2)

	C = {}
	X = []
	E = {}
	for element in NC1:
		X.append(NC1[element])
	for element in NC2:
		X.append(NC2[element])

	c = Counter(X)

	sampleChordSeqs = parseChordsChopin(str1)
	sampleChordSeqs.extend(parseChordsChopin(str2))

	uniqueChords = set([])
	for l in sampleChordSeqs:
		uniqueChords = uniqueChords | set(l)
	uniqueChords = list(uniqueChords)

	for n in N:
		for ch in uniqueChords:
			E[(n, ch)] = 0.0

	for n in N:
		count = 0.0
		for k, v in c:
			if k == n:
				count += c[(k, v)]
		for k, v in c:
			if k == n:
				E[(n, v)] = c[(k, v)]/count
	return Initial, Next, E

def chordSelector(emm, n):
	L = []
	for k, v in emm:
		if k == n:
			L.append((v, emm[(k, v)]))

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
	    if L[i][1] >= 0 and L[i][1] >= 0:
	        return L[i][0]

#str1 = converter.parse("chpn-p3_format0.mid")
str2 = converter.parse("chpn-p11_format0.mid")
str1 = converter.parse("chpn_op10_e01_format0.mid")

sampleNoteSeqs = parseNotesChopin(str1)
sampleNoteSeqs.extend(parseNotesChopin(str2))

uniqueNotes = set([])
for l in sampleNoteSeqs:
	uniqueNotes = uniqueNotes | set(l)
uniqueNotes = list(uniqueNotes)

sampleDurationSeqs = parseDurationsChopin(str1)
sampleDurationSeqs.extend(parseDurationsChopin(str2))

uniqueDurations = set([])
for l in sampleDurationSeqs:
	uniqueDurations = uniqueDurations | set(l)
uniqueDurations = list(uniqueDurations)

D = LearnPSA(0.2, 10, 3, list(set(sampleDurationSeqs[5])))
'''
for seq in sampleDurationSeqs:
	if len(seq) > 10:
		D.learn_sample(" ".join(seq))
'''

D.learn_sample(" ".join(sampleDurationSeqs[5]))

states, transition, nextstate = D.generate_psa()
durations = D.generate_run(states, transition, nextstate, 160).split(" ")

N = LearnPSA(0.2, 10, 3, list(set(sampleNoteSeqs[5])))

'''
for seq in sampleNoteSeqs:
	if len(seq) > 10:
		N.learn_sample(" ".join(seq))
'''

N.learn_sample(" ".join(sampleNoteSeqs[5]))

states, transition, nextstate = N.generate_psa()
notes = N.generate_run(states, transition, nextstate, 160).split(" ")
'''
sampleChordSeqs = []

for crd in parseChordsChopin(str1):
	if len(crd) > 10:
		sampleChordSeqs.append((crd, len(crd)))

for crd in parseChordsChopin(str2):
	if len(crd) > 10:
		sampleChordSeqs.append((crd, len(crd)))

Initial, Next, E = initializeHMM(sampleNoteSeqs, sampleChordSeqs, uniqueNotes)
model = HMM(Initial, Next, E)
model.generate(sampleChordSeqs)

prev = 0
for i in xrange(0, 1):
	model.optimize()
	cur = model.likelyhood()
	print cur
	if round(prev, 3) == round(cur, 3):
		print cur
		break
	prev = cur
'''
a = stream.Part()
b = stream.Part()
full = stream.Stream()

a = stream.Stream()
for i in xrange(0, len(notes)):
	d = duration.Duration(float(durations[i]))
	n = note.Note(notes[i])
	n.volume.velocity = 127
	n.duration = d
	a.append(n)
	'''crd = chord.Chord(chordSelector(model.Emm, notes[i]).split(" "))
	crd.duration = d
	crd.volume.velocity = 80
	b.append(crd)'''

full.append(a)
full.append(b)

mf = midi.translate.streamToMidiFile(full)
mf.open('test.mid', 'wb')
mf.write()
mf.close()

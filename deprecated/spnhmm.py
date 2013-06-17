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

str = []
for i in range(1 , len(sys.argv)-1):
	str.append(converter.parse(sys.argv[i]))

outname = sys.argv[len(sys.argv)-1]

sampleNoteSeqs = []
for s in str:
	sampleNoteSeqs.extend(parseNotes(s))

uniqueNotes = []
for l in sampleNoteSeqs:
	uniqueNotes.extend(list(set(l)))
uniqueNotes = list(set(uniqueNotes))

N = LearnPSA(0.2, 10, 6, uniqueNotes)
for seq in sampleNoteSeqs:
	N.add_sample(" ".join(seq))
N.generate_pst()

states, transition, nextstate = N.generate_psa()

notes = []
for i in range(0,10):
	notes.append(N.generate_run(states, transition, nextstate, 1500).split(" "))

sampleDurationSeqs = []
for s in str:
	sampleDurationSeqs.extend(parseDurations(s))


uniqueDurations = []
for l in sampleDurationSeqs:
	uniqueDurations.extend(list(set(l)))
uniqueDurations = list(set(uniqueDurations))

D = LearnPSA(0.2, 10, 3, uniqueDurations)
for seq in sampleDurationSeqs:
	D.add_sample(" ".join(seq))
D.generate_pst()

states, transition, nextstate = D.generate_psa()
durations = []
for i in range(0,10):
	durations.append(D.generate_run(states, transition, nextstate, 1500).split(" "))
'''

observationSeqs = []
for s in str:
	observationSeqs.extend(parseNotesWithDurations(s))

helper = HMMHelper(sampleNoteSeqs, sampleDurationSeqs, observationSeqs)
start, go, out = helper.initializeHMM()
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
for k in xrange(0,10):
	a = stream.Part()
	full = stream.Stream()

	for i in xrange(0, len(notes[k])):
		d = duration.Duration(float(durations[k][i]))
		#d = duration.Duration(float(helper.emissionSelector(model.Emm, notes[k][i])))
		n = note.Note(notes[k][i])
		n.volume.velocity = 127
		n.duration = d
		a.append(n)
	
	full.append(a)

	mf = midi.translate.streamToMidiFile(full)
	file = outname+k.__str__()+'.mid'
	mf.open(file, 'wb')
	mf.write()
	mf.close()

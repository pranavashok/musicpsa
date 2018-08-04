from hmmpy.HMM.calculator import HMM
from music21 import *
from pypsa.psa.LearnPSA import LearnPSA
from operator import itemgetter
import random
from collections import Counter
import numpy
import sys

def getNotes(s, queue):
	str = queue.pop(0)
	for ele in str.elements:
		if type(ele).__name__ == 'Score' or type(ele).__name__ == 'Part' or type(ele).__name__ == 'Voice' or type(ele).__name__ == 'Measure':
			queue.append(ele)
	for ele in queue:
		if ele.hasElementOfClass('Note'):
			sample = []
			for e in ele:
				if type(e).__name__ == 'Note':
					sample.append(e.nameWithOctave)
			if len(sample) > 10:
				s.append(sample)
		else:
			getNotes(s, queue)

def parseNotes(midifile):
	s = []
	queue = [midifile]
	getNotes(s, queue)
	return s

def getDurations(s, queue):
	str = queue.pop(0)
	for ele in str.elements:
		if type(ele).__name__ == 'Score' or type(ele).__name__ == 'Part' or type(ele).__name__ == 'Voice' or type(ele).__name__ == 'Measure':
			queue.append(ele)
	for ele in queue:
		if ele.hasElementOfClass('Note'):
			sample = []
			for e in ele:
				if type(e).__name__ == 'Note':
					sample.append(e.duration.quarterLength.__str__())
			if len(sample) > 10:
				s.append(sample)
		else:
			getNotes(s, queue)

def parseDurations(midifile):
	s = []
	queue = [midifile]
	getDurations(s, queue)
	return s


def getNotesWithDurations(s, queue):
	str = queue.pop(0)
	for ele in str.elements:
		if type(ele).__name__ == 'Score' or type(ele).__name__ == 'Part' or type(ele).__name__ == 'Voice' or type(ele).__name__ == 'Measure':
			queue.append(ele)
	for ele in queue:
		if ele.hasElementOfClass('Note'):
			obs = []
			for e in ele:
				if type(e).__name__ == 'Note':
					obs.append((e.nameWithOctave, e.duration.quarterLength.__str__()))
			if len(obs) > 10:
				s.append(obs)
		else:
			getNotesWithDurations(s, queue)

def parseNotesWithDurations(midifile):
	observationSeqs = []
	queue = [midifile]
	getNotesWithDurations(observationSeqs, queue)
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

N = LearnPSA(0.2, 10, 3, uniqueNotes)
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

for k in xrange(0,10):
	a = stream.Part()
	full = stream.Stream()
	#ins = instrument.Violin()
	#a.append(ins)
	for i in xrange(0, len(notes[k])):
		d = duration.Duration(float(durations[k][i]))
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
from music21 import *
import sys

def getNotes(full, queue):
	str = queue.pop(0)
	for ele in str.elements:
		if type(ele).__name__ == 'Score' or type(ele).__name__ == 'Part' or type(ele).__name__ == 'Voice' or type(ele).__name__ == 'Measure':
			queue.append(ele)
	for ele in queue:
		if ele.hasElementOfClass('Note'):
			a = stream.Stream()
			for e in ele:
				if type(e).__name__ == 'Note':
					if e.offset > int(sys.argv[2]) and e.offset < int(sys.argv[3]):
						n = e
						n.duration = e.duration
						a.append(n)
			full.append(a)
		else:
			getNotes(full, queue)

def trim(midifile):
	full = stream.Stream()
	queue = [midifile]
	getNotes(full, queue)
	return full

if len(sys.argv) < 5:
	sys.stderr.write("Usage: python trim.py file.mid 25 100 out.mid")
	sys.exit(1)


full = trim(converter.parse(sys.argv[1]))

mf = midi.translate.streamToMidiFile(full)
mf.open(sys.argv[4], 'wb')
mf.write()
mf.close()
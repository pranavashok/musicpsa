from music21 import *
import sys

str = corpus.parse(sys.argv[1])

name = sys.argv[1].split("/")

o = midi.translate.streamToMidiFile(str)
o.open(name[len(name)-1]+".orig.mid", 'wb')
o.write()
o.close()
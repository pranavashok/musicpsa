README
=======

What is this project?
---------------------

We explored composition of music using the mathematical model of Prediction Suffix Automata. When given an input sequence(s), a model is created from which random runs (following the transition probabilities, ofcourse) give new compositions.

The project was started with western music in mind (pianos, chords and notes etc). The Hidden Markov Model (HMM) portion was written so as to associate chords with notes. But it turned out difficult to extract chords and notes and generate compositions in which the chords weren't in *complete* sync with the notes (i.e. in our results, chords were struck every time a note was played). Soon afterward, we abandoned further improvements in the western side and focused on Hindustani/Carnatic music. With certain tweaks to the PSA, we were able to generate pretty good results for simple raags and average results for more complex raags (like the durbari).

Further research with the help of a person knowledgable in music is required to perfect this.

We concluded that the mathematical model of Prediction Suffix Automata, could model the randomness in simple music with sufficient perfection.

(Please note that the generate.py file deals only with PSA and the deprecated folder contains the may contain code which uses HMM)

Overview of the folders
------------------------

* The pypsa and hmmpy folders contain the python packages we created for PSA and HMM simulations.

* snippets folder contains small bits of code which may come helpful during modification

* deprecated folder contains files which were previously used to generate the music. Some may work without modification, some with modification and some maybe specific to a certain structure of midi files.

* outputs folder contains some of the outputs generated in earlier runs

* originals folder contains some of the original midi files. More originals can be found in the music21 corpus library.

* resources contains some files which we referred to while coding this project

* reports contains the project reports, presentations as well as some notes we made during the project


Requirements
------------

- Python 3
- Music21 - can be installed with `pip3 install music21` (http://web.mit.edu/music21)
- hmmpy - included (previously https://github.com/sharathgeorge/Hmm-python)
- pypsa - included (previously https://github.com/pranavashok/pypsa)


Usage
-----

`python generate.py input-track.midi [input-track2.midi input-track3.midi ...] output.midi`


Contact
-------

In case you want to contact us - for feedback/improvements/issues/whatsoever, please drop a mail to
pranavashok [at] gmail [dot] com

and we'll be glad to get back to you.

Thanks for showing interest in this project!


License
-------

Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported 

You are free:

to Share — to copy, distribute and transmit the work
to Remix — to adapt the work

Under the following conditions:

Attribution — You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work).

Noncommercial — You may not use this work for commercial purposes.

Share Alike — If you alter, transform, or build upon this work, you may distribute the resulting work only under the same or similar license to this one.


Credits
-------

Schulze, Walter (2010). A formal language theory approach to music generation. Master's Thesis. http://hdl.handle.net/10019.1/4157.

The sample inputs sorted and categorized by the Thaat name in the originals folder was taken from - http://www.cse.iitk.ac.in/users/tvp/music/

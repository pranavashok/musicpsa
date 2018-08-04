N = LearnPSA(0.2, 10, 3, uniqueNotes)
for seq in sampleNoteSeqs:
	N.learn_sample(" ".join(seq))

states, transition, nextstate = N.generate_psa()

#Run 100 times and print the frequency of differenct outcomes
run = []
for i in range(0,1):
	run.append(N.generate_run(states, transition, nextstate, 80))

unique = {}
for item in run:
    unique[item] = unique.get(item, 0) + 1

freq_table = sorted(unique.items(), key=itemgetter(1), reverse=True)

selector = random.randrange(0, len(freq_table)-1)

notes = freq_table[selector][0].split(" ")
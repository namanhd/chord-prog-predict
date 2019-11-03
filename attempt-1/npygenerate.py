import prepfuncs
import os
import numpy as np

SUBSEQLEN = 16
MIDIDIR = "midifiles/bossa"

for root, dirs, files in os.walk(MIDIDIR):
    fileslist = list(files)

master_melody_array = np.empty((0 ,SUBSEQLEN,12))
master_chords_array = np.empty((0 ,SUBSEQLEN,12))
master_output_array = np.empty((0 ,12))

for file in fileslist:
    mel_subseqs, cho_subseqs_trunc, cho_popped = prepfuncs.getArraysFromMidi(MIDIDIR + "/" + file, SUBSEQLEN, True)
    master_melody_array = np.concatenate((master_melody_array, mel_subseqs))
    master_chords_array = np.concatenate((master_chords_array, cho_subseqs_trunc))
    master_output_array = np.concatenate((master_output_array, cho_popped))

print(master_chords_array.shape)

np.save('input_melody.npy', master_melody_array)
np.save('input_chords.npy', master_chords_array)
np.save('output_chords.npy', master_output_array)

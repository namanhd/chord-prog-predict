import functions as prepfuncs
import os
import numpy as np

SUBSEQLEN = 8

for root, dirs, files in os.walk("midifiles"):
    fileslist = list(files)

master_melody_array = []
master_chords_array = []
master_output_array = []

for file in fileslist:
    mel_subseqs, cho_subseqs_trunc, cho_popped = prepfuncs.getArraysFromMidi("midifiles/"+file, SUBSEQLEN)
    master_melody_array += mel_subseqs
    master_chords_array += cho_subseqs_trunc
    master_output_array += cho_popped

master_melody_array_np = np.array(master_melody_array)
master_chords_array_np = np.array(master_chords_array)
print(master_chords_array_np.shape)
master_output_array_np = np.array(master_output_array)

np.save('input_melody.npy', master_melody_array_np)
np.save('input_chords.npy', master_chords_array_np)
np.save('output_chords.npy', master_output_array_np)

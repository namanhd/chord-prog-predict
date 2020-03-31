import argparse
from keras.models import load_model

import prepfuncs
import predfuncs

SUBSEQLEN = 8
CHORDLEN = 3
#MODELFILE = "chordprogpredict-fix-fullmodelsave-0-4775-nobnorm.h5"
#MODELFILE = "chordprogpredict-fix-fullmodelsave-0-7223-beforebigdrop-nobnorm.h5"
MODELFILE = "chordprogpredict-fix-fullmodelsave-0-6750-bigdrop-nobnorm.h5"
#argparse thing for command line args
argparser = argparse.ArgumentParser(description="Predicts a chord progression, given a melody and at least {0} seed chords for the first {0} melody notes. Other than that, you can add your own chords under other notes you want to harmonize yourself.".format(SUBSEQLEN - 1))
argparser.add_argument("inputfilepath", type=str, help="Input midi path + name")
argparser.add_argument("outputfilepath", type=str, help="Output midi path + name")
argparser.add_argument("-k","--key", type=str, default="", help="Key of the piece. Lowercase note name for minor, uppercase for major. # for sharp, - for minor. e.g. b- is B flat minor.")
argparser.add_argument("-e","--empty", type=bool, default=False, help="Flag for predicting from empty, no seed chords")
cmdargs = argparser.parse_args()

print("-------Loading prediction model...-------")
model = load_model(MODELFILE)
print("Done loading prediction model")

if not cmdargs.key == "": #if a custom key is specified, then parse the midi using that key
    fullmelody, fullchords, fulltimestamps, scorekey = prepfuncs.getArraysFromMidi(cmdargs.inputfilepath, SUBSEQLEN, False, key=cmdargs.key)
else: #otherwise, just try to id the key (find it in the midi or by analyzer)
    fullmelody, fullchords, fulltimestamps, scorekey = prepfuncs.getArraysFromMidi(cmdargs.inputfilepath, SUBSEQLEN, False)
#len of these lists are the same!

print([predfuncs.findOnes(note) for note in fullmelody])

#this func edits the fullchords list in-place to include all the predicted chords,
print("Currently predicting chords based on the key: " + scorekey.tonicPitchNameWithCase + " " + scorekey.mode)
if cmdargs.empty == True:
    predfuncs.seedFirstChords(fullmelody, fullchords, SUBSEQLEN)

predfuncs.predictOnArrays(model, fullmelody, fullchords, SUBSEQLEN, CHORDLEN) 
#...then using the key found above, this reconstructs a music21 score of the piece WITH the predicted chords, and writes the score to a midi file
print("Writing result to midi file")
predfuncs.writeToMidi(cmdargs.outputfilepath, fulltimestamps, fullmelody, fullchords, scorekey) 

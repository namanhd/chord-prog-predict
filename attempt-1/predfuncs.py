import music21
import numpy as np

def getChordArrayFromPrediction(pred, chordlen):
    #pred will have the form of a 12-elem np array with vals between 0 and 1.
    # we get the 3 highest ranking notes (but can be 2 or 5, based on CHORDLEN)
    returnchord = np.repeat(0,12)
    indices = np.argpartition(-pred[0], chordlen - 1)[:chordlen] #this gets the indices of the top n values in the arr (n=chordlen)
    #print(pred)
    for i in indices:
        returnchord[i] = 1
    return returnchord #type np ndarray

#this is to attempt to predict without any seed chords:
#"seed" the first SUBSEQLEN chords using the melody notes themselves, no sugar on top
def seedFirstChords(melodylist, chordslist, subseqlen):
    for i in range(subseqlen):
        chordslist[i] = melodylist[i]

#iterate over subsequences of the melody and the chords. Update the chord list on the fly with the newly predicted chord. Then predict on the next subseq.
def predictOnArrays(kerasmodel, melodylist, chordslist, subseqlen, chordlen):
    melodyarray = np.array(melodylist)
    chordsarray = np.array(chordslist)
    print(chordsarray.shape)
    for i in range(len(melodyarray) - subseqlen + 1):
        ipred = i + subseqlen - 1 #index of the chord to be predicted in the fullchords list
        if np.any(chordsarray[ipred]) == False:    #if there is no chord in the fullchords list at that position, (all 0 values)
            inputchordsubseq = np.expand_dims(chordsarray[i:(ipred + 1)], axis=0) #the shape is now (1,subseqlen, 12)
            inputmelodysubseq = np.expand_dims(melodyarray[i:(ipred + 1)], axis=0)
            nextchord = kerasmodel.predict([inputchordsubseq, inputmelodysubseq])  
            #(there's a +1 because the splice end index isn't inclusive). 
            #there's expand dims (that wraps the one subseq in a []) because the model expects a list of subseqs, even if we only have a single subseq.)
            chordsarray[ipred] = getChordArrayFromPrediction(nextchord, chordlen) #let that position be the chord predicted using this subsequence's melody and chords
        else: #if the user has already set a chord for that melody note,
            continue #then keep going until we hit a blank chord
    chordslist[:] = list(chordsarray)
            
def getMusicObjectFrom12ToneDegrees(degs, scorekey):
    if len(degs) == 1:
        objInC = music21.pitch.Pitch(degs[0])
    else:
        objInC = music21.chord.Chord(degs) 
    #music21 Chord and Pitch classes both support instantiation with a single/a list of 12tone pitch class numbers, with C=0
    
    #we just need to now transpose the Pitch or Chord in C=0 to our key
    fromCtoKey = music21.interval.Interval(noteStart = music21.pitch.Pitch("c4"), noteEnd = scorekey.tonic)
    objInKey = objInC.transpose(fromCtoKey)
    return objInKey

def findOnes(mylist): #this returns list of pitch class nums between 0 and 11 from a one-hot note or chord representation
    return [i for i in range(len(mylist)) if mylist[i]==1]

def getMusicObjectsFromOneHots(melody_or_chord_list, scorekey):    
    returnlist = []
        
    for noc in melody_or_chord_list: #noc is a note-or-chord
        twelvetonedegs = findOnes(noc) #list of nums between 0 and 11 indicating which indices has a 1
        returnlist.append(getMusicObjectFrom12ToneDegrees(twelvetonedegs, scorekey))
    
    return returnlist
    
#write to midi once we've predicted a chord for all melody notes            
def writeToMidi(outputfile, timestamps, melodylist, chordslist, scorekey):
    myScore = music21.stream.Score()
    melodyPart = music21.stream.Voice()
    chordsPart = music21.stream.Voice()
    durations = [j-i for i, j in zip(timestamps[:-1], timestamps[1:])]
    durations.append(1) #default length of 1 quarter-note for the last note
    
    melodyPitches = getMusicObjectsFromOneHots(melodylist, scorekey)
    chordsChords = getMusicObjectsFromOneHots(chordslist, scorekey)
    
    for t in zip(durations, melodyPitches, chordsChords):
        melodyNote = music21.note.Note(t[1]) #turn Pitch object into Note object with duration
        melodyNote.quarterLength = t[0]
        melodyNote.octave = 6
        melodyPart.append(melodyNote)
        
        chordChord = music21.chord.Chord([t[2]]) #since some Chord predictions may end up being just a single note, we make sure all are Chord objs.
        if len(chordChord.pitches) == 0:
            chordChord = music21.note.Rest()
        chordChord.quarterLength = t[0]
        chordsPart.append(chordChord)
    
    myScore.insert(timestamps[0], melodyPart)
    myScore.insert(timestamps[0], chordsPart)
    
    #myScore.show("text")
    
    
    myScore.write("midi", outputfile)
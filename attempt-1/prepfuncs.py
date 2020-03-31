import music21
import numpy as np

def get12ToneDegreeFromPitch(scorekey, mypitch):
    return mypitch.transpose(music21.interval.Interval(noteStart = scorekey.tonic, noteEnd = music21.pitch.Pitch("C4"))).pitchClass

def getNotestacks(myscore, **kwargs):
    key_analyzer = music21.analysis.discrete.KrumhanslSchmuckler()
    analyzed_key = key_analyzer.getSolution(myscore)
    
    chdscore = myscore.chordify()
    
    def getNotestacksShape(score): #returns shape tuple
        allnoteschords = score.recurse().notes
        current_max_cols = 1
        for elem in allnoteschords:
            if len(elem.pitches) > current_max_cols:
                current_max_cols = len(elem.pitches)
        return (len(allnoteschords), current_max_cols)
    
    if "key" in kwargs:
        try:
            scorekey = music21.key.Key(kwargs["key"]) #if possible, get the manually entered key
        except:
            scorekey = analyzed_key #otherwise, just use the key received from the analysis
    else:
        scorekey = analyzed_key
    
    notestacks_shape = getNotestacksShape(chdscore)
    timestamps = np.empty((notestacks_shape[0],))
    notestacks = np.negative(np.ones(getNotestacksShape(chdscore), dtype=int))
    # empty notes are given a pitch class number of -1, hence the negative ones.
    
    ind = 0
    
    for elem in chdscore.flat:
        
        elemtype = type(elem)
            
        if elemtype == music21.key.Key and "key" not in kwargs: #if there was no manual key, but key is specified in the parsed midi:
            scorekey = elem
            
        elif elemtype == music21.chord.Chord:
            timestamps[ind] = elem.offset
            chordtones = elem.pitches
            notestacks[ind] = np.array([get12ToneDegreeFromPitch(scorekey, p) for p in chordtones][::-1] + [-1 for _ in range(notestacks_shape[1] - len(chordtones))] )
            #get the pitch classes of the chord. Pad with -1s to match the thickest chord's width.
            ind += 1
                
    return notestacks, timestamps, scorekey

def getMelodyAndChordsFromNotestacks(notestacks):
    copied_notestacks = np.copy(notestacks) #so that we don't pop and mutate the original scoredict
    nsshape = copied_notestacks.shape
    melodylist = np.negative(np.ones( (nsshape[0],), dtype=int ))
    for ts in range(nsshape[0]):
        for partnum in range(nsshape[1]): #for each part
            if copied_notestacks[ts][partnum]==-1:
                continue
            else:
                melodylist[ts] = copied_notestacks[ts][partnum]
                copied_notestacks[ts][partnum] = -1
                #got the top note as melody? now exit the loop and leave the other notes alone.
                break
        #by this point, all the melody notes will have been popped out of the scoredict.
        #the surviving copied_notestacks is now the chordslist
    
    return melodylist, copied_notestacks

def subseq(bigseq, n, innerdim): #returns subsequences of bigseq, each of length n, containing items with length innerdim
    outshape = (len(bigseq) - n + 1, n, innerdim)
    outarr = np.empty(outshape, dtype=int)
    for i in range(outshape[0]):
        outarr[i] = np.array(bigseq[i:i+n])
    return outarr
    
def getTruncatedChordSeqs(chordsubseqs):
    copied_chordsubseqs = np.copy(chordsubseqs)
    poppedchordslist = np.zeros((copied_chordsubseqs.shape[0],12), dtype=int)
    for css in range(len(copied_chordsubseqs)):
        poppedchordslist[css] = np.copy(copied_chordsubseqs[css][-1])
        copied_chordsubseqs[css][-1]= np.zeros((12,), dtype=int)
    
    return copied_chordsubseqs, poppedchordslist

def getOneHotFrom12ToneDegrees(notes_12t):
    notevector = np.zeros((13,), dtype=int)
    notevector[notes_12t] = 1
    return notevector[:12] 
    #the last elem is cut off; it was just padding for the -1 vals that corresponded to no note
    
def convertToOneHots(melOrChordList):
    copied_list = np.copy(melOrChordList)
    list_1h = np.empty((len(copied_list),12), dtype=int)
    for i in range(len(copied_list)):
        list_1h[i] = getOneHotFrom12ToneDegrees(copied_list[i])
    return list_1h
    
def getArraysFromMidi(midipath, subseqlen, isfortraining, **kwargs): #accepts kwarg: key="some key". e.g. getScoreDict(myscore, key='C#') for C#maj, or key='c' for C minor 
    print("-------Processing file {}--------".format(midipath))
    print("Parsing")
    myscore = music21.converter.parse(midipath)
    
    print("Getting note stacks")
    notestacks, timestamps, scorekey = getNotestacks(myscore, **kwargs)
    
    print("Extracting melody and chords")
    melodylist, chordslist = getMelodyAndChordsFromNotestacks(notestacks)
    
    print("Generating one hot encoded subsequences for melody")
    melodylist_1h = convertToOneHots(melodylist)
    mel_subseqs = subseq(melodylist_1h, subseqlen, 12)
    
    print("Generating one hot encoded subsequences of chords")
    chordslist_1h = convertToOneHots(chordslist)
    cho_subseqs = subseq(chordslist_1h, subseqlen, 12)
    
    print("-------Done. Returning result-----")
    
    if isfortraining == True:
        cho_subseqs_trunc, poppedchords = getTruncatedChordSeqs(cho_subseqs)
        return mel_subseqs, cho_subseqs_trunc, poppedchords
    else: #if we're using this func to convert midis to predict chords instead of to preproc training data
        return melodylist_1h, chordslist_1h, timestamps, scorekey

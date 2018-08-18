# # music21 and data preprocessing tests

import music21
import copy

def get12ToneDegreeFromKeyNoteAcc(scorekey, note_degree_acc):
    if note_degree_acc[1] is not None: #if there is an accidental
        decimal_degree = note_degree_acc[0]+note_degree_acc[1].alter/2 #get the decimal reprsnt of the note
    else:
        decimal_degree = note_degree_acc[0]
                
                #we have to be careful here, because the 12-tone degree that our n.5 "scale degree" corresponds to 
                #depends on if its a major or minor scale
                # for major, the 3.5 becomes 4 (III# is IV), 7.5 becomes 1 (VII# is I)
                # for natural minor, the 2.5 becomes 3 (II# is III), 5.5 becomes 6 (V# is VI)
                
    if scorekey.mode == 'major':
        tonemap = {1.0: 0,
                   1.5: 1,
                   2.0: 2,
                   2.5: 3,
                   3.0: 4,
                   3.5: 5,
                   4.0: 5,
                   4.5: 6,
                   5.0: 7,
                   5.5: 8,
                   6.0: 9,
                   6.5: 10,
                   7.0: 11,
                   7.5: 11
                  }
    
    elif scorekey.mode == 'minor':
        tonemap = {1.0: 0,
                   1.5: 1,
                   2.0: 2,
                   2.5: 3,
                   3.0: 3,
                   3.5: 4,
                   4.0: 5,
                   4.5: 6,
                   5.0: 7,
                   5.5: 8,
                   6.0: 8,
                   6.5: 9,
                   7.0: 10,
                   7.5: 11
                  }
                  
    return tonemap[decimal_degree]


# The second one is to create a dictionary:  
# key = all unique timestamps across all four parts. Essentially, each key value pair will be a NOTE STACK in the midi at that key timestamp.
# If a part does not have any notes in some timestamp (this happens when there's a short duration when not all of the parts play notes together), we can pad them with special -1 notes which will encode into a Completely Zeroed Out Note Vector.


def getScoreDict(myscore):
    noteschords = [music21.note.Note, music21.chord.Chord]
    
    
    parts_dicts = []
    parts_times = []
    for scorepart in myscore.parts:
        #for each part, build a dictionary {time: note}
        part_dict = {}
        for thing in scorepart:
            thingtype = type(thing)
            
            if thingtype == music21.key.Key:
                scorekey = thing
            
            if thingtype == noteschords[0]:
                #part_dict[thing.offset] = thing
                part_dict[thing.offset] = get12ToneDegreeFromKeyNoteAcc(scorekey, scorekey.getScaleDegreeAndAccidentalFromPitch(thing.pitches[0]))
        
        parts_dicts.append(part_dict)
        parts_times.append(list(part_dict.keys()))
    
    all_times = list(set().union(*parts_times))
    all_notes = []
    
    for ts in all_times:
        notes_at_ts = [] #this list has 4 elements, each is a note played at this time ts or -1 if no note found in a part.
        for partnum in range(len(parts_dicts)):
            if ts in parts_times[partnum]: #if this timestamp is present in this part
                notes_at_ts.append(parts_dicts[partnum][ts]) #add into the timestamp the note played at that time in that part
            else:
                notes_at_ts.append(-1)
        
        all_notes.append(notes_at_ts)
    
    all_times_index = [n for n in range(len(all_times))]
    
    return dict(zip(all_times_index, all_notes))


# After we obtain the dict of `{timestamp: [list of note_12t_deg played by each part]}`, we can then parse it as follows
# - Pop out the first Note in the list (which corresponds to the soprano melody) and append it to a new list, which will be the melody. If the soprano note is a -1, then we grab the alto one, and if that one is -1, we go to tenor and so on.
# - The remaining Notes in the list at timestamp will form the Chord for that timestamp.


def getMelodyAndChordsFromScoreDict(scoredict):
    copied_scoredict = copy.deepcopy(scoredict) #so that we don't pop and mutate the original scoredict
    
    melodylist = []
    for ts in copied_scoredict:
        for partnum in range(len(copied_scoredict[ts])):
            if copied_scoredict[ts][partnum]==-1:
                continue
            else:
                melodylist.append(copied_scoredict[ts].pop(partnum))
                #got the top note as melody? now exit the loop and leave the other notes alone.
                break
        #by this point, all the melody notes will have been popped out of the scoredict.
    
    chordslist = []
    for ts in copied_scoredict:
        chordslist.append(copied_scoredict[ts])
        
    return melodylist, chordslist


# Format the melodynotes, and chords, so that we get melody subsegments, and chords subsegments of length n. That should be 5 or 6.

def subseq(bigseq, n):
    return list(map(list, zip(*(bigseq[i:] for i in range(n)))))


# We need to do something extra with the chord subsequences. The last chord should be "hidden" i.e. all turned into -1 values, so that we have something for the LSTM to predict.

def getTruncatedChordSeqs(chordsubseqs):
    copied_chordsubseqs = copy.deepcopy(chordsubseqs)
    poppedchordslist = []
    for css in copied_chordsubseqs:
        poppedchordslist.append(css[-1])
        css[-1]= [0 for _ in css[-1]]
    
    return copied_chordsubseqs, poppedchordslist


# Creating the one-hot encoding scheme

def getOneHotFrom12ToneDegrees(notes_12t):
    notevector = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    if type(notes_12t)==list:
        for n in notes_12t:
            if not n == -1:
                notevector[n]=1
    else:
        notevector[notes_12t]=1
    
    return notevector



def convertToOneHots(melOrChordList):
    copied_list = copy.deepcopy(melOrChordList)
    list_1h = []
    for thing in copied_list:
        list_1h.append(getOneHotFrom12ToneDegrees(thing))
    
    return list_1h
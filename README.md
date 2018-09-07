# chord-prog-predict
Machine learning model for predicting chords given a melody.

#### Current stage of work:  
Writing and testing preprocessing code; preparing dataset

## Dataset and preprocessing

~~For the sake of simplicity and consistency, I'm using a collection of four-part chorale carol and hymn pieces, taken from this [gem of a collection](http://www.learnchoralmusic.co.uk/Carols%20&%20Anthems/Carols-complist.html#list)~~

I found that those carol MIDIs although are laid out in a straightforward manner, are mixed up with drums and have uninteresting harmonies for the most part.  
Switching over to a dataset of midis of Final Fantasy music (a cut down set of MIDI files taken from the dataset of [this project](https://github.com/Skuldur/Classical-Piano-Composer))

Parsing the MIDIs is done using the `music21` library from MIT

The idea is as follows  
- First the midi is parsed through music21. The parts (voices), their notes, and even the *key* are automatically detected with quite a decent accuracy.
- All the notes are turned into integers from 0 to 11 representing the 12 tones in an octave. This encoding is not absolute pitch class (as in, C=0, C#=1 and so on), but relative to the key, so if the key is A major, then A=0, A#=1 and so on.  
  This is done to prevent different interpretations of different notes in separate pieces despite them doing the same job in their respective keys.
- Then, using the timestamps provided by the parsed output, a list of "note stacks" is formed.
- From the note stacks, all the top notes are put into a melody list, and the rest become the chords.
- A one-hot encoding of 12 dimensions (12 tones) is then used. At this point, the chords are combined into one vector with multiple 1s representing the notes in that chord, while the notes are singular 1s in the chord.
- All the subsequences in the big list of melody and chord are listed (so for ABCDE we would have ABC, BCD, CDE for example). The subsequence length right now is `n=5`, but that may change.
- The last chord in a paired chord-melody pair is knocked away and put into an OUTPUT list. This is what the model will be predicting.

The model is given a melody of `n` notes, and corresponding `n-1` chords, and it must predict the `n`th chord to go with that last unaccopanied note.

It's similar to what is done for LSTM text prediction: subsequences of text, where the model predicts the next character/word based on the current subsequence of letters/words.

## Model

No actual work done here yet, but will use Keras and probably be very similar to the LSTM text prediction problems.
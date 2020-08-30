# chord-prog-predict
Machine learning model for predicting chords given a melody.

#### Current stage of work:  
Wrapping up Attempt 1.

Demo video available here: https://youtu.be/8DVZycYlY7g

Trained model file used in demo is here: https://drive.google.com/file/d/15HZvQaD8n0HS0CLTXJSNIdFnIcYyPCs6/view?usp=sharing

## Dataset and preprocessing

~~For the sake of simplicity and consistency, I'm using a collection of four-part chorale carol and hymn pieces, taken from this [gem of a collection](http://www.learnchoralmusic.co.uk/Carols%20&%20Anthems/Carols-complist.html#list)~~

I found that those carol MIDIs although are laid out in a straightforward manner, are mixed up with drums and have uninteresting harmonies for the most part.  
Now using a dataset of midis of Final Fantasy music (a cut down set of MIDI files taken from the dataset of [this project](https://github.com/Skuldur/Classical-Piano-Composer)) plus some added MIDIs from my own collection (of mostly music from Pokemon games)

Parsing the MIDIs is done using the `music21` library from MIT

The idea is as follows  
- First the midi is parsed through music21. The parts (voices), their notes, and even the *key* are automatically detected with quite a decent accuracy.
- All the notes are turned into integers from 0 to 11 representing the 12 tones in an octave. This encoding is not absolute pitch class (as in, C=0, C#=1 and so on), but relative to the key, so if the key is A major, then A=0, A#=1 and so on.  
  This is done to prevent different interpretations of different notes in separate pieces despite them doing the same job in their respective keys.
- Then, using the timestamps provided by the parsed output, a list of "note stacks" is formed.
- From the note stacks, all the top notes are put into a melody list, and the rest become the chords.
- A one-hot encoding of 12 dimensions (12 tones) is then used. At this point, the chords are combined into one vector with multiple 1s representing the notes in that chord, while the notes are singular 1s in the chord.
- All the subsequences in the big list of melody and chord are listed (so for ABCDE we would have ABC, BCD, CDE for example). The subsequence length right now is `n=8`, but that may change.
- The last chord in a paired chord-melody pair is knocked away and put into an OUTPUT list. This is what the model will be predicting.

I have finally moved on to using music21's `chordify` function, which greatly simplifies the process of getting stacks of notes.

The model is given a melody of `n` notes, and corresponding `n-1` chords, and it must predict the `n`th chord to go with that last unaccopanied note.

This is similar to what is done for LSTM text prediction problems: the model is given subsequences of text, and predicts the next character/word based on the current subsequence of letters/words.

## Model

Attempts **0** and **1** at this problem uses a model that consists of 2 input layers (one for the chords subsequences, one for the melody subsequences) that are then concatenated. This goes through 2 LSTM layers (each with its own Dropout), which then finally goes to a Dense layer for predicting the final 12-dim vector corresponding to the missing chord.

## Result assessment:

Attempt **0** was done using my original faulty preprocessing functions which sometimes didn't get the correct pitch class for flat notes. (This has since been fixed in Attempt 1 by fully using music21's `pitchClass` and `transpose` instead).

Nevertheless, even with this somewhat wrong dataset, the model was able to pick up patterns with the I, IV, and V chords and place them under plausible notes. It sometimes even uses II minor chords properly. However, it seems to have a fixation with sus4 chords and repeating I chords excessively; this probably reflects the overwhelming abundance of these simple chords in the dataset. In Attempt **1**, I have spruced up the dataset so that the model may learn more complex features, however it is still limited by its note representations.

Since chord progression generation is a highly subjective task in terms of quality, a lower-loss model does **not** mean a more "pleasant-sounding" one for human ears. In the demo video above, I use a model that contains weights achieved somewhere in the middle of the training process;
the loss being not too low but also not too high means that it avoids "safe" chord choices, which will likely be correct with more test samples but will sound more musically boring, but it also "knows" enough to be able to generate reasonable chords as opposed to just random notes.

### Future plans

This model and approach currently completely ignores which chord tones are bass notes/roots of their chords; these bass notes are unfortunately extremely important to how a chord progression sounds. A correct set of notes in a chord progression may still sound terrible because the bass note is never switched up or the inversions are all wrong/the same.

Future models should encode chord data in terms of a bass note (a 12-dim vector) alongside an array of intervals (also a 12-dim vector, corresponding to 12 possible intervals starting from the bass note upwards. May also be a 24-dim vector in order to incorporate chords that stretch over more than an octave). This way, a better variety of chords as well as correct bass note placements for each chord may be encoded and learned.
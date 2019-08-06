#paths in this file are paths on my google drive because this was run on a Google Colab notebook
"""### Reading the npy files"""

import numpy as np

bigpath = ""
chords = np.load(bigpath+"input_chords.npy")
melody = np.load(bigpath+"input_melody.npy")
labelchords = np.load(bigpath+"output_chords.npy")

print(chords.shape)
print(melody.shape)
print(labelchords.shape)

"""## Building the Keras model"""

from keras.models import Model
from keras.layers import Input, Concatenate, Dense, Dropout, LSTM

chords_input = Input(shape = (chords.shape[1],chords.shape[2]), name="X_chords_input")

melody_input = Input(shape = (melody.shape[1],melody.shape[2]), name="X_melody_input")

concat_input = Concatenate()([chords_input, melody_input])
print(concat_input.shape)

lstmlayer1 = LSTM(256, return_sequences = True)(concat_input)
lstmlayer1 = Dropout(0.2)(lstmlayer1)
print(lstmlayer1.shape)

lstmlayer2 = LSTM(256)(lstmlayer1)
lstmlayer2 = Dropout(0.2)(lstmlayer2)
classifier = Dense(12, activation = "softmax")(lstmlayer2)

"""Wrapping everything into a single Model"""

final_model = Model(inputs = [chords_input, melody_input], outputs = classifier)

"""### Run this section before compiling model if loading from checkpointed weights"""

#final_model.load_weights("")

"""### Compiling the model"""

final_model.compile(loss = "categorical_crossentropy", optimizer = "adam")
print(final_model.summary())

from keras.callbacks import ModelCheckpoint
checkpointer = ModelCheckpoint(filepath="checkpts/chordprogpredict-fix.{epoch:02d}-{loss:.3f}.hdf5", monitor = "loss", save_best_only = True, mode="min")
callback_list = [checkpointer]

"""### Fitting the model

Fit the model from scratch, or continue from weights loaded from a checkpoint.
If our purpose for loading weights in (above) is just to export a new model for prediction tests, then we can skip fitting and go to saving the full model (below)
"""

final_model.fit([chords, melody], labelchords,
                epochs = 140,
                batch_size = 96,
                callbacks = callback_list)


"""### Saving the full model

Saving checkpoints during training only saves the weights, not the model architecture.
This full model save, however, does, and allows predicting right off the bat without requiring a `model.compile()`
"""
#the path is on google drive because this code was run on a Google Colab notebook

final_model.save("checkpts/fullmodelsaves/chordprogpredict-fix-fullmodelsave-new.h5")

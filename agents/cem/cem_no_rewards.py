'''
  Keras model discussing Categorical Cross Entropy loss.
  from https://www.machinecurve.com/index.php/2019/10/22/how-to-use-binary-categorical-crossentropy-with-keras/#categorical-crossentropy-keras-model

  why use crossentropy loss and not hinge loss? That is, multiclass hinge loss can both be used as well instead of binary and multiclass crossentropy.
  see here: https://www.machinecurve.com/index.php/2019/10/17/how-to-use-categorical-multiclass-hinge-with-keras/

  also check out: https://www.machinecurve.com/index.php/2019/10/06/how-to-use-sparse-categorical-crossentropy-in-keras/

  not implemented yet because dunno how to implement rewards into this
'''
import tensorflow as tf
from tensorflow import keras
#from tensorflow.keras import layers
#import keras
from tf.keras.models import Sequential
from tf.keras.layers import Dense
from tf.keras.utils import to_categorical
#import matplotlib.pyplot as plt
import numpy as np
#from sklearn.datasets import make_blobs
#from mlxtend.plotting import plot_decision_regions

# observation size, len(game.observation()
feature_vector_shape = 33
input_shape = (feature_vector_shape,)
num_classes = 4 # actions

model = Sequential()
model.add(Dense(12, input_shape=input_shape, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(8, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(num_classes, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.adam(lr=0.001), metrics=['accuracy'])

# use for whole batch
#history = model.fit(X_training, Targets_training, epochs=30, batch_size=5, verbose=1, validation_split=0.2)
model.predict(observation)
model.train_on_batch(observation)

"""
scores = train(episodes=10, step=2000, pretrained=0, noise=0) # old

fig = plt.figure()
plt.plot(np.arange(1, len(reward_list) + 1), reward_list)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()
"""
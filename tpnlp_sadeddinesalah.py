# -*- coding: utf-8 -*-
"""TPNLP-SadeddineSalah.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EOvMaRZC0vx1J-Zc4qZJq-Y132hCyVlp
"""

#chargement de données
!pip install kaggle

!kaggle datasets download -d lakshmi25npathi/imdb-dataset-of-50k-movie-reviews

!unzip imdb-dataset-of-50k-movie-reviews.zip

from os import replace
#pretraitement des données
import pandas as pd
dataframe = pd.read_csv("IMDB Dataset.csv")
dataframe["review"] = dataframe["review"].str.replace(r'<[^<>]*>', '', regex=True)
dataframe["review"] = dataframe["review"].str.replace(r'[^\w\s]','',regex=True)
dataframe ["review"]= dataframe["review"].str.lower()
dataframe

import nltk
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from collections import Counter
nltk.download('wordnet')
#lematization
lemmatizer = nltk.stem.WordNetLemmatizer()
dataframe["review"]=dataframe["review"].apply(lambda x: ' '.join([lemmatizer.lemmatize(mot) for mot in x.split()]))
#calculer le nombre de mots qui sont repetées au moins 5 fois
all_text = ' '.join(dataframe['review'])
words = all_text.split()
word_counts = Counter(words)
words_at_least_5 = [word for word, count in word_counts.items() if count >= 5]
#tokenization and transform to sequence
tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(dataframe["review"])
X = tokenizer.texts_to_sequences(dataframe["review"])
X = pad_sequences(X, maxlen=200, padding='post')
print(len(words_at_least_5))

from sklearn.model_selection import train_test_split
import tensorflow as tf
import numpy as np
#encodage de labels
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(dataframe["sentiment"])
list(le.classes_)
dataframe["sentiment"] = pd.Series(le.transform(dataframe["sentiment"]))
X_train, X_test, y_train, y_test = train_test_split(X, dataframe["sentiment"], test_size=0.2, random_state=42)



from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

model_lstm = Sequential([
    Embedding(input_dim=10000, output_dim=128,input_length=200),
    LSTM(128, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=0.0001)
model_lstm.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model_lstm.fit(X_train,y_train, epochs=10,validation_data=(X_test,y_test),batch_size=64,callbacks=[early_stopping, lr_scheduler])

#avec attention
from tensorflow.keras.layers import Attention,Input,LSTM, Attention, Dense, Dropout,Embedding
from tensorflow.keras.models import Model
input_layer = Input(shape=(200,))
embedding_layer = Embedding(input_dim=10000, output_dim=128)(input_layer)
lstm_layer = LSTM(128, return_sequences=True)(embedding_layer)
attention_layer = Attention()([lstm_layer, lstm_layer])
lstm_layer_2 = LSTM(64)(attention_layer)
dropout_layer = Dropout(0.2)(lstm_layer_2)
output_layer = Dense(1, activation='sigmoid')(dropout_layer)

model_lstm_attention = Model(inputs=input_layer, outputs=output_layer)
model_lstm_attention.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model_lstm_attention.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), batch_size=64, callbacks=[early_stopping, lr_scheduler])

#sauvegarde
model_lstm.save('sentiment_analysis_model.h5')


#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This script:

Extracts face encodings from training images.
Saves image features, labels, and addresses into a Pandas DataFrame.
Stores this DataFrame in a pickle file.
"""

import pickle
import glob
import face_recognition
import pandas as pd

training_folder = './features_dataset/'  # Training images folder
training_imgs = glob.glob(training_folder + '/*.jpg')  # Get all training images

df = pd.DataFrame(columns=['labels', 'features', 'imgs_addrs'])  # DataFrame to store extracted features

counter = 0
for img in training_imgs:
    img_name_parts = img.split('/')[len(img.split('/'))-1].split('_')  # Extract label from filename
    img_lbl = img_name_parts[0] + '_' + img_name_parts[1]

    image = face_recognition.load_image_file(img)  # Load image
    face_landmarks_list = face_recognition.face_encodings(image)  # Extract face encodings
    
    for fl in face_landmarks_list:
        df.loc[counter] = [img_lbl, fl, img]  # Store label, features, and path
        counter += 1

# Save training database as a pickle file
with open('pickle_labels/training_database.pkl', 'wb') as f:
    pickle.dump(df, f)

    

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This script:

Loads face encodings from test images.
Compares them against the trained model using face recognition.
Evaluates precision and recall for face recognition performance.
"""

import pickle
import pandas as pd
import glob
import face_recognition
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load training feature database
with open('pickle_labels/training_database.pkl', 'rb') as f:  
    df = pickle.load(f)

testing_folder = 'test_dataset/'  # Path to test images
testing_imgs = glob.glob(testing_folder + '/*.jpg')  # Get test images

testing_recall = []
testing_prec = []

for img in testing_imgs:
    img_name_parts = img.split('/')[len(img.split('/'))-1].split('_')  # Extract image label
    img_lbl = img_name_parts[0] + '_' + img_name_parts[1]

    image = face_recognition.load_image_file(img)  # Load image
    face_landmarks_list = face_recognition.face_encodings(image)  # Extract face encodings

    for fl in face_landmarks_list:
        results = face_recognition.compare_faces(df['features'].tolist(), fl, tolerance=0.552)  # Compare with database

        retriv = [i for i in range(len(results)) if results[i]]  # Retrieve matched indexes
        
        all_labels = df['labels'].tolist()  # Get labels
        prec_match = sum(1 for i in range(len(results)) if results[i] and all_labels[i] == img_lbl)  # Count correct matches
        
        testing_prec.append(float(prec_match) / sum(results) if sum(results) else 0)  # Calculate precision
        
        recall_match = all_labels.count(img_lbl)  # Total correct matches
        testing_recall.append(float(prec_match) / recall_match)  # Calculate recall

# Print final precision & recall scores
print 'Precision : ' + str(np.mean(testing_prec) * 100)+' %'
print 'Recall : ' + str(np.mean(testing_recall) * 100)+' %'

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This script:

Loads the labeled dataset from labels.pkl.
Splits images into training and testing datasets.
Moves one image per person (if at least 4 exist) to the testing dataset.
"""

import pickle
import os

# Load the labeled dataset
with open('pickle_labels/labels.pkl', 'rb') as f:  
    persons_names = pickle.load(f)

# Define training and testing folder paths
training_features = './dataset/features_dataset/'
testing_features = './dataset/test_dataset/'

# Split dataset into training & testing
for per_name in persons_names.keys():
    counter = len(persons_names[per_name])  # Count images for each person
    for i in range(counter):
        if i == counter - 1 and counter  >= 4:  # Move last image if person has 4+ images
            os.system('cp -r  '+ persons_names[per_name][i] + ' ' + testing_features)
        else:  # Otherwise, keep in training dataset
            os.system('cp -r  '+ persons_names[per_name][i] + ' ' + training_features)


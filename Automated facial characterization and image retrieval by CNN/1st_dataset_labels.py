#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This script:

Reads all image file names from a dataset folder.
Extracts person names from the file names.
Groups images by person name.
Saves the mapping (persons_names) into a pickle file.
"""

import pickle
import glob

dataset_folder = './dataset/knn_dataset'  # Define dataset path
imgs_name = glob.glob(dataset_folder+'/*.jpg')  # Get all image file names

persons_names = {}  # Dictionary to store person-wise images
for img in imgs_name:
   try:
       img_name_parts = img.split('/')[len(imgs_name[0].split('/'))-1].split('_')  # Extract name parts from filename
       if img_name_parts[0] + '_' + img_name_parts[1] in persons_names.keys():  # Check if name exists in dictionary
           persons_names[img_name_parts[0] + '_' + img_name_parts[1]].append(img)  # Append image to person's list
       else:
           persons_names[img_name_parts[0] + '_' + img_name_parts[1]] = [img]  # Create new entry
   except:
        print(img)  # Print file name if an error occurs

# Save the extracted labels in a pickle file
with open('pickle_labels/labels.pkl', 'wb') as f:
    pickle.dump(persons_names, f)

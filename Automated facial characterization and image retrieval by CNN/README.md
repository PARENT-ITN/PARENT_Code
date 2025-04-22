The PARENT project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie Innovative Training Network 2020, Grant Agreement N° 956394.

DOI Citation

1.1. Shah, S. T. H., Shah, S. A. H., Qureshi, S. A., Di Terlizzi, A., & Deriu, M. A. (2023). Automated facial characterization and image retrieval by convolutional neural networks. Frontiers in Artificial Intelligence, 6, 1230383, doihttps://doi.org/10.3389/frai.2023.1230383.

1.2. Shah, Syed Taimoor Hussain, Shah, Syed Adil Hussain, Shah, Syed Baqir Hussain, Qureshi, Shahzad Ahmad, Di Terlizzi, Angelo, Deriu, Marco Agostino (2023). Automated Facial Characterization and Image Retrieval by Convolutional Neural Networks. Zenodo, Version 1.0. Published December 20, 2023. DOI: https://doi.org/10.5281/zenodo.14865793.

Introduction

Facial characterization and image retrieval are crucial in many areas such as healthcare, criminology, and forensic analysis. The provided code is designed to develop an efficient method for facial feature extraction, characterization, and identification using a hybrid deep learning approach combining GoogleNet and AlexNet models. The system preprocesses images using classical computer vision techniques and then applies deep learning for robust feature extraction and retrieval of the relevant images.

Purpose of the Code

The provided Python scripts serve the following objectives:

Dataset Preprocessing: Converts raw image datasets into structured datasets suitable for training and testing.

Feature Extraction: Extracts and stores facial features using a combination of deep learning and classical computer vision techniques.

Training & Testing: Implements a facial recognition model based on GoogleNet and AlexNet.

Cosine Similarity Matching: Computes feature similarity for query images using cosine similarity.

K-Nearest Neighbors (KNN) Feature Matching: Matches images based on KNN.

Automated Image Retrieval: Retrieves facial images with similar features from a stored database.

How to Use the Code

1. Directory Structure

Ensure the following directory structure before execution:

Facial_Recognition/
│── 1st_dataset_labels.py
│── 2nd_img_training_testing.py
│── 3rd_training_features_database.py
│── 4th_testing_imgs.py
│── 5th_cosine_similarity.py
│── 6th_KNN_featureMatching.py
│── pickle_labels/
│    ├── labels.pkl
│    ├── training_database.pkl

2. Running the Code

Step 1: Generate Dataset Labels

python 1st_dataset_labels.py

Step 2: Prepare Training & Testing Data

python 2nd_img_training_testing.py

Step 3: Extract Features & Train Database

python 3rd_training_features_database.py

Step 4: Test Images for Facial Recognition

python 4th_testing_imgs.py

Step 5: Compute Cosine Similarity for Image Matching

python 5th_cosine_similarity.py

Step 6: Perform KNN Feature Matching

python 6th_KNN_featureMatching.py

Required Libraries

Since the code is developed for Python 2.7, the following libraries should be installed:

NumPy (pip install numpy)

OpenCV (pip install opencv-python)

scikit-learn (pip install scikit-learn)

matplotlib (pip install matplotlib)

Pandas (pip install pandas)

Pickle (Included in Python standard library)

OS (Included in Python standard library)

Acknowledgment

Thank you for using this facial recognition and retrieval system. If you use this code in your research, kindly cite the reference provided above. This work presents a robust approach to automated facial characterization and image retrieval, leveraging hybrid deep learning techniques for accurate and efficient performance.

For further details, refer to the original publication:https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1230383/full

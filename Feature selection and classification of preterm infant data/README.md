### Overview

This project applies feature selection and classification techniques to preterm infant data. Two feature selection methods were used: clinician-based selection and mutual information. Multiple classification models were evaluated with cross-validation and hyperparameter tuning.

## Feature Selection

- **Clinician-Based Selection**: Experts reduced features to 22 based on medical relevance.

- **Mutual Information**: Features were retained if their mutual information coefficient exceeded that of a generated random variable.

## Classification Models

Evaluated models include: Logistic Regression, AdaBoost, Decision Trees, Random Forest, Gaussian Naive Bayes, K-Nearest Neighbors (KNN)

## Experimental Design

- **Evaluation:** Leave-one-out cross-validation (LOO-CV) and 5-fold grid search tuning.

- **Metrics:** Accuracy, Recall, ROC AUC.

- **Implementation:** Python 3.11.6, scikit-learn 1.4.

- **Handling Data Imbalance**: SMOTE-NC: Synthetic oversampling to balance classes.

### Requirements

## Install dependencies:

pip install scikit-learn numpy pandas
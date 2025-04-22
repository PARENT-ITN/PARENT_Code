The PARENT project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie Innovative Training Network 2020, Grant Agreement N° 956394.

Cite: Shah, Syed Taimoor Hussain, Shah, Syed Adil Hussain, Panagiotopoulos, Konstantinos, Pigueiras-del-Real, Janet, Shah, Syed Baqir Hussain, Deriu, Marco Agostino (2025). Xception-based Facial Expression Recognition with SHAP-Driven Explainability. Zenodo, Version 1.0. Published February 5, 2025. DOI: https://doi.org/10.5281/zenodo.14809941.

# Explainable Facial Expression Recognition: Leveraging Xception and SHAP for Model Interpretability

This repository contains code to test a trained Xception-based facial expression recognition model and generate explainability visualizations using SHAP (SHapley Additive exPlanations). The main script `test_and_explainability.py` runs the model on a test image and produces explainability heatmaps.

## Repository Structure
.
├── assets/ # Folder for storing additional assets (e.g., sample images)
├── Data/ # Folder for input test images to be analyzed
├── explainability/ # Output directory for explainability heatmaps
├── variables/ # Contains model variables/weights
├── fingerprint.pb # Model fingerprint file
├── keras_metadata.pb # Keras model metadata
├── saved_model.pb # TensorFlow SavedModel file
└── test_and_explainability.py # Main script for testing & explainability

Copy

## Prerequisites
- Python 3.9
- Required Python libraries (listed in `requirements.txt`)

### Install Dependencies
Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
requirements.txt
The requirements.txt file contains the following dependencies for Python 3.9:

Copy
numpy==1.24.3
matplotlib==3.7.1
tensorflow==2.14.0
opencv-python==4.8.1.78
mediapipe==0.9.1.0
shap==0.44.0
lime==0.2.0.1
scikit-image==0.22.0
plotly==5.18.0
Pillow==9.5.0
omnixai==1.3.1
tf-keras-vis==0.8.6
cmapy==0.6.0
How to Run the Code
1. Prepare Input Image
Place your test image in the Data/ folder (e.g., Data/test_image.jpg)

2. Set Up Parameters
The run_shap_explainer() function requires 3 arguments:

python
Copy
def run_shap_explainer(
    input_shape_299,       # Input shape for model (e.g., (299, 299, 3))
    test_img_path,         # Path to test image (from Data/ folder)
    save_explain_dir       # Directory to save outputs (explainability/)
)
3. Run the Script
Execute the following command in your terminal:

bash
Copy
python test_and_explainability.py
Example Usage
Modify the following variables in test_and_explainability.py before running:

python
Copy
# Set these variables at the beginning of the script
input_shape = (299, 299, 3)  # Example input shape for Xception models
test_image_path = "Data/your_test_image.jpg"  # Replace with your image name
output_dir = "explainability/"  # Directory for saving SHAP visualizations
Then call the function:

python
Copy
run_shap_explainer(
    input_shape_299=input_shape,
    test_img_path=test_image_path,
    save_explain_dir=output_dir
)
Output
SHAP explanation plots will be saved in the explainability/ folder

Includes both raw and processed explainability heatmaps

Output filenames: shap_explanation.png, processed_shap.png

Notes
Ensure TensorFlow model files (saved_model.pb, variables/, etc.) are in the root directory

Supported image formats: JPG, PNG

For best results, use images resized to match input_shape

SHAP might take 1-2 minutes to generate explanations depending on your hardware

Troubleshooting
If you get shape mismatches, verify input_shape matches the model's expected input

If images aren't found, check paths relative to repository root

Ensure write permissions for explainability/ directory
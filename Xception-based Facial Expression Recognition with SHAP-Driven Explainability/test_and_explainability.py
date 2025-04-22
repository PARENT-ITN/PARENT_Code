# Import required libraries
import os  # For file and directory operations
import numpy as np  # For numerical computations and array handling
import matplotlib.pyplot as plt  # For plotting and visualization
import tensorflow as tf  # TensorFlow framework for deep learning
from tensorflow.keras.models import load_model  # Load pre-trained models
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # Preprocess image data
from tensorflow.keras.applications.xception import preprocess_input as xception_preprocess_input  # Xception model preprocessing
import cv2  # OpenCV for image processing
import mediapipe as mp  # MediaPipe for facial landmark detection
import shap  # SHAP library for explainability and model interpretation

# Set Matplotlib visualization parameters for better plots
plt.rcParams.update({
    'font.size': 15,           # Set font size for all text elements
    'lines.linewidth': 1.5,    # Adjust the thickness of plotted lines
    'axes.labelsize': 15,      # Set font size for axis labels
    'savefig.dpi': 300,        # Save figures with high resolution (300 DPI)
    'legend.fancybox': False,  # Disable rounded edges for legend boxes
    'legend.fontsize': 15,     # Set font size for legend text
    'xtick.labelsize': 15,     # Set font size for x-axis tick labels
    'ytick.labelsize': 15,     # Set font size for y-axis tick labels
    'patch.linewidth': 1.5,    # Define thickness of shape boundaries
    'legend.frameon': False    # Remove borders around the legend
})


###############################################################################
###########################Functions###########################################
###############################################################################

def read_img_file_mediapipe(img_path, input_shape = (299, 299, 3)):
    """
    Reads an image and processes it using MediaPipe to extract facial landmarks.
    The image is then masked and resized to the specified input shape.
    """
    try:
        mp_face_mesh = mp.solutions.face_mesh
        
        # Key points for facial landmarks
        Face_KP =[10,109,67,103,54,21,162,127,234,93,132,58,172,\
                  136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454,356,389,251,284,332,297,338];    
        
        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
                        refine_landmarks=True,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5
                        ) as face_mesh:
            frame = cv2.imread(img_path)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_h, img_w = frame.shape[:2]
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                mesh_points=np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])
                mask = np.ones((img_h, img_w), dtype=np.uint8) *255
        
                cv2.fillPoly(mask, [mesh_points[Face_KP]], 0)
        
                mask = np.dstack((mask,mask,mask))
        
                masked_image = cv2.bitwise_or(mask,frame)
                
                masked_image = cv2.resize(masked_image, input_shape[:2])
                
                return masked_image         
    except:
        print("Image is having issues")


#############################Preprocess Function##########################
def f(X):
    """
    Preprocesses the input data and returns the model's predictions.
    """
    global best_xception_model
    temp_datagen = ImageDataGenerator(rescale=1./255, 
                                      preprocessing_function=xception_preprocess_input)
    tmp = temp_datagen.standardize(X.copy())
    return best_xception_model(tmp)

#############################Checking Files################################
def check_and_create_directories(file_path):
    """
    Checks if a directory exists, and if not, creates it.
    """
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

#######################Generator for Testing the Model#########################
input_shape_299 = (299, 299, 3)
test_img_path = r'./Data/30490.jpg'
model_saving_dir = r'./'
save_explain_dir = r'./explainability/'

## Model Loading
best_xception_model = tf.keras.models.load_model(model_saving_dir)
models_list = [best_xception_model]

#######################################################################
#########################SHAP##########################################
#######################################################################
def run_shap_explainer(input_shape, test_img_path, save_explain_dir):
    """
    Runs the SHAP explainer on a test image and saves the explanation plot.
    """
    test_image =  read_img_file_mediapipe(test_img_path)
    
    full_save_dir = save_explain_dir + test_img_path.split('/')[-1].split('.')[0] + '_shap_image.jpg'
    check_and_create_directories(full_save_dir)
    
    # define a masker that is used to mask out partitions of the input image, this one uses a blurred background
    masker_blur = shap.maskers.Image("blur(128,128)", input_shape)
    
    # By default the Partition explainer is used for all  partition explainer
    explainer = shap.Explainer(f, masker_blur, output_names=['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise'])        
    
    # here we use 500 evaluations of the underlying model to estimate the SHAP values
    shap_values = explainer(test_image[np.newaxis, :], max_evals
    
    plt.clf()
    plt.xticks(fontsize=14, rotation=90)
    shap.image_plot(shap_values, show=False)   
    plt.savefig(full_save_dir, format = "jpg", dpi = 600, bbox_inches = 'tight')
    

####################################################################################
##################################SHAP##############################################
####################################################################################
run_shap_explainer(input_shape_299, test_img_path, save_explain_dir)

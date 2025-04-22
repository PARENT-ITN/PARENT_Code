import pickle
import os
import glob
import numpy as np
import face_recognition
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.metrics import confusion_matrix, recall_score, precision_score

df = ''
with open('pickle_labels/training_database.pkl') as f:  
    df = pickle.load(f)
    
testing_folder = '/home/adil/Desktop/fdirs/dataset/test_dataset/'
testing_imgs = glob.glob(testing_folder + '/*.jpg')

labels = []
label_dic = {}
counter = 0

tp = 0
fn = 0
fp = 0

for dff in df['labels'].tolist():
    if (dff not in label_dic.keys()):
        label_dic[dff] = counter
        labels.append(counter)
        counter += 1
    else:
        labels.append(label_dic[dff])    
        
clf = NearestCentroid()
clf.fit(df['features'].tolist(), labels)


test_fl = []
test_lb = []

for img in testing_imgs:
    img_name_parts = img.split('/')[len(img.split('/'))-1].split('_')
    img_lbl = img_name_parts[0] + '_' + img_name_parts[1]
   
    test_lb.append(label_dic[img_lbl])
    
    image = face_recognition.load_image_file(img)
    land_mark = face_recognition.face_encodings(image)
    if len(land_mark) > 0:    
       # test_fl.append(land_mark[0].reshape(1,128))
       test_fl.append(land_mark[0])
results = clf.predict(test_fl)
print results
cm = confusion_matrix(test_lb[0:len(results)], results)
print "Precision : " + str(precision_score(test_lb[0:len(results)], results, average='weighted') *100)+' %'
print "Recall : " + str(recall_score(test_lb[0:len(results)], results, average='weighted') * 100)+' %'

"""
prec = []
for i in range(cm.shape[0]):
    temp = 0
    for j in range(cm.shape[1]):
        temp += cm[j, i]
    
    if (temp > 0):
        prec.append(cm[i, i] / temp)
    else:
        prec.append(0)

print "Precision : " + np.average(prec)

recal = []
for i in range(cm.shape[0]):
    temp = 0
    for j in range(cm.shape[1]):
        temp += cm[i, j]
    
    if (temp > 0):
        recal.append(cm[i, i] / temp)
    else:
        recal.append(0)
print "Recal : " + np.average(recal)
"""       
        

 #       print len(results)
 

"""
    if label_dic[index] == img_lbl:
                
        tp++
    else:
        
    
            
 #       image2 = Image.open(df['imgs_addrs'][i])
 #       axarr[img_counter/4,img_counter%4].imshow(image2)
 #       img_counter += 1
     #   image1.show()
      #  image2.show()
       # print results
        
  #      plt.show()
  
        recall_match = 0
        for lbl in all_labels:
            if img_lbl == lbl:
                recall_match += 1
        testing_recall.append(float(prec_match)/recall_match)
        break
        

print 'Precision : ' + str(np.mean(testing_prec))
print 'Recall : ' + str(np.mean(testing_recall))
"""
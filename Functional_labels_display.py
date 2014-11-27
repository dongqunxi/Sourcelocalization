########################################################################################
# Display ROIs based on MNE estimates and select dipoles for causality analysis
#######################################################################################
import mne, os, sys
from surfer import Brain
import random

try:
    subject = sys.argv[1]
except:
    print "Please run with input file provided. Exiting"
    sys.exit()

subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + subject#Set the data path of the subject
#subject_id = subject
subject_id = 'fsaverage'
hemi = "split"
#surf = "smoothwm"
surf = 'inflated'

#label_fname='/home/qdong/freesurfer/subjects/101611/func_labels/new_func_temporal-lh.label'
brain = Brain(subject_id, hemi, surf)
list_dirs = os.walk(subject_path + '/func_labels/standard/') 
#list_dirs = os.walk(subject_path + '/func_labels/') 
#list_dirs = os.walk(subject_path + '/func_labels/merged')
#list_dirs = os.walk(subjects_dir + subject) 
#color = ['#990033', '#9900CC', '#FF6600', '#FF3333', '#00CC33']
#/home/qdong/freesurfer/subjects/101611/func_labels/stim_func_superiortemporal-lh.label

for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label = mne.read_label(label_fname)
        brain.add_label(label, color='red')
        #if f[0:3]=='tri':
        #   #continue
        #    brain.add_label(label, color='green', alpha=0.5, subdir=root)
        #elif f[0:3]=='res':
        #    brain.add_label(label, color='yellow', alpha=0.5, subdir=root) 
        #else:
        #    brain.add_label(label, color='red',  subdir=root) 
#mne.gui.coregistration()      

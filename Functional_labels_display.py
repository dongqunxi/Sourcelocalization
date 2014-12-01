########################################################################################
# Display ROIs based on MNE estimates and select dipoles for causality analysis
#######################################################################################
import mne, os
from surfer import Brain
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + 'fsaverage'
labels_dir = subject_path + '/func_labels/common/'
subject_id = 'fsaverage'
hemi = "split"
#surf = "smoothwm"
surf = 'inflated'

#label_fname='/home/qdong/freesurfer/subjects/101611/func_labels/new_func_temporal-lh.label'
brain = Brain(subject_id, hemi, surf)
list_dirs = os.walk(labels_dir) 
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label = mne.read_label(label_fname)
        brain.add_label(label, color='red')
        #if f[0:6]=='101611':
        #    brain.add_label(label, color='green', alpha=0.5)
        #elif f[0:6]=='108815':
        #    brain.add_label(label, color='yellow', alpha=0.5) 
        #elif f[0:6]=='109925':
        #    brain.add_label(label, color='blue', alpha=0.5)
        #elif f[0:6]=='110061':
        #    brain.add_label(label, color='cyan', alpha=0.5)
        #elif f[0:6]=='201394':
        #    brain.add_label(label, color='red', alpha=0.5)
        #elif f[0:6]=='202825':
        #    brain.add_label(label, color='magenta', alpha=0.5)
        #else:
        #    brain.add_label(label, color='red',  subdir=root) 
#mne.gui.coregistration()      

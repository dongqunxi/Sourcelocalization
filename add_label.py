from surfer import Brain
import mne
subject_id = 'fsaverage'
hemi = "split"
#surf = "smoothwm"
surf = 'inflated'
brain = Brain(subject_id, hemi, surf)
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + 'fsaverage'
labels_dir = subject_path + '/func_labels/common/'
label_fname= labels_dir + '101611,110061,108815,202825_tri5-rh.label'
label = mne.read_label(label_fname)
brain.add_label(label, color='red')

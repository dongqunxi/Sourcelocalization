import os,mne
import numpy as np
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + 'fsaverage'
list_dirs = os.walk(subject_path + '/func_labels/standard/')
label_list = ['']
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label_list.append(label_fname)
label_list=label_list[1:]
mer_path = subject_path+'/func_labels/merged'
isExists=os.path.exists(mer_path)
if not isExists:
    os.makedirs(mer_path) 
class_list = []
class_list.append(label_list[0]) 
for test_fn in label_list[1:]:
    test_label = mne.read_label(test_fn)
    i = 0
    belong = False
    while (i < len(class_list)) and (belong == False):
        class_label = mne.read_label(class_list[i])
        label_name = class_label.name
        com_label = class_label.copy() 
        if test_label.hemi != class_label.hemi:
            i = i + 1
            continue
        if len(np.intersect1d(test_label.vertices, class_label.vertices)) > 0:
            com_label = test_label + class_label
            if test_label.name.split('_')[0] not in label_name:
                label_name = '%s,' %(test_label.name.split('_')[0]) + label_name
            if os.path.dirname(class_list[i]) == mer_path:
                os.remove(class_list[i])
            mne.write_label(mer_path + '/%s' %label_name, com_label)
            print label_name
            class_list[i] = mer_path + '/%s.label' %label_name 
            belong = True
        i = i + 1
    if belong == False:
        class_list.append(test_fn)

import shutil
com_path = subject_path+'/func_labels/common'
list_dirs = os.walk(subject_path + '/func_labels/merged/')
label_list = ['']
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label_list.append(label_fname)
label_list=label_list[1:]

for fn_label in label_list:
    fn_name = os.path.basename(fn_label)
    subjects = (fn_name.split('_')[0]).split(',')
    if len(subjects) >= 4:          
        shutil.copy(fn_label, com_path)
        
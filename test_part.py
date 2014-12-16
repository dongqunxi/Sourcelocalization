
import source_localization
subjects_dir = '/home/qdong/freesurfer/subjects/'
for subject in ['101611','110061','109925', '201394', '202825', '108815']:
    #subject='110061'
    subject_path = subjects_dir + subject#Set the data path of the subject
    raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
    basename = raw_fname.split('-')[0]
    res_name, tri_name = 'STI 013', 'STI 014'
    #basename='/home/qdong/freesurfer/subjects/108815/MEG/108815_audi_cued'
    
   
    ##################################################                                                                                 
    # ROIs_definition                               #  
    #################################################
    #fn_stc_tri = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger,morph'
    #fn_stc_res = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response,morph'
    #source_localization.ROIs_definition(fn_stc_tri, tri=tri_name)
    #source_localization.ROIs_definition(fn_stc_res, tri=res_name)                                    
    ##Merging the overlapped labels and standardlize the size of them
    #source_localization.ROIs_Merging(subject)
    fn_stc_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger,morph' 
    source_localization.ROIs_standardlization(fn_stc_both, size=8)

source_localization.group_ROI()
source_localization.com_ROI(5)

import mne, os
import numpy as np
mer_path='/home/qdong/freesurfer/subjects/fsaverage/func_labels/merged'
list_dirs = os.walk(mer_path)
label_list = ['']
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label_list.append(label_fname)
label_list = label_list[1:]
class_list = []
class_list.append(label_list[0]) 
for test_fn in label_list[1:]:
    test_label = mne.read_label(test_fn)
    i = 0
    belong = False
    while (i < len(class_list)) and (belong == False):
        class_label = mne.read_label(class_list[i])
        label_name = class_label.name
        if test_label.hemi != class_label.hemi:
            i = i + 1
            continue
        if len(np.intersect1d(test_label.vertices, class_label.vertices)) > 0:
            com_label = test_label + class_label
            pre_test = test_label.name.split('_')[0]
            pre_class = class_label.name.split('_')[0]
            if pre_test != pre_class:
                pre_class += ',%s' %pre_test
                pre_class = list(set(pre_class.split(',')))
                new_pre = ''
                for pre in pre_class[:-1]:
                    new_pre += '%s,' %pre
                new_pre += pre_class[-1]
                label_name = '%s_' %new_pre + class_label.name.split('_')[1]
            if os.path.dirname(class_list[i]) == mer_path:
                os.remove(class_list[i])
            if os.path.dirname(test_fn) == mer_path:
                os.remove(test_fn)
            mne.write_label(mer_path + '/%s.label' %label_name, com_label)
            print label_name
            class_list[i] = mer_path + '/%s.label' %label_name 
            belong = True
        i = i + 1
    if belong == False:
        class_list.append(test_fn)
print len(class_list), len(label_list)
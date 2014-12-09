
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
    source_localization.ROIs_standardlization(fn_stc_both, size=8.0)

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
mer_path = subject_path+'/func_labels/merged/'
isExists=os.path.exists(mer_path)
if not isExists:
    os.makedirs(mer_path) 

l_label = len(label_list)
#i=0
#j=l_label - 1
#while i <= l_label-1:
#    label1 = mne.read_label(label_list[i])
#    com_label = label1.copy()
#    while j >= 0:
#        label2 = mne.read_label(label_list[j]) 
#        j = j - 1
#        if label1.hemi != label2.hemi:
#            continue
#        if len(np.intersect1d(label1.vertices, label2.vertices)) > 0:
#            com_label = label1 + label2
#            com_label.name = '%s,' %(label2.name.split('_')[0]) + com_label.name 
#            
#    subjects = (label1.name.split('_')[0]).split(',')
#    if len(set(subjects)) >= 4:          
#        mne.write_label(mer_path + '%s' %com_label.name, com_label)
#    i = i + 1

for fn_label1 in label_list:
    label1 = mne.read_label(fn_label1) 
    com_label = label1.copy()
    label_name = label1.name
    for fn_label2 in label_list:
        label2 = mne.read_label(fn_label2) 
        if label1.hemi != label2.hemi:
            continue
        if len(np.intersect1d(label1.vertices, label2.vertices)) > 0:
            com_label = label1 + label2
            if label2.name.split('_')[0] not in label_name:
                label_name = '%s,' %(label2.name.split('_')[0]) + label_name
    subjects = (label_name.split('_')[0]).split(',')
    if len(set(subjects)) >= 4:          
        mne.write_label(mer_path + '%s'  %label_name, com_label)
   # mne.write_label(mer_path + '%s' %label1.name, com_label)

list_dirs = os.walk(mer_path)
label_list = ['']
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        label_list.append(label_fname)
label_list=label_list[1:]
com_path = subject_path+'/func_labels/common/'
isExists=os.path.exists(com_path)
if not isExists:
    os.makedirs(com_path) 



            
            
    subjects = (label1.name.split('_')[0]).split(',')
    if len(set(subjects)) >= 4:          
        mne.write_label(mer_path + '%s' %com_label.name, com_label)
    i = i + 1
#i=0
#j=l_label - 1
#while i <= l_label-1:
#    label1 = mne.read_label(label_list[i])
#    com_label = label1.copy()
#    while j >= 0:
#        label2 = mne.read_label(label_list[j]) 
#        j = j - 1
#        if label1.hemi != label2.hemi:
#            continue
#        if len(np.intersect1d(label1.vertices, label2.vertices)) > 0:
#            #com_label = label1 + label2
#            #pre1 = label1.name.split('_')[0].split(',')
#            #pre2 = label2.name.split('_')[0].split(',')
#            #pre = pre1 + pre2
#            #pre = list(set(pre))
#            #com_name = pre[0]
#            #for sub in pre[1:]:
#            #    com_name += ',%s' %sub
#            #label_name = '%s_' %com_name + label1.name.split('_')[1]
#    mne.write_label(com_path + '%s'  %label_name, com_label)
#    i = i + 1

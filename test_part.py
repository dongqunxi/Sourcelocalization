
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
    fn_stc_tri = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger,morph'
    fn_stc_res = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response,morph'
    source_localization.ROIs_definition(fn_stc_tri, tri=tri_name)
    source_localization.ROIs_definition(fn_stc_res, tri=res_name)                                    
    #Merging the overlapped labels and standardlize the size of them
    source_localization.ROIs_Merging(subject)
    fn_stc_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger,morph' 
    source_localization.ROIs_standardlization(fn_stc_both)

import os,mne
import numpy as np
subject_path = subjects_dir + 'fsaverage'
list_dirs = os.walk(subject_path + '/func_labels/')
#list_dirs = os.walk(subjects_dir + subject) 
#color = ['#990033', '#9900CC', '#FF6600', '#FF3333', '#00CC33']
#/home/qdong/freesurfer/subjects/101611/func_labels/stim_func_superiortemporal-lh.label
tri_list = ['']
res_list = ['']
for root, dirs, files in list_dirs: 
    for f in files:
        label_fname = os.path.join(root, f) 
        if f.split('_')[1][0:3]=='tri':
            tri_list.append(label_fname)
        elif f.split('_')[1][0:3]=='res': 
            res_list.append(label_fname)

tri_list=tri_list[1:]
res_list=res_list[1:]

mer_path = subject_path+'/func_labels/merged/'
isExists=os.path.exists(mer_path)
if not isExists:
    os.makedirs(mer_path) 
    
com_list=['']        
for fn_tri in tri_list:
    tri_label = mne.read_label(fn_tri) 
    com_label = tri_label.copy()
    for fn_res in res_list:
        res_label = mne.read_label(fn_res) 
        if tri_label.hemi != res_label.hemi:
            continue
        if len(np.intersect1d(tri_label.vertices, res_label.vertices)) > 0:
            com_label = tri_label + res_label
            tri_label.name += ',%s' %res_label.name
            com_list.append(fn_res)#Keep the overlapped ROIs related with res 
    mne.write_label(mer_path + '%s' %tri_label.name, com_label)

# save the independent res ROIs
com_list=com_list[1:]
ind_list = list(set(res_list)-set(com_list))
for fn_res in ind_list:
    res_label = mne.read_label(fn_res) 
    res_label.save(mer_path + '%s' %res_label.name)

                                        

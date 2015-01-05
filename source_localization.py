# -*- coding: utf-8 -*-
#######################################################
#                                                     #
# small utility function to handle file lists         #
#                                                     #
#######################################################
def get_files_from_list(fin):
    ''' Return files as iterables lists '''
    if isinstance(fin, list):
        fout = fin
    else:
        if isinstance(fin, str):
            fout = list([fin])
        else:
            fout = list(fin)
    return fout
    
subjects_dir = '/home/qdong/freesurfer/subjects/'
MNI_dir = subjects_dir + 'fsaverage/'
fn_inv = MNI_dir + 'bem/fsaverage-ico-4-src.fif' 
subject_id = 'fsaverage'
def make_inverse_operator(fname_evoked):
    from mne.minimum_norm import (apply_inverse)
    import mne, os
    fnlist = get_files_from_list(fname_evoked)
    # loop across all filenames
    for fn_evoked in fnlist:
        #extract the subject infromation from the file name
        name = os.path.basename(fn_evoked)
        subject = name.split('_')[0]
        
        fn_inv = fn_evoked.split('.fif')[0] + '-inv.fif'
        fn_stc = fn_evoked.split('.fif')[0] 
        fn_morph = fn_evoked.split('.fif')[0] + ',morph'
        subject_path = subjects_dir + subject
        fn_cov = subject_path + '/MEG/%s,bp1-45Hz,empty-cov.fif' %subject
        fn_trans = subject_path + '/MEG/%s-trans.fif' %subject
        fn_src = subject_path + '/bem/%s-ico-4-src.fif' %subject
        fn_bem = subject_path + '/bem/%s-5120-5120-5120-bem-sol.fif' %subject
        snr = 3.0
        lambda2 = 1.0 / snr ** 2
        # Load data
        evoked = mne.read_evokeds(fn_evoked, condition=0, baseline=(None, 0))
        fwd = mne.make_forward_solution(evoked.info, mri=fn_trans, src=fn_src, 
                                    bem=fn_bem,fname=None, meg=True, eeg=False, 
                                    mindist=5.0,n_jobs=2, overwrite=True)
        fwd = mne.convert_forward_solution(fwd, surf_ori=True)
        noise_cov = mne.read_cov(fn_cov)
        noise_cov = mne.cov.regularize(noise_cov, evoked.info,
                                    mag=0.05, grad=0.05, proj=True)
        forward_meg = mne.pick_types_forward(fwd, meg=True, eeg=False)
        inverse_operator = mne.minimum_norm.make_inverse_operator(evoked.info, 
                                    forward_meg, noise_cov, loose=0.2, depth=0.8)
        mne.minimum_norm.write_inverse_operator(fn_inv, inverse_operator)
        stcs = dict()
        # Compute inverse solution
        stcs[subject] = apply_inverse(evoked, inverse_operator, lambda2, "dSPM",
                                pick_ori=None)
        # Morph STC
        subject_id = 'fsaverage'
        #vertices_to = mne.grade_to_vertices(subject_to, grade=5)
        #stcs['morph'] = mne.morph_data(subject, subject_to, stcs[subject], n_jobs=1,
        #                              grade=vertices_to)
        stcs[subject].save(fn_stc)
        stcs['morph'] = mne.morph_data(subject, subject_id, stcs[subject], 4, smooth=4)
        stcs['morph'].save(fn_morph)
        fig_out = fn_morph + '.png'
        plot_evoked_stc(subject,stcs, fig_out)
    
import matplotlib.pyplot as plt
def plot_evoked_stc(subject, stcs,fig_out):
    import numpy as np
    names = [subject, 'morph']
    plt.close('all')
    plt.figure(figsize=(8, 6))
    for ii in range(len(stcs)):
        name = names[ii]
        stc = stcs[name]
        plt.subplot(len(stcs), 1, ii + 1)
        src_pow = np.sum(stc.data ** 2, axis=1)
        plt.plot(1e3 * stc.times, stc.data[src_pow > np.percentile(src_pow, 90)].T)
        plt.ylabel('%s\ndSPM value' % str.upper(name))
    plt.xlabel('time (ms)')
    plt.show()
    plt.savefig(fig_out, dpi=100)
    plt.close()
    


def ROIs_definition(fname_stc, tri='STI 014', thr=99):
    import mne, os
    import numpy as np
    fnlist = get_files_from_list(fname_stc)
    # loop across all filenames
    for fn_stc in fnlist:
        #extract the subject infromation from the file name
        name = os.path.basename(fn_stc)
        subject = name.split('_')[0]
        subject_path = subjects_dir + subject
        fun_path = subject_path+'/func_labels/'
        src_inv = mne.read_source_spaces(fn_inv, add_geom=True) 
        if tri == 'STI 014':
            #stc_thr = 85 
            stc_thr = thr
            tri = 'tri'
        elif tri == 'STI 013':
            stc_thr = thr
            tri = 'res'
        stc_morph = mne.read_source_estimate(fn_stc, subject=subject_id)
        src_pow = np.sum(stc_morph.data ** 2, axis=1)
        stc_morph.data[src_pow < np.percentile(src_pow, stc_thr)] = 0. 
        func_labels_lh, func_labels_rh = mne.stc_to_label(stc_morph, src=src_inv, smooth=5,
                                    subjects_dir=subjects_dir, connected=True)    
        # Left hemisphere definition                                                                
        i = 0
        while i < len(func_labels_lh):
            func_label = func_labels_lh[i]
            func_label.save(fun_path+'%s' %(tri)+str(i))
            i = i + 1
        # right hemisphere definition      
        j = 0
        while j < len(func_labels_rh):
            func_label = func_labels_rh[j]
            func_label.save(fun_path+'%s' %(tri)+str(j))
            j = j + 1
                
###################################################################################
#  Merge overlaped ROIs
###################################################################################
def ROIs_Merging(subject):
    import os,mne,shutil
    import numpy as np
    subject_path = subjects_dir + subject
    list_dirs = os.walk(subject_path + '/func_labels/')
    #list_dirs = os.walk(subjects_dir + subject) 
    #color = ['#990033', '#9900CC', '#FF6600', '#FF3333', '#00CC33']
    #/home/qdong/freesurfer/subjects/101611/func_labels/stim_func_superiortemporal-lh.label
    tri_list = ['']
    res_list = ['']
    for root, dirs, files in list_dirs: 
        for f in files:
            label_fname = os.path.join(root, f) 
            if f[0:3]=='tri':
                tri_list.append(label_fname)
            elif f[0:3]=='res': 
                res_list.append(label_fname)
    
    tri_list=tri_list[1:]
    res_list=res_list[1:]
    
    mer_path = subject_path+'/func_labels/merged/'
    isExists=os.path.exists(mer_path)
    if isExists:
        shutil.rmtree(mer_path)
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
####################################################################
# For the special subject, to standardize the size of ROIs
####################################################################
def ROIs_standardlization(fname_stc, size=8.0):
    import mne,os,shutil
    import numpy as np
    fnlist = get_files_from_list(fname_stc)
    # loop across all filenames
    for fn_stc in fnlist:
        stc_morph = mne.read_source_estimate(fn_stc, subject=subject_id)
        
        #extract the subject infromation from the file name
        name = os.path.basename(fn_stc)
        subject = name.split('_')[0]
        subject_path = subjects_dir + subject
        sta_path = MNI_dir+'func_labels/standard/'
        list_dirs = os.walk(subject_path + '/func_labels/merged/') 
        for root, dirs, files in list_dirs: 
            for f in files:
                label_fname = os.path.join(root, f) 
                label = mne.read_label(label_fname)
                stc_label = stc_morph.in_label(label)
                src_pow = np.sum(stc_label.data ** 2, axis=1)
                if label.hemi == 'lh':
                    seed_vertno = stc_label.vertno[0][np.argmax(src_pow)]#Get the max MNE value within each ROI
                    func_label = mne.grow_labels(subject_id, seed_vertno, extents=size, 
                                                hemis=0, subjects_dir=subjects_dir, 
                                                n_jobs=1)
                    func_label = func_label[0]
                    func_label.save(sta_path+'%s_%s' %(subject,f))
                elif label.hemi == 'rh':
                    seed_vertno = stc_label.vertno[1][np.argmax(src_pow)]
                    func_label = mne.grow_labels(subject_id, seed_vertno, extents=size, 
                                                hemis=1, subjects_dir=subjects_dir, 
                                                n_jobs=1)
                    func_label = func_label[0]
                    func_label.save(sta_path+'%s_%s' %(subject,f))
                    
##################################################################################
# Evaluate the group ROIs across subjects:
#  1) merge the overlapped labels across subjects
#  2) select the ROIs coming out in at least am_sub subjects
#################################################################################
def cluster_ROI(mer_path, label_list):
    import mne, os
    import numpy as np
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
    return len(class_list)
    
def group_ROI():
    import os, shutil
    import numpy as np
    subject_path = subjects_dir + 'fsaverage'
    
    #Merge the individual subject's ROIs
    list_dirs = os.walk(subject_path + '/func_labels/standard/')
    label_list = ['']
    for root, dirs, files in list_dirs: 
        for f in files:
            label_fname = os.path.join(root, f) 
            label_list.append(label_fname)
    label_list=label_list[1:]
    mer_path = subject_path+'/func_labels/merged'
    isExists=os.path.exists(mer_path)
    if isExists:
        shutil.rmtree(mer_path)
    os.makedirs(mer_path) 
    cluster_ROI(mer_path, label_list)
    
    #Merge the overlabpped class
    list_dirs = os.walk(mer_path)
    label_list = ['']
    for root, dirs, files in list_dirs: 
        for f in files:
            label_fname = os.path.join(root, f) 
            label_list.append(label_fname)
    label_list=label_list[1:]
    len_class = 0
    while len_class < len(label_list):
        len_class = cluster_ROI(mer_path, label_list)
        list_dirs = os.walk(mer_path)
        label_list = ['']
        for root, dirs, files in list_dirs: 
            for f in files:
                label_fname = os.path.join(root, f) 
                label_list.append(label_fname)
        label_list = label_list[1:]
        #print len_class, len(label_list)
        
def com_ROI(am_sub):
#Select the ROIs more than am_sub subjects        
    import shutil, os
    subject_path = subjects_dir + 'fsaverage'
    com_path = subject_path+'/func_labels/common/'
    mer_path = subject_path+'/func_labels/merged/'
    isExists=os.path.exists(com_path)
    if isExists:
        shutil.rmtree(com_path)
    os.makedirs(com_path) 
    list_dirs = os.walk(mer_path)
    label_list = ['']
    for root, dirs, files in list_dirs: 
        for f in files:
            label_fname = os.path.join(root, f) 
            label_list.append(label_fname)
    label_list=label_list[1:]    
    for fn_label in label_list:
        fn_name = os.path.basename(fn_label)
        subjects = (fn_name.split('_')[0]).split(',')
        if len(subjects) >= am_sub:          
            shutil.copy(fn_label, com_path)
            
    
    
####################################################################
# inverse the epochs of individual raw data and morph into the
# common brain space
####################################################################        
def make_inverse_epochs(fname_raw):
    from mne.minimum_norm import (apply_inverse_epochs)
    import mne, os
    from mne.fiff import Raw
    fnlist = get_files_from_list(fname_raw)
    # loop across all filenames
    for fn_raw in fnlist:
        #extract the subject infromation from the file name
        name = os.path.basename(fn_raw)
        subject = name.split('_')[0]
        
        fn_inv = fn_raw.split('.fif')[0] + '-inv.fif'
        subject_path = subjects_dir + subject
        fn_cov = subject_path + '/MEG/%s,empty-cov.fif' %subject
        fn_trans = subject_path + '/MEG/%s-trans.fif' %subject
        fn_src = subject_path + '/bem/%s-ico-4-src.fif' %subject
        fn_bem = subject_path + '/bem/%s-5120-5120-5120-bem-sol.fif' %subject
        snr = 3.0
        lambda2 = 1.0 / snr ** 2
        # Load data
        raw = Raw(fn_raw, preload=True)
        tmin, tmax = -0.2, 0.5
        events = mne.find_events(raw, stim_channel='STI 014')
        picks = mne.fiff.pick_types(raw.info, meg=True, exclude='bads')
        epochs = mne.Epochs(raw, events, 1, tmin, tmax, proj=False, picks=picks, preload=True, reject=None)
        fwd = mne.make_forward_solution(epochs.info, mri=fn_trans, src=fn_src, 
                                    bem=fn_bem,fname=None, meg=True, eeg=False, 
                                    mindist=5.0,n_jobs=2, overwrite=True)
                                    
        fwd = mne.convert_forward_solution(fwd, surf_ori=True)
        noise_cov = mne.read_cov(fn_cov)
        noise_cov = mne.cov.regularize(noise_cov, epochs.info,
                                    mag=0.05, grad=0.05, proj=True)
        forward_meg = mne.pick_types_forward(fwd, meg=True, eeg=False)
        inverse_operator = mne.minimum_norm.make_inverse_operator(epochs.info, 
                                    forward_meg, noise_cov, loose=0.2, depth=0.8)
        mne.minimum_norm.write_inverse_operator(fn_inv, inverse_operator)
        # Compute inverse solution
        stcs = apply_inverse_epochs(epochs, inverse_operator, lambda2, "dSPM",
                                pick_ori=None)
        stcs_path = MNI_dir+'/stcs/%s' %subject
        isExists=os.path.exists(stcs_path)
        if not isExists:
            os.makedirs(stcs_path) 
        s = 0
        while s < len(stcs):
            stc_morph = mne.morph_data(subject, 'fsaverage', stcs[s], 4, smooth=4)
            stc_morph.save(stcs_path+'/%s_trial%s_fsaverage' %(subject, str(s)), ftype='stc')
            s = s +1
##################################################################
# Causal analysis
# 1) read the morphed individual epochs
# 2) compute the model order
# 3) make the significant threshold
# 4）get the effective connectivities
##################################################################
def causal_analysis(subject,top_c=8):
    import numpy as np
    import mne, sys, os

    subject_path = subjects_dir + 'fsaverage'
    stcs_path = subject_path + '/stcs/%s/' %subject
    inv_path = subject_path + '/bem/fsaverage-ico-4-src.fif'
    src_inv = mne.read_source_spaces(inv_path, add_geom=True)
    
    #Get unfiltered and morphed stcs
    stcs = []
    i = 0
    while i < 120:
        fn_stc = stcs_path + '%s_trial%s_fsaverage' %(subject, str(i))
        stc = mne.read_source_estimate(fn_stc+'-lh.stc', subject='fsaverage')
        stcs.append(stc)
        i = i + 1
    #Get common labels
    list_dirs = os.walk(subject_path + '/func_labels/common/') 
    labels = []
    rois = []
    for root, dirs, files in list_dirs: 
        for f in files: 
            label_fname = os.path.join(root, f) 
            label = mne.read_label(label_fname)
            labels.append(label)
            rois.append(f)
    #Extract stcs in common labels
    label_ts = mne.extract_label_time_course(stcs, labels, src_inv, mode='mean_flip',
                                         return_generator=False)
    
    # Causal analysis
    from scot.connectivity import connectivity
    import scot.connectivity_statistics as scs
    from scot.backend_sklearn import VAR
    import scot.plotting as splt
    from scipy import linalg
    import heapq
    import matplotlib.pylab as plt
    import make_model_order
    # rearrange data to fit scot's format
    label_ts = np.asarray(label_ts).transpose(2, 1, 0)
    label_or = np.mean(label_ts, -1)
    label_or = label_or.T
    mu = np.mean(label_or, axis=1)
    label_or = label_or - mu[:, None]
    p, bic = make_model_order.compute_order(label_or, p_max=20)
    #mvar = VAR(6)
    mvar = VAR(p)
    # generate connectivity surrogates under the null-hypothesis of no connectivity
    c_surrogates = scs.surrogate_connectivity('dDTF', label_ts, mvar, repeats=1000)
    c0 = np.percentile(c_surrogates, 99, axis=0)
    sfreq = 1017.25 
    freqs=[(4, 7), (6, 9), (8, 12), (11, 15), (14, 20),(19, 30)]
    nfreq = len(freqs)
    mvar.fit(label_ts)
    con = connectivity('dDTF', mvar.coef, mvar.rescov)
    con_dif = con - c0

    for ifreq in range(nfreq):             
        fmin,fmax = freqs[ifreq][0],freqs[ifreq][1]
        #fig = splt.plot_connectivity_spectrum([c0], fs=sfreq, freq_range=[fmin, fmax], diagonal=-1)
        #splt.plot_connectivity_spectrum(con, fs=sfreq, freq_range=[fmin, fmax], diagonal=-1, fig=fig)
        #splt.show_plots()
        fig = plt.figure()
        con_band = np.mean(con_dif[:, :, fmin:fmax], axis=-1)
        np.fill_diagonal(con_band, 0)#ignore the dignoal values
        con_band[con_band<0] = 0#ignore the value less than significance
        sig_thr = heapq.nlargest(top_c,con_band.flatten())[-1]#get the top top_c largest significance CA
        con_band[con_band > sig_thr] = con_band.max()
        plt.imshow(con_band, interpolation='nearest', cmap=plt.cm.gray)
        v = np.linspace(0.0, con_band.max(), 10, endpoint=True)
        plt.colorbar(ticks=v)
        #plt.colorbar()
        plt.show()
        plt.savefig(stcs_path+'dDTF_%s_%s.png' %(str(fmin),str(fmax)), dpi=100)
        plt.close()
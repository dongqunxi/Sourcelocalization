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
fn_inv = MNI_dir + '/bem/fsaverage-ico-4-src.fif' 
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
        fn_stc = fn_evoked.split('.fif')[0] + ',morph'
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
        stcs['morph'] = mne.morph_data(subject, subject_id, stcs[subject], 4, smooth=4)
        stcs['morph'].save(fn_stc)
        fig_out = fn_stc + '.png'
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
    


def ROIs_definition(fname_stc, tri='STI 014'):
    import mne, os
    import numpy as np
    fnlist = get_files_from_list(fname_stc)
    # loop across all filenames
    for fn_stc in fnlist:
        #extract the subject infromation from the file name
        name = os.path.basename(fn_stc)
        subject = name.split('_')[0]
        
        subject_path = subjects_dir + subject
        src_inv = mne.read_source_spaces(fn_inv, add_geom=True) 
        if tri == 'STI 014':
            #stc_thr = 85 
            stc_thr = 95
            tri = 'tri'
        elif tri == 'STI 013':
            stc_thr = 95
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
            if  func_label.vertices.shape[0] > 170:  #990 for 90%
                func_label.save(subject_path+'/func_labels/%s' %(tri)+str(i))
            i = i + 1
        # right hemisphere definition      
        j = 0
        while j < len(func_labels_rh):
            func_label = func_labels_rh[j]
            if  func_label.vertices.shape[0] > 170: 
                func_label.save(subject_path+'/func_labels/%s' %(tri)+str(j))
            j = j + 1
        
###########################################################
# This function will show the top 5 strongest labels related
# with auditory and mortor events seperately.
#
###########################################################
def ROIs_selection(fname_stc, tri='STI 014'):
    import mne,os
    import numpy as np
    fnlist = get_files_from_list(fname_stc)
    # loop across all filenames
    for fn_stc in fnlist:
        if tri == 'STI 014':
            tri = 'tri'
        elif tri == 'STI 013':
            tri = 'res'
        stc_morph = mne.read_source_estimate(fn_stc, subject=subject_id)
        src_inv = mne.read_source_spaces(fn_inv, add_geom=True) 
        #extract the subject infromation from the file name
        name = os.path.basename(fn_stc)
        subject = name.split('_')[0]
        
        subject_path = subjects_dir + subject
        list_dirs = os.walk(subject_path + '/func_labels/') 
        labels = []
        rois = []
        for root, dirs, files in list_dirs: 
            for f in files: 
                label_fname = os.path.join(root, f) 
                label = mne.read_label(label_fname)
                if label.name[:3] == tri:
                    labels.append(label)
                    rois.append(f)
    
        pca = stc_morph.extract_label_time_course(labels, src=src_inv, mode='pca_flip')
        src_pow = np.sum(pca**2, axis=1)
        rois_new = np.array(rois)
        plt.figure('pca distribution', figsize=(16, 10))
        if len(rois_new) > 5:
            plt.plot(1e3*stc_morph.times, pca[np.argpartition(src_pow, -5)[-5:]].T,
                    linewidth=3)#Get the top 6 labels
            plt.legend(rois_new[np.argpartition(src_pow, -5)[-5:]])
        else:
            plt.plot(1e3*stc_morph.times, pca[:].T, linewidth=3)#Get the top 5 labels
            plt.legend(rois_new[:])
        plt.show()
        plt.savefig(subject_path+'/MEG/%s_%s_filtered_ROIs_selection' %(subject,tri)) 
        plt.close()
        
###################################################################################
#  Merge overlaped ROIs
###################################################################################
def ROIs_Merging(subject):
    import os,mne
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
####################################################################
# After merge the overlapped labels from two kinds of events, we put 
# the preprocessed top strongest labels into a folder 'selected', and use
# the following function to standardlize the size of them
####################################################################
def ROIs_standardlization(fname_stc):
    import mne,os
    import numpy as np
    fnlist = get_files_from_list(fname_stc)
    # loop across all filenames
    for fn_stc in fnlist:
        stc_morph = mne.read_source_estimate(fn_stc, subject=subject_id)
        
        #extract the subject infromation from the file name
        name = os.path.basename(fn_stc)
        subject = name.split('_')[0]
        
        subject_path = subjects_dir + subject
        sta_path = subject_path+'/func_labels/standard/'
        isExists=os.path.exists(sta_path)
        if not isExists:
            os.makedirs(sta_path) 
        list_dirs = os.walk(subject_path + '/func_labels/merged/') 
        for root, dirs, files in list_dirs: 
            for f in files:
                label_fname = os.path.join(root, f) 
                label = mne.read_label(label_fname)
                stc_label = stc_morph.in_label(label)
                src_pow = np.sum(stc_label.data ** 2, axis=1)
                if label.hemi == 'lh':
                    seed_vertno = stc_label.vertno[0][np.argmax(src_pow)]#Get the max MNE value within each ROI
                    func_label = mne.grow_labels(subject_id, seed_vertno, extents=10.0, 
                                                hemis=0, subjects_dir=subjects_dir, 
                                                n_jobs=1)
                    func_label = func_label[0]
                    func_label.save(sta_path+'%s' %f)
                elif label.hemi == 'rh':
                    seed_vertno = stc_label.vertno[1][np.argmax(src_pow)]
                    func_label = mne.grow_labels(subject_id, seed_vertno, extents=10.0, 
                                                hemis=1, subjects_dir=subjects_dir, 
                                                n_jobs=1)
                    func_label = func_label[0]
                    func_label.save(sta_path+'%s' %f)
                    

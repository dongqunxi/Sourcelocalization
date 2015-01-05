import numpy as np
import mne, sys, os
subject = '108815'
subjects_dir = '/home/qdong/freesurfer/subjects/'
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
import matplotlib.pylab as plt
import make_model_order
# rearrange data to fit scot's format
label_ts = np.asarray(label_ts).transpose(2, 1, 0)
label_cau = label_ts - label_ts.mean(axis=2, keepdims=True)
label_or = np.mean(label_ts, -1,keepdims=True)
label_or = label_or.T
mu = np.mean(label_or, axis=1)
label_or = label_or - mu[:, None]
p, bic = make_model_order.compute_order(label_or, p_max=20)
#compute the causality across trials
#mvar = VAR(p)
#mvar.fit(label_cau)
#con = connectivity('PDC', mvar.coef, mvar.rescov)
#
##make statistical thresholds using LOOM
#mvar_train = VAR(p)
#mvar_test = VAR(p)
#
#freqs=[(4, 7), (6, 9), (8, 12), (11, 15), (14, 20), (19, 30)]
#nfreq = len(freqs)
#
#from sklearn.cross_validation import LeaveOneOut
#loo = LeaveOneOut(120)
#con_train = []
#con_test = []
#for train, test in loo:
#    label_train = label_cau[:, :, train]
#    label_test = label_cau[:, :, test]
#    mvar_train.fit(label_train)
#    con_train.append(connectivity('PDC', mvar_train.coef, mvar_train.rescov))
#    mvar_test.fit(label_test)
#    con_test.append(connectivity('PDC', mvar_test.coef, mvar_test.rescov))
#
#con_mean = np.mean(np.array(con_test), axis=0)
#i = 0
#SE = 0
#while i < 120:
#    SE += (con_train[i] - con_mean)**2
#    i += 1
#SE = np.sqrt(119./120 * SE) 
#from scipy import stats
#thre_con = SE * stats.t.ppf(0.95, 120)
#sfreq = 1017.25
#fig = splt.plot_connectivity_spectrum([thre_con], fs=sfreq, freq_range=[0, 45], diagonal=-1) 
##plot connectivity
#splt.plot_connectivity_spectrum(con, fs=sfreq, freq_range=[0, 45], diagonal=-1, fig=fig)
# 
#splt.show_plots() 
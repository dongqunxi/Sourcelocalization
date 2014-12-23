import numpy as np
import mne, sys, os
subject='108815'
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

# rearrange data to fit scot's format
label_ts = np.asarray(label_ts).transpose(2, 1, 0)
#label_or = np.mean(label_ts, -1)
#label_or = label_or.T
#mu = np.mean(label_or, axis=1)
#label_or = label_or - mu[:, None]
#p, bic = make_model_order.compute_order(label_or, p_max=20)
mvar = VAR(6)

# generate connectivity surrogates under the null-hypothesis of no connectivity
c_surrogates = scs.surrogate_connectivity('GPDC', label_ts, mvar, repeats=1000)
c0 = np.percentile(c_surrogates, 99, axis=0)
sfreq = 1017.25 
freqs=[(4, 7), (6, 9), (8, 12), (11, 15), (14, 20),(19, 30)]
nfreq = len(freqs)
mvar.fit(label_ts)
con = connectivity('GPDC', mvar.coef, mvar.rescov)
fig = splt.plot_connectivity_spectrum([c0], fs=sfreq, freq_range=[0, 45], diagonal=-1) 
##plot connectivity
splt.plot_connectivity_spectrum(con, fs=sfreq, freq_range=[0, 45], diagonal=-1, fig=fig)
fig.show()

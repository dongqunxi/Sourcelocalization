import numpy as np
import mne
import matplotlib.pyplot as plt
subject='108815'
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + 'fsaverage'
stcs_path = subject_path + '/stcs/%s/' %subject
inv_path = subject_path + '/bem/fsaverage-ico-4-src.fif'
src_inv = mne.read_source_spaces(inv_path, add_geom=True)
stcs = []
i = 0
#while i < 120:
#    fn_stc = stcs_path + '%s_trial%s_fsaverage' %(subject, str(i))
#    stc = mne.read_source_estimate(fn_stc+'-lh.stc', subject='fsaverage')
#    stcs.append(stc)
#    i = i + 1
fn_stc = stcs_path + '%s_trial0_fsaverage' %(subject)    
stc = mne.read_source_estimate(fn_stc+'-lh.stc', subject='fsaverage')
src_pow = np.sum(stc.data ** 2, axis=1)
plt.plot(1e3 * stc.times, stc.data[src_pow > np.percentile(src_pow, 90)].T)
plt.show()


from mne.minimum_norm import (apply_inverse_epochs)
import mne, os
from mne.fiff import Raw
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + subject#Set the data path of the subject
raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
basename = raw_fname.split('-')[0]
fn_raw = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw.fif'

fn_inv = fn_raw.split('.fif')[0] + '-inv.fif'
subject_path = subjects_dir + subject
fn_cov = subject_path + '/MEG/%s,bp1-45Hz,empty-cov.fif' %subject
#fn_cov = subject_path + '/MEG/%s,empty-cov.fif' %subject
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
stc=stcs[0]
src_pow = np.sum(stc.data ** 2, axis=1)
plt.plot(1e3 * stc.times, stc.data[src_pow > np.percentile(src_pow, 90)].T)
plt.show()
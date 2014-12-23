from mne.minimum_norm import (apply_inverse_epochs)
import mne, os
from mne.fiff import Raw
subject='108815'
subjects_dir = '/home/qdong/freesurfer/subjects/'
MNI_dir = subjects_dir + 'fsaverage/'
subject_path = subjects_dir + subject#Set the data path of the subject
raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
basename = raw_fname.split('-')[0]
fn_raw = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw.fif'
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
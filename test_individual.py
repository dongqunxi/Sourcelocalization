import source_localization
subjects_dir = '/home/qdong/freesurfer/subjects/'

for subject in ['101611','109925']:
    subject_path = subjects_dir + subject#Set the data path of the subject
    raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
    basename = raw_fname.split('-')[0]
    res_name, tri_name = 'STI 013', 'STI 014'
    fn_tri_evoked = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger.fif'
    fn_res_evoked = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response.fif'
    fn_both_evoked = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger.fif'                                  
    source_localization.make_inverse_operator(fname_evoked=fn_tri_evoked,)
    source_localization.make_inverse_operator(fname_evoked=fn_res_evoked)

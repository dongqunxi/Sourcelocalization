
import source_localization01
for subject in ['101611','110061','109925', '201394', '202825', '108815']:
    #subject='110061'
    subjects_dir = '/home/qdong/freesurfer/subjects/'
    subject_path = subjects_dir + subject#Set the data path of the subject
    raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
    basename = raw_fname.split('-')[0]
    res_name, tri_name = 'STI 013', 'STI 014'
    #basename='/home/qdong/freesurfer/subjects/108815/MEG/108815_audi_cued'
    
   
                                        
    #Merging the overlapped labels and standardlize the size of them
    source_localization01.ROIs_Merging(subject)
    fn_stc_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger,morph' 
    source_localization01.ROIs_standardlization(fn_stc_both)

                                            
    
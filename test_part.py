
import source_localization,os,shutil

subjects_dir = '/home/qdong/freesurfer/subjects/'
MNI_dir = subjects_dir + 'fsaverage/'
subjects_dir = '/home/qdong/freesurfer/subjects/'
sta_path = MNI_dir+'func_labels/standard/'
isExists=os.path.exists(sta_path)
if isExists:
    shutil.rmtree(sta_path)
os.makedirs(sta_path) 
for subject in ['110061','109925', '201394', '202825','101611','108815']:
    #subject='110061'
    subject_path = subjects_dir + subject#Set the data path of the subject
    raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
    basename = raw_fname.split('-')[0]
    res_name, tri_name = 'STI 013', 'STI 014'
    #make filtered and morphed STCs
    #fn_tri_evoked = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger.fif'
    #fn_res_evoked = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response.fif'
    #fn_both_evoked = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger.fif'                                  
    #source_localization.make_inverse_operator(fname_evoked=fn_tri_evoked,)
    #source_localization.make_inverse_operator(fname_evoked=fn_res_evoked)
    #source_localization.make_inverse_operator(fname_evoked=fn_both_evoked) 
   
    ##################################################                                                                                 
    # ROIs_definition                               #  
    #################################################
    fn_stc_tri = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger,morph'
    fn_stc_res = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response,morph'
    fun_path = subject_path+'/func_labels/'
    isExists=os.path.exists(fun_path)
    if isExists:
        shutil.rmtree(fun_path)
    os.makedirs(fun_path) 
    source_localization.ROIs_definition(fn_stc_tri, tri=tri_name)
    source_localization.ROIs_definition(fn_stc_res, tri=res_name)                                    
    #Merging the overlapped labels and standardlize the size of them
    source_localization.ROIs_Merging(subject)
    fn_stc_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger,morph' 
    source_localization.ROIs_standardlization(fn_stc_both, size=8)

source_localization.group_ROI()
source_localization.com_ROI(4)
source_localization.causal_analysis('108815')

import source_localization, jumeg
subjects_dir = '/home/qdong/freesurfer/subjects/'
for subject in ['101611','110061','109925', '201394', '202825']:
    #subject_path = subjects_dir + subject#Set the data path of the subject
    #raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
    #basename = raw_fname.split('-')[0]
    #res_name, tri_name = 'STI 013', 'STI 014'
    #fn_empty_room = subject_path + '/MEG/%s-empty.fif' %subject
    #############################################
    ## unfiltered interest components extraction#
    ############################################# 
    #fn_clean_unfilt = basename + ',ar-raw.fif' 
    #fn_ica2_unfilt = basename + ',ar-ica.fif' 
    #fn_ctps_tri_unfilt = basename + ',ar,ctps-trigger.npy'
    #fn_ctps_res_unfilt = basename + ',ar,ctps-response.npy'
    #fn_ics_tri_unfilt = basename + ',ar,ctps-trigger-ic_selection.txt' 
    #jumeg.jumeg_preprocessing.apply_ica(fn_clean_unfilt,n_components=0.95, 
    #                                    decim=None)
    #tmin, tmax = 0, 0.3
    #jumeg.jumeg_preprocessing.apply_ctps(fn_ica2_unfilt, tmin=tmin, tmax=tmax, 
    #                                                name_stim=tri_name)
    #jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_tri_unfilt)  
    #                                            
    ##response components extraction                                                 
    #tmin, tmax = -0.15, 0.15 
    #jumeg.jumeg_preprocessing.apply_ctps(fn_ica2_unfilt, tmin=tmin, tmax=tmax, 
    #                                                name_stim=res_name)
    #jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_res_unfilt) 
    ##recompose interest components
    #conditions=['trigger', 'response']                
    #jumeg.jumeg_preprocessing.apply_ica_select_brain_response(fn_clean_unfilt, 
    #                                conditions=conditions, n_pca_components=0.95) 
    #
    #################################################################################
    ## morph the unfiltered and insterest Raw data into the common brain space
    ################################################################################
    #fn_unfilt = basename + ',ar,trigger,response,ctpsbr-raw.fif'
    #
    #jumeg.jumeg_preprocessing.apply_create_noise_covariance(fn_empty_room, 
    #                                                    require_filter=False)
    #source_localization.make_inverse_epochs(fn_unfilt)
    source_localization.causal_analysis(subject)
import jumeg
import source_localization01
   
subject='108815'
subjects_dir = '/home/qdong/freesurfer/subjects/'
subject_path = subjects_dir + subject#Set the data path of the subject
raw_fname = subject_path + '/MEG/%s_audi_cued-raw.fif' %subject
basename = raw_fname.split('-')[0]
res_name, tri_name = 'STI 013', 'STI 014'
#basename='/home/qdong/freesurfer/subjects/108815/MEG/108815_audi_cued'

#######################
#ECG and EOG rejection#
######################
fn_filt = basename + ',bp1-45Hz-raw.fif'
fn_ica = basename + ',bp1-45Hz-ica.fif'

jumeg.jumeg_preprocessing.apply_filter(raw_fname)
jumeg.jumeg_preprocessing.apply_ica(fn_filt, n_components=0.99, decim=None)    
# perform cleaning on filtered data   
jumeg.jumeg_preprocessing.apply_ica_cleaning(fn_ica,n_pca_components=0.99,
                                                 unfiltered=False)                                                                                      
# perform cleaning on unfiltered data
jumeg.jumeg_preprocessing.apply_ica_cleaning(fn_ica,n_pca_components=0.99,
                                                 unfiltered=True)
############################################
# filtered interest components extraction  #
############################################
fn_clean = basename + ',bp1-45Hz,ar-raw.fif'
fn_ica2 = basename + ',bp1-45Hz,ar-ica.fif'
fn_ctps_tri = basename + ',bp1-45Hz,ar,ctps-trigger.npy'
fn_ctps_res = basename + ',bp1-45Hz,ar,ctps-response.npy'
fn_ics_tri = basename + ',bp1-45Hz,ar,ctps-trigger-ic_selection.txt'
fn_ics_res = basename + ',bp1-45Hz,ar,ctps-response-ic_selection.txt'

# second ICA decomposition
jumeg.jumeg_preprocessing.apply_ica(fn_clean,n_components=0.95, decim=None) 
#stimulus components extraction
tmin, tmax = 0, 0.3
conditions=['trigger']
jumeg.jumeg_preprocessing.apply_ctps(fn_ica2, tmin=tmin, tmax=tmax, 
                                                 name_stim=tri_name)
jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_tri, 
                                               threshold=0.1)  
jumeg.jumeg_preprocessing.apply_ica_select_brain_response(fn_clean, 
                                conditions=conditions, n_pca_components=0.95)  
#jumeg.jumeg_preprocessing.plot_compare_brain_responses(fn_ics_tri, stim_ch=tri_name, 
 #                                                      tmin=tmin, tmax=tmax)                                             
#response components extraction                                                 
tmin, tmax = -0.15, 0.15 
conditions=['response']
jumeg.jumeg_preprocessing.apply_ctps(fn_ica2, tmin=tmin, tmax=tmax, 
                                                 name_stim=res_name)
jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_res, 
                                                        threshold=0.1) 
jumeg.jumeg_preprocessing.apply_ica_select_brain_response(fn_clean, 
                                conditions=conditions, n_pca_components=0.95) 
#jumeg.jumeg_preprocessing.plot_compare_brain_responses(fn_ics_tri, stim_ch=res_name, 
             #                                          tmin=tmin, tmax=tmax) 
#interest components extraction
conditions=['trigger', 'response']                
jumeg.jumeg_preprocessing.apply_ica_select_brain_response(fn_clean, 
                                conditions=conditions, n_pca_components=0.95)                                
 

                                   
#########################
#Noise covariance making#
#########################
fn_empty_room = subject_path + '/MEG/%s-empty.fif' %subject
jumeg.jumeg_preprocessing.apply_create_noise_covariance(fn_empty_room, 
                                                     require_filter=True)
##########################
#inverse operator makeing#
##########################
#make average evoked data
fn_tri = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw.fif'
fn_res = basename + ',bp1-45Hz,ar,response,ctpsbr-raw.fif'
fn_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw.fif'
jumeg.jumeg_preprocessing.apply_average(fn_tri, name_stim=tri_name, 
                                        tmin=0., tmax=0.3)
jumeg.jumeg_preprocessing.apply_average(fn_res, name_stim=res_name, 
                                        tmin=-0.15, tmax=0.15) 
jumeg.jumeg_preprocessing.apply_average(fn_both)  
                                       
#make inverse operator     
fn_tri_evoked = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger.fif'
fn_res_evoked = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response.fif'
fn_both_evoked = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger.fif'                                  
source_localization01.make_inverse_operator(fname_evoked=fn_tri_evoked,)
source_localization01.make_inverse_operator(fname_evoked=fn_res_evoked)
source_localization01.make_inverse_operator(fname_evoked=fn_both_evoked)  
                                           
##################################################                                                                                 
# ROIs_definition                               #  
#################################################
fn_stc_tri = basename + ',bp1-45Hz,ar,trigger,ctpsbr-raw,avg,trigger,morph'
fn_stc_res = basename + ',bp1-45Hz,ar,response,ctpsbr-raw,avg,response,morph'
source_localization01.ROIs_definition(fn_stc_tri, tri=tri_name)
source_localization01.ROIs_definition(fn_stc_res, tri=res_name)
#Merging the overlapped labels and standardlize the size of them
source_localization01.ROIs_Merging(subject)
fn_stc_both = basename + ',bp1-45Hz,ar,trigger,response,ctpsbr-raw,avg,trigger,morph' 
source_localization01.ROIs_standardlization(fn_stc_both)

##################################################                                                                                 
# ROIs_selection                                 #  
#################################################
#source_localization01.ROIs_selection(fn_stc_tri, tri=tri_name)
#source_localization01.ROIs_selection(fn_stc_res, tri=res_name)



############################################
# unfiltered interest components extraction#
############################################ 
fn_clean_unfilt = basename + ',ar-raw.fif' 
fn_ica2_unfilt = basename + ',ar-ica.fif' 
fn_ctps_tri_unfilt = basename + ',ar,ctps-trigger.npy'
fn_ctps_res_unfilt = basename + ',ar,ctps-response.npy'
fn_ics_tri_unfilt = basename + ',ar,ctps-trigger-ic_selection.txt' 
jumeg.jumeg_preprocessing.apply_ica(fn_clean_unfilt,n_components=0.95, 
                                     decim=None)
tmin, tmax = 0, 0.3
jumeg.jumeg_preprocessing.apply_ctps(fn_ica2_unfilt, tmin=tmin, tmax=tmax, 
                                                 name_stim=tri_name)
jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_tri_unfilt)  
                                              
#response components extraction                                                 
tmin, tmax = -0.15, 0.15 
jumeg.jumeg_preprocessing.apply_ctps(fn_ica2_unfilt, tmin=tmin, tmax=tmax, 
                                                 name_stim=res_name)
jumeg.jumeg_preprocessing.apply_ctps_select_ic(fname_ctps=fn_ctps_res_unfilt) 
#recompose interest components
jumeg.jumeg_preprocessing.apply_ica_select_brain_response(fn_ics_tri_unfilt, 
                                                n_pca_components=0.95) 
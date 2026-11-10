import os
import numpy as np
import pandas as pd
import subprocess
from keras.models import load_model
from ToolsFuns.Material.support import *
from config import Config
import keras.backend as K

K.clear_session()

zeopp_executable = Config().AEOPP_EXECUTABLE
models_directory = Config().SOLVENT_THERMAL_MODEL_PATH

base_path_RASPA = "YOUR PATH TO RASPA"
featurization_directory = "TempFiles/adsorption_stability_temp_data/"

def generate_descriptors(cif_file_path: str):
    featurization_directory, cif_file = os.path.split(cif_file_path)
    
    primitive_path = os.path.join(featurization_directory, 'primitive')
    xyz_path = os.path.join(featurization_directory, 'xyz')
    os.makedirs(primitive_path, exist_ok=True)
    os.makedirs(xyz_path, exist_ok=True)
    # Get the original cell
    primitive_cif_path = os.path.join(primitive_path, cif_file)
    get_primitive(cif_file_path, primitive_cif_path)
    
    # Build the RAC descriptor
    xyz_file_path = os.path.join(xyz_path, cif_file.replace('cif', 'xyz'))
    full_names, full_descriptors = get_MOF_descriptors(primitive_cif_path, 3, path=featurization_directory+'/', xyzpath=xyz_file_path)
    full_names.append('filename')
    full_descriptors.append(cif_file)
    featurization = dict(zip(full_names, full_descriptors))
    return featurization

def get_geometric_features(cif_file_path: str, geo_features_list):
    featurization_directory, cif_file = os.path.split(cif_file_path)
    geometric_path = os.path.join(featurization_directory, 'geometric')
    os.makedirs(geometric_path, exist_ok=True)

    primitive_cif_path = os.path.join(featurization_directory, 'primitive', cif_file)
    basename = os.path.basename(primitive_cif_path).strip('.cif')
    
    # Initialize the geo_dict using geo_features_list
    geo_dict = {key: np.nan for key in geo_features_list}
    geo_dict['name'] = basename
    geo_dict['refcode'] = basename.split('_')[0]
    geo_dict['cif_file'] = cif_file
    
    # Run the Zeo++ command to get geometric features
    cmd1 = f"{zeopp_executable} -ha -res {geometric_path}/{basename}_pd.txt {primitive_cif_path}"
    cmd2 = f"{zeopp_executable} -sa 1.86 1.86 10000 {geometric_path}/{basename}_sa.txt {primitive_cif_path}"
    cmd3 = f"{zeopp_executable} -ha -vol 1.86 1.86 10000 {geometric_path}/{basename}_av.txt {primitive_cif_path}"
    cmd4 = f"{zeopp_executable} -volpo 1.86 1.86 10000 {geometric_path}/{basename}_pov.txt {primitive_cif_path}"
    
    
    subprocess.run(cmd1, shell=True)
    subprocess.run(cmd2, shell=True)
    subprocess.run(cmd3, shell=True)
    subprocess.run(cmd4, shell=True)

    if (os.path.exists(featurization_directory+'geometric/'+str(basename)+'_pd.txt') and 
        os.path.exists(featurization_directory+'geometric/'+str(basename)+'_sa.txt') and
        os.path.exists(featurization_directory+'geometric/'+str(basename)+'_av.txt') and
        os.path.exists(featurization_directory+'geometric/'+str(basename)+'_pov.txt')):
        
        with open(featurization_directory+'geometric/'+str(basename)+'_pd.txt') as f:
            pore_diameter_data = f.readlines()
            for row in pore_diameter_data:
                largest_included_sphere = float(row.split()[1]) # largest included sphere
                largest_free_sphere = float(row.split()[2]) # largest free sphere
                largest_included_sphere_along_free_sphere_path = float(row.split()[3]) # largest included sphere along free sphere path
        with open(featurization_directory+'/geometric/'+str(basename)+'_sa.txt') as f:
            surface_area_data = f.readlines()
            for i, row in enumerate(surface_area_data):
                if i == 0:
                    unit_cell_volume = float(row.split('Unitcell_volume:')[1].split()[0]) # unit cell volume
                    crystal_density = float(row.split('Unitcell_volume:')[1].split()[0]) # crystal density
                    VSA = float(row.split('ASA_m^2/cm^3:')[1].split()[0]) # volumetric surface area
                    GSA = float(row.split('ASA_m^2/g:')[1].split()[0]) # gravimetric surface area
        with open(featurization_directory+'geometric/'+str(basename)+'_pov.txt') as f:
            pore_volume_data = f.readlines()
            for i, row in enumerate(pore_volume_data):
                if i == 0:
                    density = float(row.split('Density:')[1].split()[0])
                    POAV = float(row.split('POAV_A^3:')[1].split()[0]) # Probe accessible pore volume
                    PONAV = float(row.split('PONAV_A^3:')[1].split()[0]) # Probe non-accessible probe volume
                    GPOAV = float(row.split('POAV_cm^3/g:')[1].split()[0])
                    GPONAV = float(row.split('PONAV_cm^3/g:')[1].split()[0])
                    POAV_volume_fraction = float(row.split('POAV_Volume_fraction:')[1].split()[0]) # probe accessible volume fraction
                    PONAV_volume_fraction = float(row.split('PONAV_Volume_fraction:')[1].split()[0]) # probe non accessible volume fraction
                    VPOV = POAV_volume_fraction+PONAV_volume_fraction
                    GPOV = VPOV/density
        # Fill in the geo_dict
        geo_dict = {'name':basename,'refcode':basename.split('_')[0], 'cif_file':cif_file, 'Di':largest_included_sphere, 'Df': largest_free_sphere, 'Dif': largest_included_sphere_along_free_sphere_path,
            'rho': crystal_density, 'VSA':VSA, 'GSA': GSA, 'VPOV': VPOV, 'GPOV':GPOV, 'POAV_vol_frac':POAV_volume_fraction,
            'PONAV_vol_frac':PONAV_volume_fraction, 'GPOAV':GPOAV,'GPONAV':GPONAV,'POAV':POAV,'PONAV':PONAV}
    else:
        print(f"{basename}: Not all required geometric files are available.")

    return geo_dict


def predict_stability(cif_file_name: str):
    """
    Predicts the thermal and solvent removal stability of a MOF based on its structural features.
    Args:
        cif_file_path (str): The path to a single CIF file.

    Return: The thermal and solvent removal stability.
    """

    base_path = Config().UPLOAD_FILES_BASE_PATH

    if not cif_file_name.endswith('.cif'):
            cif_file_name += '.cif'
        
    cif_file_path = os.path.join(base_path, cif_file_name)
    
    if not os.path.exists(cif_file_path):
        return f"Tool function execution error, No such file or directory: {cif_file_name}"
    featurization_list = []

    if os.path.isfile(cif_file_path):
        print(f"Processing: {cif_file_name}")
        featurization = generate_descriptors(cif_file_path)
        geo_features = get_geometric_features(cif_file_path, geo)
        featurization.update(geo_features)
        featurization_list.append(featurization)
        print(f"Finished processing: {cif_file_name}")
    else:
        print(f"The provided path is not a file: {cif_file_path}")
        return "Error: Provided path is not a file."
        
    df = pd.DataFrame(featurization_list) 
    df.to_csv(featurization_directory+'/full_featurization_frame.csv',index=False)
    dependencies = {'precision':precision,'recall':recall,'f1':f1}

    solvent_ANN = load_model(models_directory+'/solvent_removal_stability_ANN.h5',custom_objects=dependencies)
    thermal_ANN = load_model(models_directory+'/thermal_stability_ANN.h5')

    ### prep thermal frames
    df_train_thermal = pd.read_csv(models_directory+'/thermal/train.csv')
    df_train_thermal = df_train_thermal.loc[:, (df_train_thermal != df_train_thermal.iloc[0]).any()]
    df_val_thermal = pd.read_csv(models_directory+'/thermal/val.csv')
    df_test_thermal = pd.read_csv(models_directory+'/thermal/test.csv')
    features_thermal = [val for val in df_train_thermal.columns.values if val in RACs+geo]


    ### prep solvent frames
    df_train_solvent = pd.read_csv(models_directory+'/solvent/train.csv')
    df_train_solvent = df_train_solvent.loc[:, (df_train_solvent != df_train_solvent.iloc[0]).any()]
    df_val_solvent = pd.read_csv(models_directory+'/solvent/val.csv')
    df_test_solvent = pd.read_csv(models_directory+'/solvent/test.csv')
    joint_train_val_solvent = pd.concat([df_train_solvent,df_val_solvent],axis=0)
    features_solvent = [val for val in df_train_solvent.columns.values if val in RACs+geo]
    
    X_train_thermal, X_test_thermal, y_train_thermal, y_test_thermal, x_scaler_thermal, y_scaler_thermal = thermal_normalize_data(df_train_thermal, df_test_thermal, features_thermal, ["T"], unit_trans=1, debug=False)
    X_train_thermal, X_val_thermal, y_train_thermal, y_val_thermal, x_scaler_thermal, y_scaler_thermal = thermal_normalize_data(df_train_thermal, df_val_thermal, features_thermal, ["T"], unit_trans=1, debug=False)
    
    X_train_solvent, X_test_solvent, y_train_solvent, y_test_solvent, x_scaler_solvent = solvent_normalize_data(df_train_solvent, df_test_solvent, features_solvent, ["flag"], unit_trans=1, debug=False)
    X_train_solvent, X_val, y_train, y_val_solvent, x_scaler_solvent = solvent_normalize_data(df_train_solvent, df_val_solvent, features_solvent, ["flag"], unit_trans=1, debug=False)
    

    X_new_MOF_thermal = x_scaler_thermal.transform(df[features_thermal].values)
    pred_thermal_new_MOF = y_scaler_thermal.inverse_transform(thermal_ANN.predict(X_new_MOF_thermal))
    
    X_new_MOF_solvent = x_scaler_solvent.transform(df[features_solvent].values)
    pred_solvent_new_MOF = solvent_ANN.predict(X_new_MOF_solvent)

    df['ANN_thermal_prediction'] = pred_thermal_new_MOF
    df['ANN_solvent_removal_prediction'] = pred_solvent_new_MOF
    return df[['filename', 'ANN_thermal_prediction', 'ANN_solvent_removal_prediction']].to_string(index=False)

def predict_adsorption(cif_file_name: str):
    """
    Predicts the adsorption performance of MOF based on its structural features.
    Args:
        cif_file_path (str): The path to a single CIF file.
    Return: The adsorption performance.
    """
    components=['CO2', 'H2']

    base_path = Config().UPLOAD_FILES_BASE_PATH

    if not cif_file_name.endswith('.cif'):
            cif_file_name += '.cif'
        
    cif_file_path = os.path.join(base_path, cif_file_name)
    print(f"cif_file_path: {cif_file_path}")
    if not os.path.exists(cif_file_path):
        return f"Tool function execution error, No such file or directory: {cif_file_name}"
    
    template_path = os.path.join(base_path_RASPA, "ToolsAgent/ToolsFuns/Material/utils/simulation_template.input")
    result_file = os.path.join(base_path_RASPA, "ToolsAgent/DataFiles/csv/adsorption_results.csv")
    output_dir = os.path.join(base_path_RASPA, "ToolsAgent/TempFiles/RASPA_Output/")

    # Assuming `check_parameters_single` is a modified version of `check_parameters` to work with a single file
    raspa_dir, cif_file, cutoffvdm, max_threads = check_parameters(cif_file_path)

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ensure the result file does not exist (or delete if it does)
    if os.path.exists(result_file):
        os.remove(result_file)

    # Initialize the result file with headers
    with open(result_file, 'w') as f:
        headers = get_field_headers(components)
        f.write(",".join(headers) + "\n")

    with open(template_path, "r") as f:
        template = f.read()

    print(f"Processing {cif_file}")
    input_text = generate_simulation_input(template, cutoffvdm, cif_file_path)
    work(cif_file_path, raspa_dir, result_file, components, headers, input_text)
    print("Finished processing single CIF file.")

    df_full = pd.read_csv(result_file)
    df_selected = df_full[['filename', 'finished', 'CO2_absolute_mg/g', 'H2_absolute_mg/g', 'CO2_excess_mg/g', 'H2_excess_mg/g']].to_string(index=False)
    return df_selected




import os
from typing import List
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

import pandas as pd
import numpy as np

import requests
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier  
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier

base_path = 'ToolsKG/TempFiles/ChemLab'
def Generate_ElectricalDescriptors_from_csv(csv_name: str):
    """
    Generate electrical RDKit descriptors for the SMILES strings in a CSV file and save to a new CSV file.
    
    Args:
        input_csv: Path to the input CSV file containing SMILES strings.
        output_csv: Path where the output CSV file will be saved.

    Returns:
        str: Message indicating the completion of processing and the path to the output CSV file.
    """
    # base_path = config.UPLOAD_FILES_BASE_PATH 
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'
    input_csv_path = os.path.join(base_path, csv_name)
    output_csv_name = os.path.splitext(csv_name)[0] + '_electrical_descriptors.csv'
    output_csv_path = os.path.join(base_path, output_csv_name)
    
    if not os.path.exists(input_csv_path):
        return f"Error: input file {csv_name} not found."


    data = pd.read_csv(input_csv_path)
    if len(data.columns) < 3:
        return "Error: The CSV file must have at least three columns for SMILES strings."

    descriptor_keys = ['MaxEStateIndex', 'MinAbsEStateIndex', 'MinEStateIndex', 'qed', 
                       'NumValenceElectrons', 'NumRadicalElectrons', 'MaxPartialCharge', 
                       'MinPartialCharge', 'MaxAbsPartialCharge', 'MinAbsPartialCharge', 
                       'MolLogP', 'MolMR']

    descriptors_list = []
    # Process each of the first three SMILES string columns
    for col in data.columns[:3]:  # Assumes the first three columns are SMILES strings
        descriptors = []
        for smi in data[col]:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                # Calculate the descriptors for each molecule
                desc = [Descriptors.__dict__[dk](mol) if dk in Descriptors.__dict__ else None for dk in descriptor_keys]
                descriptors.append(desc)
            else:
                # Append None for each descriptor if the SMILES string is invalid
                descriptors.append([None] * len(descriptor_keys))
        # Append the results to the descriptors_list
        descriptors_list.append(pd.DataFrame(descriptors, columns=[f"{col}_{dk}" for dk in descriptor_keys]))

    # Concatenate all descriptors along the column axis
    all_descriptors = pd.concat(descriptors_list, axis=1)
    result_data = pd.concat([all_descriptors, data.iloc[:, 3:]], axis=1)  # Concatenate descriptors with conversion data columns

    # Save the resulting DataFrame to a new CSV file
    result_data.to_csv(output_csv_path, index=False)

    return f"Processed SMILES strings and saved electrical descriptors to {output_csv_path}"

def Generate_Morganfingerprints_from_csv(csv_name: str):
    """
    Generate morgan fingerprints for the SMILES strings in a CSV file and save to a new CSV file.

    Args:
        csv_name: file name of the input CSV containing SMILES strings.

    Returns:
        str: Message indicating the completion of processing and the path to the output CSV file.
    
    Note: Your input only needs to contain the file name, without any additional information. For example, your input should be "filename.csv" instead of "csv_name='filename.csv'"    

    """
    # base_path = config.UPLOAD_FILES_BASE_PATH 
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'
    input_csv_path = os.path.join(base_path, csv_name)
    output_csv_name = os.path.splitext(csv_name)[0] + '_Morgan_fingerprints.csv'
    output_csv_path = os.path.join(base_path, output_csv_name)
    
    if not os.path.exists(input_csv_path):
        return f"Error: input file {csv_name} not found."

    # Read the input CSV file
    data = pd.read_csv(input_csv_path)
    
    # Ensure there are at least three columns for SMILES strings
    if len(data.columns) < 3:
        return "The input CSV file must have at least three columns for SMILES strings."

    # Process each SMILES string and generate fingerprints
    fingerprints = []
    for idx, row in data.iterrows():
        row_fps = []
        for smi in row[:3]:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                # Generate Morgan fingerprints with radius 3 and 512 bits
                morgan_fp = AllChem.GetMorganFingerprintAsBitVect(mol, 3, nBits=512)
                # Convert the fingerprint to a binary string representation
                binary_string = morgan_fp.ToBitString()
                row_fps.append(binary_string)
            else:
                # In case the SMILES string cannot be converted to a molecule
                row_fps.append("Invalid SMILES")
        fingerprints.append(row_fps)
    
    # Create a new DataFrame with the fingerprints and the remaining data
    fp_data = pd.DataFrame(fingerprints, columns=['B_Fingerprint', 'C_Fingerprint', 'Product_Fingerprint'])
    result_data = pd.concat([fp_data, data.iloc[:, 3:]], axis=1)
    
    # Save the resulting DataFrame to a new CSV file
    result_data.to_csv(output_csv_path, index=False)

    return f"\nSMILES strings in the {csv_name} file have been processed, and the morgan fingerprints features are saved to the path {output_csv_path}\n"

def Generate_RDKfingerprints_from_csv(csv_name: str):
    """
    Generate RDKfingerprints for the SMILES strings in a CSV file and save to a new CSV file.
    Args:
        csv_name: file name
    
    Note: Your input only needs to contain the file name, without any additional information. For example, your input should be "filename.csv" instead of "csv_name='filename.csv'"    
    """
    # base_path = config.UPLOAD_FILES_BASE_PATH 
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'
    input_csv_path = os.path.join(base_path, csv_name)
    output_csv_name = os.path.splitext(csv_name)[0] + '_RDK_fingerprints.csv'
    output_csv_path = os.path.join(base_path, output_csv_name)
    
    if not os.path.exists(input_csv_path):
        return f"Error: input file {csv_name} not found."
    
    data = pd.read_csv(input_csv_path)
    
    # Ensure there are at least three columns for B, C, and Product SMILES
    if len(data.columns) < 3:
        return "The input CSV file must have at least three columns for B, C, and Product SMILES."
    
    # Process each SMILES string and generate fingerprints
    fingerprints = []
    for idx, row in data.iterrows():
        row_fps = []
        for smi in row[:3]:  # Assuming the first three columns are the SMILES strings
            mol = Chem.MolFromSmiles(smi)
            if mol:
                fp = Chem.RDKFingerprint(mol, fpSize=512)
                # Convert the fingerprint to a binary string representation
                binary_string = fp.ToBitString()
                row_fps.append(binary_string)
            else:
                # In case the SMILES string cannot be converted to a molecule
                row_fps.append("Invalid SMILES")
        fingerprints.append(row_fps)
    
    # Create a new DataFrame with the fingerprints and the remaining data
    fp_data = pd.DataFrame(fingerprints, columns=['B_Fingerprint', 'C_Fingerprint', 'Product_Fingerprint'])
    result_data = pd.concat([fp_data, data.iloc[:, 3:]], axis=1)
    
    # Save the resulting DataFrame to a new CSV file
    result_data.to_csv(output_csv_path, index=False)

    return f"\nsmiles in the {csv_name} file have been processed, and the fingerprints features are saved to the path {output_csv_path}\n"

# load data
def load_and_prepare_data(csv_file, y_label_index):
    data = pd.read_csv(csv_file)
    # The first three columns of # are Fingerprints, converting them from string to numeric
    features = data.iloc[:, :3].apply(lambda row: np.array([int(x) for x in ''.join(row.values)]), axis=1)
    labels = data.iloc[:, y_label_index]
    # Convert features to a format that fits the model
    features = np.array(features.tolist())
    # Convert labels to classes
    labels = labels.apply(lambda x: 0 if x <= 33 else (1 if x <= 66 else 2))
    return features, labels

def load_and_prepare_electrical_data(csv_file, y_label_index):
    """
    Load data from a CSV file and prepare it for machine learning models.
    
    Args:
        csv_file: Path to the CSV file containing the data.
        y_label_index: The column index of the label in the CSV file.

    Returns:
        tuple: A tuple containing the features as a numpy array and the labels as a numpy array.
    """
    data = pd.read_csv(csv_file)

    # Assuming that all except the last two columns are features if y_label_index is -2 (the second last column as label)
    if y_label_index == -2:
        X = data.iloc[:, :-2]  # All columns except the last two are features
        y = data.iloc[:, y_label_index]  # The second last column is the label
    else:
        # Adjust according to specific layout if needed
        X = data.iloc[:, :y_label_index]  # Features up to the label index
        y = data.iloc[:, y_label_index]  # Label column

    # Convert features to float if not already
    X = X.apply(pd.to_numeric, errors='coerce', axis=1)

    # Handling possible NaNs in features
    X = X.fillna(0.0).values

    # Convert labels to categories based on a specific threshold or logic
    y = y.apply(lambda x: 0 if x <= 33 else (1 if x <= 66 else 2)).values

    return X, y

def normalize_csv_name(csv_name: str, base_path: str) -> str:
    """
    Normalize the input CSV name to remove unnecessary path prefixes.

    Args:
        csv_name: Input CSV file name or path.
        base_path: The base path to compare against.

    Returns:
        str: Normalized CSV file name.
    """
    # If the input contains the base path, strip it
    if csv_name.startswith(base_path):
        csv_name = os.path.basename(csv_name)
    return csv_name

def MLP_Classifier(csv_name: str):
    """
    General MLP classifier function that predicts based on processed feature files.

    Args:
        csv_name: The name of the test data feature file for prediction.
                  For example: 'chemsmiles_test_electrical_descriptors.csv' or 'demo_test_Morgan_fingerprints.csv'.

    Returns:
        str: A string describing the accuracy of the model on the training set and test set.
    """
    # base_path = config.UPLOAD_FILES_BASE_PATH
    csv_name = normalize_csv_name(csv_name, base_path)
    # Ensure csv_name ends with '.csv'
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'

    test_data_feature_path = os.path.join(base_path, csv_name)
    if not os.path.exists(test_data_feature_path):
        return f"Error: Test data feature file {csv_name} not found."

    # Extract feature type and prefix from the file name
    base_name = os.path.splitext(csv_name)[0]
    tokens = base_name.split('_')

    if 'test' not in tokens:
        return "Error: The test file name format is incorrect. It should contain 'test'."

    # Find the index of 'test' and replace it with 'train' to get training file name
    test_index = tokens.index('test')
    tokens[test_index] = 'train'
    training_base_name = '_'.join(tokens)
    training_csv_name = training_base_name + '.csv'
    train_data_feature_path = os.path.join(base_path, training_csv_name)

    # Extract feature type (tokens after 'train')
    feature_type = '_'.join(tokens[test_index + 1:])

    # Construct original training data file name (without feature type)
    original_train_tokens = tokens[:test_index + 1]  # Include 'train'
    original_train_base_name = '_'.join(original_train_tokens)
    train_data_input_name = original_train_base_name + '.csv'
    train_data_input_path = os.path.join(base_path, train_data_input_name)

    if not os.path.exists(train_data_feature_path):
        # If the training data feature file doesn't exist, generate it
        if not os.path.exists(train_data_input_path):
            return f"Error: Training data file {train_data_input_name} not found."

        try:
            # Generate the training feature file based on the feature type
            if feature_type == 'electrical_descriptors':
                Generate_ElectricalDescriptors_from_csv(train_data_input_name)
            elif feature_type == 'Morgan_fingerprints':
                Generate_Morganfingerprints_from_csv(train_data_input_name)
            elif feature_type == 'RDK_fingerprints':
                Generate_RDKfingerprints_from_csv(train_data_input_name)    
            # Add other feature type processing functions as needed
            else:
                return f"Error: Unrecognized feature type '{feature_type}'."
        except Exception as e:
            return f"Error generating training features for feature type '{feature_type}': {str(e)}"

    # Now load training and test data
    try:
        y_label_index = -1  # Assuming the label is in the last column
        # Load training and test data based on feature type
        if feature_type == 'electrical_descriptors':
            x_train, y_train = load_and_prepare_electrical_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_electrical_data(test_data_feature_path, y_label_index)
        elif feature_type in ['Morgan_fingerprints', 'RDK_fingerprints']:
            x_train, y_train = load_and_prepare_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_data(test_data_feature_path, y_label_index)
        else:
            return f"Error: Unknown feature type '{feature_type}'."
        # Train the MLP model
        clf_mlp = MLPClassifier(max_iter=500)
        clf_mlp.fit(x_train, y_train)

        # Evaluate the model
        train_accuracy = accuracy_score(y_train, clf_mlp.predict(x_train))
        test_accuracy = accuracy_score(y_test, clf_mlp.predict(x_test))

        markdown_result = f"""
### MLP Classifier Results for {feature_type.replace('_', ' ').title()}

- **Training Accuracy**: {train_accuracy:.4f}
- **Test Accuracy**: {test_accuracy:.4f}

"""
        return markdown_result
    except Exception as e:
        return f"Error during model training or evaluation: {str(e)}"

def AdaBoost_Classifier(csv_name: str):
    """
    General AdaBoost classifier function that predicts based on processed feature files.

    Args:
        csv_name: The name of the test data feature file for prediction.
                  For example: 'chemsmiles_test_electrical_descriptors.csv' or 'demo_test_Morgan_fingerprints.csv'.

    Returns:
        str: A string containing the model's accuracy on the training set and test set, in markdown format.
    """
    # base_path = config.UPLOAD_FILES_BASE_PATH
    csv_name = normalize_csv_name(csv_name, base_path)
    # Ensure csv_name ends with '.csv'
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'

    test_data_feature_path = os.path.join(base_path, csv_name)
    if not os.path.exists(test_data_feature_path):
        return f"Error: Test data feature file {csv_name} not found."

    # Extract feature type and prefix from the file name
    base_name = os.path.splitext(csv_name)[0]
    tokens = base_name.split('_')

    if 'test' not in tokens:
        return "Error: The test file name format is incorrect. It should contain 'test'."

    # Find the index of 'test' and replace it with 'train' to get training file name
    test_index = tokens.index('test')
    tokens[test_index] = 'train'
    training_base_name = '_'.join(tokens)
    training_csv_name = training_base_name + '.csv'
    train_data_feature_path = os.path.join(base_path, training_csv_name)

    # Extract feature type (tokens after 'train')
    feature_type = '_'.join(tokens[test_index + 1:])

    # Construct original training data file name (without feature type)
    original_train_tokens = tokens[:test_index + 1]  # Include 'train'
    original_train_base_name = '_'.join(original_train_tokens)
    train_data_input_name = original_train_base_name + '.csv'
    train_data_input_path = os.path.join(base_path, train_data_input_name)

    if not os.path.exists(train_data_feature_path):
        # If the training data feature file doesn't exist, generate it
        if not os.path.exists(train_data_input_path):
            return f"Error: Training data file {train_data_input_name} not found."

        try:
            # Generate the training feature file based on the feature type
            if feature_type == 'electrical_descriptors':
                Generate_ElectricalDescriptors_from_csv(train_data_input_name)
            elif feature_type == 'Morgan_fingerprints':
                Generate_Morganfingerprints_from_csv(train_data_input_name)
            elif feature_type == 'RDK_fingerprints':
                Generate_RDKfingerprints_from_csv(train_data_input_name)
            # Add other feature type processing functions as needed
            else:
                return f"Error: Unrecognized feature type '{feature_type}'."
        except Exception as e:
            return f"Error generating training features for feature type '{feature_type}': {str(e)}"

    # Now load training and test data
    try:
        y_label_index = -1  # Assuming the label is in the last column
        # Load training and test data based on feature type
        if feature_type == 'electrical_descriptors':
            x_train, y_train = load_and_prepare_electrical_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_electrical_data(test_data_feature_path, y_label_index)
        elif feature_type in ['Morgan_fingerprints', 'RDK_fingerprints']:
            x_train, y_train = load_and_prepare_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_data(test_data_feature_path, y_label_index)
        else:
            return f"Error: Unknown feature type '{feature_type}'."

        # Train the AdaBoost model
        clf_adaboost = AdaBoostClassifier(n_estimators=100)
        clf_adaboost.fit(x_train, y_train)

        # Evaluate the model
        train_accuracy = accuracy_score(y_train, clf_adaboost.predict(x_train))
        test_accuracy = accuracy_score(y_test, clf_adaboost.predict(x_test))

        markdown_result = f"""
### AdaBoost Classifier Results for {feature_type.replace('_', ' ').title()}

- **Training Accuracy**: {train_accuracy:.4f}
- **Test Accuracy**: {test_accuracy:.4f}

"""
        return markdown_result
    except Exception as e:
        return f"Error during model training or evaluation: {str(e)}"

    
def RandomForest_Classifier(csv_name: str):
    """
    General Random Forest classifier function that predicts based on processed feature files.

    Args:
        csv_name: The name of the test data feature file for prediction.
                  For example: 'chemsmiles_test_electrical_descriptors.csv' or 'demo_test_Morgan_fingerprints.csv'.

    Returns:
        str: A string containing the model's accuracy on the training set and test set, in markdown format.
    """
    # base_path = config.UPLOAD_FILES_BASE_PATH
    csv_name = normalize_csv_name(csv_name, base_path)
    if not csv_name.endswith('.csv'):
        csv_name += '.csv'

    test_data_feature_path = os.path.join(base_path, csv_name)
    if not os.path.exists(test_data_feature_path):
        return f"Error: Test data feature file {csv_name} not found."

    # Extract feature type and prefix from the file name
    base_name = os.path.splitext(csv_name)[0]
    tokens = base_name.split('_')

    if 'test' not in tokens:
        return "Error: The test file name format is incorrect. It should contain 'test'."

    # Find the index of 'test' and replace it with 'train' to get training file name
    test_index = tokens.index('test')
    tokens[test_index] = 'train'
    training_base_name = '_'.join(tokens)
    training_csv_name = training_base_name + '.csv'
    train_data_feature_path = os.path.join(base_path, training_csv_name)

    # Extract feature type (tokens after 'train')
    feature_type = '_'.join(tokens[test_index + 1:])

    # Construct original training data file name (without feature type)
    original_train_tokens = tokens[:test_index + 1]  # Include 'train'
    original_train_base_name = '_'.join(original_train_tokens)
    train_data_input_name = original_train_base_name + '.csv'
    train_data_input_path = os.path.join(base_path, train_data_input_name)

    if not os.path.exists(train_data_feature_path):
        # If the training data feature file doesn't exist, generate it
        if not os.path.exists(train_data_input_path):
            return f"Error: Training data file {train_data_input_name} not found."

        try:
            # Generate the training feature file based on the feature type
            if feature_type == 'electrical_descriptors':
                Generate_ElectricalDescriptors_from_csv(train_data_input_name)
            elif feature_type == 'Morgan_fingerprints':
                Generate_Morganfingerprints_from_csv(train_data_input_name)
            elif feature_type == 'RDK_fingerprints':
                Generate_RDKfingerprints_from_csv(train_data_input_name)
            # Add other feature type processing functions as needed
            else:
                return f"Error: Unrecognized feature type '{feature_type}'."
        except Exception as e:
            return f"Error generating training features for feature type '{feature_type}': {str(e)}"

    # Now load training and test data
    try:
        y_label_index = -1  # Assuming the label is in the last column
        # Load training and test data based on feature type
        if feature_type == 'electrical_descriptors':
            x_train, y_train = load_and_prepare_electrical_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_electrical_data(test_data_feature_path, y_label_index)
        elif feature_type in ['Morgan_fingerprints', 'RDK_fingerprints']:
            x_train, y_train = load_and_prepare_data(train_data_feature_path, y_label_index)
            x_test, y_test = load_and_prepare_data(test_data_feature_path, y_label_index)
        else:
            return f"Error: Unknown feature type '{feature_type}'."

        # Train the Random Forest model
        clf_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_rf.fit(x_train, y_train)

        # Evaluate the model
        train_accuracy = accuracy_score(y_train, clf_rf.predict(x_train))
        test_accuracy = accuracy_score(y_test, clf_rf.predict(x_test))

        markdown_result = f"""
### Random Forest Classifier Results for {feature_type.replace('_', ' ').title()}

- **Training Accuracy**: {train_accuracy:.4f}
- **Test Accuracy**: {test_accuracy:.4f}

"""
        return markdown_result
    except Exception as e:
        return f"Error during model training or evaluation: {str(e)}"
    
def RunSuZuKiReactionExperiment(num_iterations: int):
    """
    This function performs an automated Suzuki Reaction experiment by iteratively optimizing experimental parameters using Bayesian optimization.
    
    Args:
        num_iterations (int): Number of iterations for Bayesian optimization. Default is 5.
        
    Returns:
        str: A markdown string with the results of the experiment.
    """
    try:
        params = {
            "num_iterations": num_iterations
        }

        response = requests.get("http://10.99.211.252:8080/run_bayesian_optimization/", params=params)

        if response.status_code == 200:
            json_response = response.json()
            if json_response["status"] == "success":
                return json_response["result"]
            else:
                return f"调用服务失败：{json_response['message']}"
        else:
            return f"调用服务失败：{response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"
import subprocess
import pandas as pd
import json
import re
import os
import requests
import torch
from prody import *
from chroma import Chroma, conditioners, Protein, api
from chroma.models import graph_classifier, procap
from config import Config

from ToolsFuns.Biology.ForceGPT import ForceGPTmodel
from ToolsFuns.Biology.support.utils import extract_start_and_end, generate_output_from_prompt, extract_task


api.register_key(Config().CHROMA_KEY,)
code_dir="TempFiles/pdb/code_protein"
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

def analyze_protein_CATH_from_PDBID(PDB_id: str) -> str:
    """
    Queries the CATH database for a given PDB ID and returns the CATH classification
    along with a detailed explanation in an easy-to-understand Markdown format.

    Args:
        PDB_id (str): The PDB ID of the protein to query.

    Returns:
        str: A Markdown formatted string that describes the CATH classification of the protein
             with detailed explanations. If an error occurs or the PDB ID is not found,
             an error message is returned.
    """
    try:
        cath = CATHDB()
        result = cath.search(PDB_id)
        
        if not result or len(result.cath) == 0:
            raise ValueError(f"No CATH classification found for PDB ID '{PDB_id}'.")

        classification = result.cath[0]
        class_, architecture, topology, homologous_superfamily = classification.split('.')

        markdown_output = (
            f"## CATH Classification for PDB ID: `{PDB_id}`\n\n"
            f"- **CATH Classification**: `{classification}`\n"
            f"    - **Class {class_}**: Mainly alpha helices.\n"
            f"    - **Architecture {architecture}**: Specific arrangement of alpha helices.\n"
            f"    - **Topology {topology}**: Specific topology of alpha helices within the architecture.\n"
            f"    - **Homologous Superfamily {homologous_superfamily}**: Proteins sharing a common evolutionary origin with similar functions and structural features.\n"
        )
    except Exception as e:
        markdown_output = f"Error occurred while querying CATH classification: {str(e)}\n"

    return markdown_output

def analyze_protein_length_from_PDB(PDB_name: str) -> str:
    """
    Determines the sequence length of a protein given its PDB ID or file name.

    Args:
        PDB_name (str): The PDB ID or filename of the protein.

    Returns:
        str: A Markdown formatted string describing the sequence length of the protein.
             If an error occurs, an error message is returned.
    """
    markdown_output = f"### Protein Sequence Length for `{PDB_name}`\n\n"
    try:
        if re.search('.pdb$', PDB_name):
            if re.search(f'^{code_dir}', PDB_name):
                protein_path = PDB_name
            else:
                protein_path = os.path.join(code_dir, PDB_name)
            # Assuming from_PDB method exists and can read from a file path
            prot = Protein.from_PDB(protein_path)
        else:
            # Assuming from_PDBID method exists and can fetch protein data using PDB ID
            prot = Protein.from_PDBID(PDB_name)

        sequence_length = len(prot.sequence())
        markdown_output += f"- **Sequence Length**: `{sequence_length}` amino acids\n"
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}\n"

    return markdown_output

def analyze_protein_seq_from_PDB(PDB_name: str) -> str:
    """
    Returns the amino acid sequence of proteins given their PDB ID or filename.

    Args:
        PDB_name (str): The PDB ID or filename of the protein.

    Returns:
        str: A Markdown formatted string describing the amino acid sequence of the protein.
             If an error occurs, an error message is returned.
    """
    if not PDB_name.endswith('.pdb'):
        PDB_name += '.pdb'
    
    try:
        markdown_output = f"### Protein Sequence for `{PDB_name}`\n\n"
        if re.search('.pdb', PDB_name):
            protein_path = os.path.join(code_dir, PDB_name)
            # Assuming from_PDB method exists and can read from a file path
            prot = Protein.from_PDB(protein_path)
        else:
            # Assuming from_PDBID method exists and can fetch protein data using PDB ID
            prot = Protein.from_PDBID(PDB_name)

        sequence = prot.sequence()
        markdown_output += f"- **Amino Acid Sequence**:\n\n```plaintext\n{sequence}\n```\n"
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}\n"

    return markdown_output


def calculate_energy_from_sequence(sequence):
    """
    Calculates the unfolding energy of a protein based on its amino acid sequence.
    Args:
        sequence (str): Amino acid sequence of the protein.
    Returns:
        str: A Markdown formatted string representing the calculated energy value.
    """
    try:
        prompt = f"CalculateEnergy<{sequence}>"
        task = extract_task(prompt, end_task_token='>') + ' '
        model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

        sample_output = generate_output_from_prompt(model, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
        for output in sample_output:
            result = tokenizer.decode(output, skip_special_tokens=True)
            energy_value = extract_start_and_end(result, start_token='[', end_token=']')
        return f"### Energy Calculation Result\n\n- **Sequence**: `{sequence}`\n- **Calculated Energy**: `{energy_value}`"
    except Exception as e:
        return f"### Error\n\nAn error occurred during the energy calculation: {str(e)}"

def calculate_force_from_sequence(sequence):
    """
    Calculates the unfolding force of a protein based on its amino acid sequence.
    Args:
        sequence (str): Amino acid sequence of the protein.
    Returns:
        str: A Markdown formatted string representing the calculated force value.
    """
    try:
        prompt = f"CalculateForce<{sequence}>"
        task = extract_task(prompt, end_task_token='>') + ' '
        model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

        sample_output = generate_output_from_prompt(model, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
        for output in sample_output:
            result = tokenizer.decode(output, skip_special_tokens=True)
            force_value = extract_start_and_end(result, start_token='[', end_token=']')
        return f"### Force Calculation Result\n\n- **Sequence**: `{sequence}`\n- **Calculated Force**: `{force_value}`"
    except Exception as e:
        return f"### Error\n\nAn error occurred during the force calculation: {str(e)}"


def calculate_force_energy_from_sequence(sequence):
    """
    Calculates both the unfolding force and energy of a protein based on its sequence.
    Args:
        sequence (str): Amino acid sequence of the protein.
    Returns:
        str: A Markdown formatted string representing the calculated force and energy values.
    """
    try:
        prompt = f"CalculateForceEnergy<{sequence}>"
        task = extract_task(prompt, end_task_token='>') + ' '
        model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

        sample_output = generate_output_from_prompt(model, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
        force, energy = None, None  # Initialize variables to hold force and energy values
        for output in sample_output:
            result = tokenizer.decode(output, skip_special_tokens=True)
            data = extract_start_and_end(result, start_token='[', end_token=']')
            # Assume the data format is "force,energy" and split it accordingly
            values = data.split(',')
            if len(values) == 2:
                force, energy = values[0], values[1]
            else:
                raise ValueError("Expected force and energy values but got: " + data)
        return f"### Force and Energy Calculation Result\n\n- **Sequence**: `{sequence}`\n\n- **Unfolding Force**: `{force}`\n- **Energy**: `{energy}`"
    except Exception as e:
        return f"### Error\n\nAn error occurred during the force and energy calculation: {str(e)}"

def fix_pdb_file(original_pdb_path, fixed_pdb_path):
    """
    Inserts a CRYST1 record into a PDB file if it is missing.

    Args:
    original_pdb_path (str): Path to the original PDB file.
    fixed_pdb_path (str): Path where the fixed PDB file will be saved.
    """
    with open(original_pdb_path, 'r') as file:
        lines = file.readlines()

    #print (lines)
    # Check if the first record is CRYST1
    CRYST1 = False
    header = False
    for line in lines:
        LINE = str(line).split(sep=' ')
        for item in LINE:
            if re.search('CRYST1', item):
                CRYST1 = True
            if re.search('HEADER', item):
                header = True

    if (not CRYST1) and (not header):
        # Define a dummy CRYST1 record with a large unit cell
        # These numbers mean that the unit cell is a cube with 1000 Å edges.
        cryst1_record = "CRYST1 1000.000 1000.000 1000.000  90.00  90.00  90.00 P 1           1\n"
        lines.insert(0, cryst1_record)  # Insert the dummy CRYST1 record
        #lines.insert(0, 'header \n')

    with open(fixed_pdb_path, 'w') as file:
        file.writelines(lines)

    #print(f"Fixed PDB file written to {fixed_pdb_path}")
        
def fold_protein(sequence):
    """
    Predicts the 3D structure of a protein from its sequence and saves it to a PDB file.

    Args:
        sequence (str): Amino acid sequence of the protein.
    """
    name="DefaultProtein"
    filename = 'temp.fasta'
    output_path = code_dir
    fasta_content = f">{name}\n{sequence}\n"

    with open(filename, "w") as f:
        f.write(fasta_content)
        
    command = f"omegafold {filename} {output_path} --model 2 --device cpu "
    subprocess.run(command, shell=True)

    original_pdb_path = os.path.join(code_dir, f"{name}.pdb")
    os.makedirs(original_pdb_path, exist_ok=True)
    fixed_pdb_path = original_pdb_path  # In this case, we overwrite the original file
    fix_pdb_file(original_pdb_path, fixed_pdb_path)

    return f"{name}.pdb"

def generate_sequence_from_energy(energy):
    """
    Generates a protein sequence based on the specified energy level.
    Args:
        energy (str): Energy level to base the sequence generation on.
    Returns:
        str: A Markdown formatted string representing the generated protein sequence.
    """
    try:
        temperature=0.01
        prompt = f"GenerateEnergy<{energy}>"
        task = extract_task(prompt, end_task_token='>') + ' '
        model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

        sample_output = generate_output_from_prompt(model, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=float(temperature))
        for output in sample_output:
            result = tokenizer.decode(output, skip_special_tokens=True)
            sequence = extract_start_and_end(result, start_token='[', end_token=']')
        return f"### Sequence Generation from Energy\n\n- **Energy Level**: `{energy}`\n- **Generated Sequence**: `{sequence}`"
    except Exception as e:
        return f"### Error\n\nAn error occurred during sequence generation from energy: {str(e)}"

def get_FASTA_from_name(protein_name: str) -> str:
    """
    Fetches the FASTA sequence of a protein by its name from EBI protein API.

    Args:
        protein_name (str): The name of the protein to fetch the FASTA sequence for.

    Returns:
        str: A Markdown formatted string containing the FASTA sequence of the protein
             or an error message if the protein cannot be found or request fails.
    """
    size = 128
    requestURL = f"https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size={size}&protein={protein_name}"
    markdown_output = f"### FASTA Sequence for Protein: `{protein_name}`\n\n"
    
    try:
        r = requests.get(requestURL, headers={"Accept": "application/json"})
        r.raise_for_status()  # This will raise an HTTPError if the response was an error
        responseBody = r.text
        json_object = json.loads(responseBody)
        
        if len(json_object) > 0:
            fasta_sequence = json_object[0]['sequence']['sequence']
            markdown_output += f"```\n{fasta_sequence}\n```"
        else:
            markdown_output += "No results found."
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}"

    return markdown_output

def send_expasy_request(url, data):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        # "Referer": "https://web.expasy.org/protparam/",
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response

def sequence_to_pdb(sequence: str) -> dict:
    """
    EsmFold: Convert the sequence of the protein into 3D structures and generate PDB format files and calculate the residue accuracy of protein sequences, i.e., the plddt value. which return a PDF file content and residue accuracy.

    Args:
        sequence (str): The sequence of the protein.

    Returns:
        str: The text content with 3D structures.
    """
    data = {
        "seq": sequence,
    }
    response = send_expasy_request(url="http://127.0.0.1:5101/api/esmfold/topdb", data=data)
    result = json.loads(response.text)["msg"]
    
    target_directory = "DataFiles/pdb/code_protein"
    os.makedirs(target_directory, exist_ok=True)
    
    filename = os.path.join(target_directory,f"alpha_protein.pdb")
    with open(filename, "w") as f:
        f.write(result["output"][0])
    result["output"][0] = {os.path.abspath(filename)}

    output = f'The file has been stored with the name alpha_protein.pdb.\nThe mutated plddt values were {result["plddt"][0]}'
    
    return output

def calculate_protein_ANM(protein_name: str, n_modes: int = 10, cutoff: float = 12.0) -> str:
    """
    Calculates the Anisotropic Network Model (ANM) for a given protein structure.

    Args:
        protein_name (str): Name of the protein structure file (with or without .pdb extension).
        n_modes (int): Number of normal modes to calculate. Default is 10.
        cutoff (float): Cutoff distance for ANM calculations. Default is 12.0 Å.

    Returns:
        str: A Markdown formatted string that lists the first 'n_modes' eigenvalues
             from the ANM calculation or an error message if the calculation fails.
    """
    # Construct the file path based on the protein name
    if not protein_name.endswith('.pdb'):
        protein_name += '.pdb'
    protein_structure_path = os.path.join(code_dir, protein_name)

    # If the file does not exist, try to get it from the environment variable
    if not os.path.exists(protein_structure_path):
        protein_structure_path = os.getenv('PROTEIN_DATA_DIR', '')

    markdown_output = f"### ANM Calculation Results for `{protein_name}`\n\n"
    markdown_output += f"- **Number of Modes**: `{n_modes}`\n"
    markdown_output += f"- **Cutoff Distance**: `{cutoff}` Å\n\n"
    markdown_output += "**Eigenvalues**:\n\n"

    try:
        protein = prody.parsePDB(protein_structure_path)
        anm = prody.ANM('protein_anm')
        anm.buildHessian(protein, cutoff=cutoff)
        anm.calcModes(n_modes=n_modes)

        eigenvalues = anm.getEigvals()[:n_modes].round(4)  # Correct method to get eigenvalues
        for i, eigenvalue in enumerate(eigenvalues):
            markdown_output += f"- Mode {i+1}: `{eigenvalue}`\n"
    except Exception as e:
        markdown_output += f"Error occurred during ANM calculation: {str(e)}\n"

    return markdown_output


def analyze_protein_structure(protein_name: str) -> str:
    """
    Analyzes the secondary structure composition of a given protein structure.

    Args:
        protein_structure_path (str): Path to the protein's PDB file.

    Returns:
        str: A Markdown formatted string summarizing the composition of the secondary structures
             in the protein, or an error message if the analysis fails.
    """
    from Bio.PDB import PDBParser, DSSP

    # Construct the file path based on the protein name
    if not protein_name.endswith('.pdb'):
        protein_name += '.pdb'
    protein_structure_path = os.path.join(code_dir, protein_name)

    try:
        # Verify if the file exists
        if not os.path.exists(protein_structure_path):
            raise FileNotFoundError(f"No such file: '{protein_structure_path}'")

        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein_structure', protein_structure_path)
        model = structure[0]
        dssp = DSSP(model, protein_structure_path, dssp='mkdssp')

        # Initialize a dictionary for secondary structure counts
        secondary_structure_counts = {
            'H': 0,  # Alpha helix
            'B': 0,  # Isolated beta-bridge
            'E': 0,  # Extended strand
            'G': 0,  # 3-helix (3/10 helix)
            'I': 0,  # 5 helix (pi-helix)
            'T': 0,  # Hydrogen bonded turn
            'S': 0,  # Bend
            'P': 0,  # Poly-proline helices
            '-': 0   # None
        }

        # Count each secondary structure type
        for residue in dssp:
            secondary_structure_counts[residue[2]] += 1
        
        # Calculate the total number of residues with assigned secondary structure
        total_residues = sum(secondary_structure_counts.values())
        
        # Calculate the percentage content for each secondary structure type
        secondary_structure_percentages = {ss: (count / total_residues * 100) for ss, count in secondary_structure_counts.items()}
     
    # Return the results as a JSON string
        return json.dumps(secondary_structure_percentages, indent=4)
    except Exception as e:
       return f"erro with {e}"
def design_protein_alpha(length: int) -> str:
    """
    Designs a protein with an alpha structure based on a given length and generates its structure file in PDB format.

    Args:
        length (int): Length of the protein to be designed.

    Returns:
        str: A Markdown formatted string describing the generated protein and its file location.
    """
    # 指定使用第二张 GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    return design_protein_from_CATH(length, "alpha_protein", "1", steps=300, devices=device)


def design_protein_beta(length: int) -> str:
    """
    Designs a protein with a beta structure based on a given length and generates its structure file in PDB format.

    Args:
        length (int): Length of the protein to be designed.

    Returns:
        str: A Markdown formatted string describing the generated protein and its file location.
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    return design_protein_from_CATH(length, "beta_protein", "2.40", steps=300, devices=device)


def design_protein_alpha_beta(length: int) -> str:
    """
    Designs a protein with an alpha-beta structure based on a given length and generates its structure file in PDB format.

    Args:
        length (int): Length of the protein to be designed.

    Returns:
        str: A Markdown formatted string describing the generated protein and its file location.
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    return design_protein_from_CATH(length, "alpha_beta_protein", "3.30", steps=300, devices=device)
def design_protein_from_CATH(length: int, name: str, CATH_ANNOTATION: str, steps: int = 300, devices: str = 'cpu') -> str:
    """
    Designs a protein based on a given CATH annotation and generates its structure file in PDB format.

    Args:
        length (int): Length of the protein to be designed.
        name (str): Name for the generated protein structure file.
        CATH_ANNOTATION (str): CATH classification used to guide the protein design.
        steps (int): Number of sampling steps for protein generation. Default is 300.
        devices (str): Computing device to use ('cpu' or 'cuda'). Default is 'cpu'.

    Returns:
        str: A Markdown formatted string describing the generated protein and its file location.

    Raises:
        Exception: If there's an issue with generating the protein.
    """
    try:
        # Initialize Chroma and load the classifier model
        chroma = Chroma()
        
        proclass_model = graph_classifier.load_model("named:public", device=devices)
        conditioner = conditioners.ProClassConditioner("cath", CATH_ANNOTATION, model=proclass_model)

        # Generate protein based on CATH annotation
        cath_conditioned_protein, _ = chroma.sample(
            samples=1,
            steps=steps,
            conditioner=conditioner,
            chain_lengths=[int(length)],
            full_output=True
        )

        # Construct the file name and save the protein structure
        pdb_filename = f'{name}.pdb'
        pdb_path = os.path.join(code_dir, pdb_filename)
        os.makedirs(os.path.dirname(pdb_path), exist_ok=True)  # Create directory if it doesn't exist

        cath_conditioned_protein.to(pdb_path)
        sequence = cath_conditioned_protein.sequence()

        # Map CATH_ANNOTATION to corresponding type
        cath_annotation_mapping = {"1": "alpha", "2.40": "beta", "3.30": "alpha-beta"}
        cath_annotation_str = cath_annotation_mapping.get(CATH_ANNOTATION, CATH_ANNOTATION)

        # Format and return the result
        result_md = f"""## Protein Design Result
- **Protein Filename**: `{name}`
- **CATH Annotation**: `{cath_annotation_str}`
- **Sequence Length**: `{length}`

**Protein Sequence**:  
`{sequence}`"""

        return result_md
    except Exception as e:
        error_md = f"Error occurred during protein design: {str(e)}"
        return error_md


def design_protein_from_length(length: str):
    """
    Designs a new protein based on a specified length, optionally guided by a caption, 
    and saves the protein structure as a PDB file. Returns a detailed Markdown formatted description.

    Args:
        length (int): The desired length of the protein.

    Returns:
        str: A Markdown formatted string with details about the designed protein or an error message.
    """
    try:
        name = 'temp'
        caption=''
        device= 'cpu'
        steps= 300
        length = int(length)
        # Initialize Chroma with specified device
        chroma = Chroma(device='cpu')

        # Determine if a caption is provided to guide the protein design
        if caption:
            print(f"We use this caption to generate a protein: {caption}")
            procap_model = procap.load_model("named:public", device=device, strict_unexpected=False)
            conditioner = conditioners.ProCapConditioner(caption, -1, model=procap_model)
        else:
            conditioner = None

        # Sample a protein based on the specified length and (optional) caption
        protein = chroma.sample(chain_lengths=[length], steps=steps, conditioner=conditioner)

        # Save the designed protein structure to a PDB file
        pdb_filename = f"{name}.pdb"
        pdb_path = os.path.join(code_dir, pdb_filename)
        print(f"pdb_path:{pdb_path}")
        os.makedirs(os.path.dirname(pdb_path), exist_ok=True)  
        protein.to(pdb_path)

        # Retrieve the protein sequence
        sequence = protein.sequence()

        # Create a Markdown formatted string to summarize the results
        result_md = f"""
## Designed Protein Summary

- **Name**: `{name}`
- **Length**: `{length}`
- **Caption**: `{caption}`
- **Sampling Steps**: `{steps}`
- **PDB File**: `{pdb_filename}`
- **Sequence**:
    ```
    {sequence}
    ```
"""

        return result_md
    except Exception as e:
        error_md = f"Error occurred during protein design: {str(e)}"
        return error_md

def save_to_csv_file(input_json):
    """
    Converts an input JSON string to a CSV file and saves it to the specified location.

    Args:
        input_json (str): A JSON string containing data to be saved.

    Returns:
        str: A Markdown formatted string summarizing the operation.
    """

    try:
        data = json.loads(input_json)
        if isinstance(data, dict) and not all(isinstance(value, list) for value in data.values()):
            data = {key: [value] for key, value in data.items()}
        
        df = pd.DataFrame(data)
        
        target_directory = "DataFiles/csv"
        os.makedirs(target_directory, exist_ok=True)
        # protein_name = os.getenv('PROTEIN_NAME', '')
        full_output_path = os.path.join(target_directory, f'_temp.csv')
        
        df.to_csv(full_output_path, index=False)
        # os.environ['PROTEIN_NAME'] = ''
        return f"_temp.csv has been save to {full_output_path}."
    except Exception as e:
        return f"### Error\n\nFailed to create CSV file due to: `{str(e)}`."
    
def fetch_protein_structure_from_PDBID(PDB_id: str) -> str:
    """
    Fetches the protein structure file (.pdb) for the given PDB ID and saves it to a specified directory.

    Args:
        PDB_id (str): The PDB ID of the protein to fetch.

    Returns:
        str: A Markdown formatted string describing the outcome of the operation, including the file path of the saved PDB file or an error message.

    Raises:
        Exception: If the PDB ID is not valid or if there's an issue downloading or saving the file.
    """
    try:
        # Ensure PDB ID is a string
        if not isinstance(PDB_id, str):
            raise ValueError("PDB_id must be a string.")
        
        # Define the path for saving the PDB file
        pdb_file_path = f'{code_dir}/{PDB_id}.pdb'
        
        # Attempt to fetch and save the PDB file
        print(f"Fetching protein structure with PDB ID: {PDB_id}")
        fetch_result = fetchPDB(PDB_id, folder=code_dir, compressed=False, copy=True)
        
        # Check if fetch was successful
        if fetch_result:
            result_md = f"""## PDB File Fetching Result
- **PDB ID**: `{PDB_id}`
- **Saved File Path**: `{pdb_file_path}`"""
            return result_md
        else:
            raise Exception("Failed to fetch the PDB file.")
    except Exception as e:
        error_md = f"Error occurred during PDB file fetching: {str(e)}"
        return error_md


def calculate_force_from_seq(sequence):
    prompt = f"CalculateForce<{sequence}>"
    print(prompt)
    task = extract_task(prompt, end_task_token='>') + ' '
    model, tokenizer = ForceGPTmodel(model_name=Config().FORCEGPT_MODEL_PATH, device=device)

    sample_output = generate_output_from_prompt(model, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
    for sample_output in sample_output:
        result=tokenizer.decode(sample_output, skip_special_tokens=True)  
        extract_data=extract_start_and_end(result, start_token='[', end_token=']')
        
    return json.dumps(extract_data, indent=4)



import ast
import os
import random
import logging
from bs4 import BeautifulSoup
import json
import numpy as np

from ToolsFuns.utils.sendRequest import send_novopro_request, send_expasy_request
from ToolsFuns.Biology.support.processFun import *

def compute_pI_mW(protein):
    """
    Compute the theoretical isoelectric point (pI) and molecular weight (mW) of a protein sequence.
    The input should be a protein sequence.

    Returns:
        str: A string containing the calculated pI and mW.
    """
    try:
        data = {
            "protein": protein,
            "resolution": "average",
            "mandatory": ""
        }
        response = send_expasy_request("https://web.expasy.org/cgi-bin/compute_pi/pi_tool", data)

        soup = BeautifulSoup(response, 'html.parser')
        result = soup.find('strong', string="Theoretical pI/Mw:")

        if result and result.next_sibling:
            values = result.next_sibling.strip().split(" / ")
            if len(values) == 2:
                pi, mw = values
                output = f"""
**Input sequence:**

`{protein}`

**Theoretical pI:** {pi}

**Theoretical Mw:** {mw}
"""
                return output
        
        return "No 'Theoretical pI/Mw' content found."
    except Exception as e:
        return f"Error computing pI/Mw: {e}"



def compute_protein_parameters(protein):
    """
    Compute various physical and chemical parameters for a given protein sequence using Expasy ProtParam API.
    Parameters include molecular weight, theoretical pI, amino acid composition, atomic composition, 
    extinction coefficient, half-life, instability index, aliphatic index, and GRAVY.

    Args:
        protein (str): Protein sequence.

    Returns:
        str: Processed Markdown content.
    """
    try:
        data = {"sequence": protein, "mandatory": ""}

        response_text = send_expasy_request("https://web.expasy.org/cgi-bin/protparam/protparam", data)

        # print(html_content)
        processed_content = extract_and_process_protparam_html(response_text)
        # Convert to Markdown
        markdown_content = convert_protparam_to_markdown(processed_content)
        return markdown_content

    except Exception as e:
        return f"Error computing protein parameters: {e}"
    

def predict_hydrophilicity(protein: str) -> str:
    """
    Predict the hydrophilicity of a protein sequence.

    Args:
        protein (str): Protein sequence.

    Returns:
        str: Markdown content with hydrophilicity information.
    """
    try:
        cleaned_protein = protein.replace('\n', '').replace(' ', '')
        data = {
            "sr": "hp",
            "sq": cleaned_protein
        }

        response = send_novopro_request(data)
        if not response:
            raise ValueError("Server did not return a response.")

        try:
            data_list = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse server response. Invalid JSON format.")

        if len(data_list) <= 1 or not isinstance(data_list[1], dict):
            raise ValueError("Unexpected response structure. Expected a dictionary of positions and scores.")

        # Extracting hydrophobicity data
        hydrophilicity_data = data_list[1]

        # Construct a table of amino acids and scores, and only display the amino acids with scores
        markdown_table = "| Amino Acid | Score |\n|------------|-------|\n"
        for index, amino_acid in enumerate(cleaned_protein, start=1):
            score = hydrophilicity_data.get(str(index))
            if score is not None:  
                markdown_table += f"| {amino_acid}          | {score:.2f} |\n"

        generated_markdown = f"""
## Hydrophilicity Prediction

**Input Sequence:**  
`{cleaned_protein}`  

### Hydrophilicity Scores
{markdown_table}
"""
        return generated_markdown

    except Exception as e:
        return f"Error predicting hydrophilicity: {e}"


def predict_signalpeptide(protein)-> str:
    """
    This tool predict the signal peptide of the protein.
    Args:
        protein: protein sequence and the type of the protein. You can only input the following four types: euk, arch, Gram-, Gram+. euk means eukaryotes, arch means archaea, Gram- means gram-negative bacteria, Gram+ means gram-positive bacteria.
                format: sequence.type
    Returns:
          str: The Markdown content with signal peptide information.
    """

    try:
        cleaned_protein = protein.replace('\n', '').replace(' ', '')
        data = {
            "sr": "sgp",
            "sq": cleaned_protein,
            "org": "euk",
        }
        response = send_novopro_request(data)
        if not response:
            raise ValueError("Failed to get a response from the server.")

        try:
            data_list = json.loads(response)  
        except json.JSONDecodeError:
            raise ValueError("Failed to parse server response. Response format may be invalid.")

        
        if len(data_list) <= 1 or not isinstance(data_list[1], list):
            raise ValueError("Unexpected response structure.")

        probability = data_list[1][2]
        cleavage1 = data_list[1][3]
        cleavage2 = data_list[1][4]
        cleavage_probability = data_list[1][5]

        markdown = f'''
- **Input sequence:** `{cleaned_protein}`\n"
    
**Probability of having a signal peptide:** {probability}

**Type of signal peptide:** euk

**Cleavage site:** {cleavage1} - {cleavage2}

**Probability of the cleavage site:** {cleavage_probability}

'''
        return markdown
    except Exception as e:
        return f"Error predict signal peptide: {e}"


def predict_transmembrane(protein):
    """
    Predict the transmembrane regions of a protein sequence.

    Args:
        protein (str): The protein sequence.

    Returns:
        str: Markdown content with predicted transmembrane information or an error message.
    """
    try:
        cleaned_protein = protein.replace('\n', '').replace(' ', '')

        data = {
            "sr": "tmhmm",
            "sq": cleaned_protein
        }
        data_str = send_novopro_request(data=data)
        if not data_str:
            return "Error: Failed to retrieve data from the server."

        data_list = json.loads(data_str)
        if not data_list or len(data_list) <= 1:
            return "Error: Invalid data received from the server."

        pd_data = data_list[1][0]
        gif_name = data_list[1][1].replace('\\', '/').split('/')[-1]
        gif_url = f"https://www.novopro.cn/plus/tmp/{gif_name}"

        # Parse prediction data into a DataFrame
        df = parse_pd_data(pd_data)

        # Convert the DataFrame to Markdown format
        markdown_table = df.to_markdown(index=False)

        generated_markdown = f"""
## Predicted Transmembrane Information

![GIF Image]({gif_url})

{markdown_table}
"""
        return generated_markdown
    except Exception as e:
        return f"Error predicting transmembrane: {str(e)}"

def compute_extinction_coefficient(protein):
    """
    This tool compute the molar extinction coefficient and protein concentration of the protein, 
    and also provides information such as the protein isoelectric point. 

    Returns:
        str: The Markdown content with molar extinction coefficient. 
    """
    try:
        cleaned_protein = protein.replace('\n', '').replace(' ', '')

        data = {
            "sr": "pecc",
            "sq": cleaned_protein
        }

        response = send_novopro_request(data)

        try:
            data_list = json.loads(response)  
        except json.JSONDecodeError:
            raise ValueError("Failed to parse server response. Response format may be invalid.")

        
        if len(data_list) <= 1 or not isinstance(data_list[1], list):
            raise ValueError("Unexpected response structure.")

        epsilon_molar = data_list[1][0]
        molecular_weight = data_list[1][1]
        a1mg_ml280nm = data_list[1][2]
        protein_concentration = data_list[1][3]
        protein_isoelectric_point = data_list[1][4]

        generated_markdown = f'''
**Input sequence:** 

`{cleaned_protein}`

**Molecular Weight (kDa):** {molecular_weight}

**ε~molar~ (M^-1^cm^-1^):** {epsilon_molar}

**A^1mg/ml^~280nm~:** {a1mg_ml280nm}

**Protein Concentration (mg/ml):** {protein_concentration}

**Protein Isoelectric Point:** {protein_isoelectric_point}
'''

        return generated_markdown
    except Exception as e:
        return "Error compute extinction coefficient" 
    

def sequence_to_pdb(sequence: str) -> dict:
    """
    Convert the sequence of the protein into 3D structures and generate PDB format files and calculate the residue accuracy of protein sequences, i.e., the plddt value. which return a PDF file content and residue accuracy.

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
    
    target_directory = "ToolsKG/TempFiles/pdb/code_protein"
    os.makedirs(target_directory, exist_ok=True)

    filename = os.path.join(target_directory,f"alpha_protein.pdb")
    with open(filename, "w") as f:
        f.write(result["output"][0])
    result["output"][0] = {os.path.abspath(filename)}

    output = f'The file has been stored with the name alpha_protein.pdb.\nThe mutated plddt values were {result["plddt"][0]}'
    
    return output

def compute_protein_sequence_residue_accuracy(sequence: str) -> float:
    """
    Calculate the residue accuracy of protein sequences, i.e., the plddt value

    Args:
        sequence (str): 3D structured text content of the protein.

    Returns:
        float: The residue accuracy of protein sequences.
    """
    if "ATOM" in sequence:
        bs = []
        pdb = sequence.split("\n")
        for line in pdb:
            if line.startswith("ATOM"):
                b = float(line[60:66])
                bs.append(b)
        return np.mean(bs)
    else:
        data = {
            "seq": sequence,
        }
        response = send_expasy_request(url="http://127.0.0.1:5101/api/esmfold/topdb", data=data)
        result = json.loads(response.text)["msg"]
        return result['plddt'][0]

def generate_random_mutation_tool(sequence: str):
    """
    Randomized point mutation tool for proteins. Returns mutated protein sequences.

    Parameters:
        sequence (str): protein sequences.

    Returns:
        str: The residue accuracy of protein sequences.
    
    """
    amino_acids = ['S', 'N', 'K', 'A', 'V', 'W', 'D', 'M', 'P', 'G', 'H', 'E', 'L', 'Y', 'C', 'I', 'F', 'R', 'T', 'Q']
    
    rnd = random.randint(0, len(sequence))
    mutant = list(sequence.upper())

    substitute = mutant[rnd]
    aa = random.choice(amino_acids)
    while substitute == aa:
        aa = random.choice(amino_acids)
    mutant[rnd] = aa
    return "".join(mutant)

def cipher_optimizer_tool(sq: str, st: str = 'DNA', og: str = 'E.coli') -> str:
    """
    Codon Optimization Tool: Used to optimize codons for expression of recombinant genes in mainstream hosts. The parameters optimized include up to a dozen key parameters for both transcription and translation processes.

    Args:
        sq: protein or DNA sequences
        st: sequence type, should be Protein or DNA
        og: host for gene or protein expression. It can be E.coli, Arabidopsis thaliana or customized
        
    Returns:
        chemical information string

    Notes:
        your input should ideally be in the form of something like 'sq=ACTTAA, st=DNA, og=E.coli'
    """
    try:
        sq = sq.upper()
        data = {
            "sr": "co",
            "sq": sq,
            "st": st,
            "og": og,
            "ez": "",
        }
        data_str = send_novopro_request(data=data)
        result = ast.literal_eval(data_str)[1]
        if isinstance(result, list):
            formatted_data = [f"{value:.2f}" if isinstance(value, float) else value for value in result]

            generated_markdown = f'The optimized sequence: {formatted_data[0]}\n'\
                                f'CAI before optimization: {formatted_data[1]}\n'\
                                f'CAI after optimization: {formatted_data[2]}\n'\
                                f'Pre-optimization GC content(%): {formatted_data[-2]}\n'\
                                f'Post-optimization GC content(%): {formatted_data[-1]}'
            return generated_markdown
        return result


    except Exception as e:
        logging.error(f"Error predicting transmembrane: {e}")
        return "Parameter or request error, please pass in parameters as required"

def peptide_property_calculator(sq: str, aaCode: str = '0', nTerm: str = "", cTerm: str = "", disulphideBonds: str = ""):
    """
    Peptide Property Calculator: Calculate molecular weight, extinction coefficient, net peptide charge, peptide isoelectric point, and average hydrophobicity (GRAVY) of peptide properties.

    Args:
        sq: amino acid sequence
        aaCode: amino acid abbreviations, 0 for single letters, 1 for three letters
        nTerm: n-terminal modification
        cTerm: c-terminal modification
        disulphideBonds: disulfide bond position: (format: 1-8, 5-16)
        
    Returns:
        peptide properties string

    Notes:
        your input should ideally be in the form of something like 'sq=DYKDDDDK, aaCode=0'
    """
    try:
        sq = sq.upper()
        data = {
            "nTerm": nTerm,
            "cTerm": cTerm,
            "disulphideBonds": disulphideBonds,
            "aaCode": aaCode,
            "sequence": sq,
        }
        data_str = send_novopro_request(data=data)
        result = ast.literal_eval(data_str)[1]
        if isinstance(result, dict):
            
            generated_markdown = f'Average molecular weight: {result["mw"]} g/mol\n'\
                                f'Extinction coefficient: {result["ce"]}$M_{-1}cm_{-1}$\n'\
                                f'Theoretical isoelectric point: pH {result["pi"]}\n'\
                                f'GRAVY: {result["gravy"]}\n'\
                                f'Chemical formula: {result["cf"]}\n'\
                                f'Sequence length: {result["len"]}\n'\
                                f'three-letter word: {result["triplet"]}'
            return generated_markdown
        return result
    
    except Exception as e:
        logging.error(f"Error predicting transmembrane: {e}")
        return "Parameter or request error, please pass in parameters as required"

def oligonucleotide_calculator(sq: str, capping: str = "", tailing: str = "") -> str:
    """
    Oligonucleotide (primer) Calculator: The annealing temperature (Tm), molecular weight (MW), extinction coefficient (OD/μmol, μg/OD) of the oligonucleotides were calculated.

    Args:
        sq: oligonucleotide sequence
        capping: 5'-capping modification of proteins, can be filled in as needed
        tailing: 3'-tailing modification of proteins, can be filled in as needed
        
    Returns:
        Annealing temperature, molecular weight, extinction coefficient information of oligonucleotides.

    Notes:
        your input should ideally be in the form of something like 'sq=DYKDDDDK, capping="", tailing=""'
    """
    try:
        sq = sq.upper()
        data = {
            "sr": "oc",
            "sq": sq,
            "mod": f"{capping}::{tailing}",
        }
        data_str = send_novopro_request(data=data)
        result = ast.literal_eval(data_str)[1]
        if isinstance(result, list):
            generated_markdown = f'GC CONTENT(%): {result[6]}\n'\
                                f'Tm (°C): {result[8]}-{result[9]}\n'\
                                f'Molecular Weight (g/mole): {result[5]}\n'\
                                f'Extinction Coefficient (M-1cm-1): {result[7]}\n'\
                                f'nmole/OD260nm (1ml sample): {result[10]}\n'\
                                f'μg/OD260nm (1ml sample): {result[11]}\n'
            return generated_markdown
        return result
    
    except Exception as e:
        logging.error(f"Error predicting transmembrane: {e}")
        return "Parameter or request error, please pass in parameters as required"

def protein_signal_peptide_prediction(sq: str, org: str = "euk") -> str:
    """
    Protein Signal Peptide Prediction: Predicting the probability of the presence of a signal peptide.
    
    Args:
        sq: protein sequence
        org: protein species. It should be one of 'euk', 'gram-', 'gram+', 'arch'.  
        
    Returns:
        Annealing temperature, molecular weight, extinction coefficient information of oligonucleotides.

    Notes:
        In the field for protein species, 'euk' represents eukaryotes, 'gram-' represents gram-negative bacteria, 'gram+' represents gram-positive bacteria, 'arch' represents archaea.
        your input should ideally be in the form of something like 'sq=MGQPGNGSA, org=euk'
    """
    try:
        sq = sq.upper()
        data = {
            "sr": "sgp",
            "sq": sq,
            "org": org,
        }
        data_str = send_novopro_request(data=data)
        data_str = data_str.replace('\\', '')
        result = ast.literal_eval(data_str)[1]
        if isinstance(result, list):
            pic_url = f"https://www.novopro.cn/plus/{result[0]}"
            property = round(float(result[2])*100, 3)
            if result[1] == "OTHER":
                generated_markdown = f'![probability chart]({pic_url})\n'\
                                     f'The probability of having a signal peptide: {property}%'
            else:
                cut_property = round(float(result[5])*100, 3)
                generated_markdown = f'![probability chart]({pic_url})\n'\
                                     f'The probability of having a signal peptide: {property}%\n'\
                                     f'Signal peptide type: {result[1]}\n'\
                                     f'Cleavage site: {result[3]}-{result[4]}\n'\
                                     f'Probability: {cut_property}\n'
            return generated_markdown
        return result
    
    except Exception as e:
        logging.error(f"Error predicting transmembrane: {e}")
        return "Parameter or request error, please pass in parameters as required"
    
def protein_transmembrane_region_prediction(sq: str) -> str:
    # """
    # Protein transmembrane region prediction: Predicting regions of protein sequences that span cell membranes.
    # Args:
    #     sq: protein sequence
        
    # Returns:
    #     Predicted sequence of transmembrane regions.

    # Notes:
    #     your input should ideally be in the form of something like 'sq=MGQPGNGSA'
    # """
    try:
        sq = sq.upper()
        data = {
            "sr": "tmhmm",
            "sq": sq
        }
        data_str = send_novopro_request(data=data)
        data_str = data_str.replace('\\', '')
        result = ast.literal_eval(data_str)[1]
        if isinstance(result, list):

            pic_url = f"https://www.novopro.cn/{result[1]}"
            generated_markdown = '|Type|Start|End|Sequences|\n'\
                                 '|:-:|:-:|:-:|\n'
            for info in result[0]:
                msg = info.split(" ")
                generated_markdown += f'|{msg[0]}|{msg[1]}|{msg[2]}|{sq[int(msg[1]):int(msg[2])]}|\n'
                                    # f'The probability of having a signal peptide: {property}%\n'\
                                    # f'Signal peptide type: {result[1]}\n'\
                                    # f'Cleavage site: {result[3]}-{result[4]}\n'\
                                    # f'Probability: {cut_property}\n'
                generated_markdown += f"![prediction]({pic_url})"
            return generated_markdown
        return result
    
    except Exception as e:
        logging.error(f"Error predicting transmembrane: {e}")
        return "Parameter or request error, please pass in parameters as required"


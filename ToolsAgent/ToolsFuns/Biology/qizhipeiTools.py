import os
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer
import selfies as sf

from config import Config
base_dir = Config().QizhiPei_MODEL_PATH

def generate_molecule_description(selfies):
    """
    Given a molecule SELFIES, generates its English description using a pre-trained T5 model.
    
    Parameters:
    - selfies: A string representing the molecule in SELFIES format.
    
    Returns:
    - A Markdown string containing the molecule SELFIES and its generated English description.
    
    """
    if not isinstance(selfies, str) or not selfies:
        raise ValueError("Invalid SELFIES input. It must be a non-empty string.")
    
    try:
        model_name = "biot5-plus-base-chebi20/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = T5Tokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        task_definition = 'Definition: You are given a molecule SELFIES. Your job is to generate the molecule description in English that fits the molecule SELFIES.\n\n'
        task_input = f'Now complete the following example -\nInput: <bom>{selfies}<eom>\nOutput: '

        model_input = task_definition + task_input
        input_ids = tokenizer(model_input, return_tensors="pt").input_ids

        generation_config = model.config
        generation_config.max_length = 512
        generation_config.num_beams = 1

        outputs = model.generate(input_ids, max_length=generation_config.max_length, num_beams=generation_config.num_beams)

        description = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return f"**SELFIES:** `{selfies}`\n\n**Description:** {description}"
    except Exception as e:
        return f"Error generating description: {str(e)}"
    
def text_to_molecule_SELFIES(description):
    """
    Given a molecule description in English, generates its SELFIES and SMILES representation using a pre-trained T5 model.
    
    Parameters:
    - description: A string containing the molecule description in English.
    
    Returns:
    - A Markdown string containing the molecule description, SELFIES, and SMILES representation.
    
    Raises:
    - ValueError: If the description input is not a valid string.
    """
    if not isinstance(description, str) or not description:
        raise ValueError("Invalid description input. It must be a non-empty string.")
    
    try:
        model_name = "biot5-base-text2mol/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = T5Tokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        task_definition = 'Definition: You are given a molecule description in English. Your job is to generate the molecule SELFIES that fits the description.\n\n'
        task_input = f'Now complete the following example -\nInput: {description}\nOutput: '

        model_input = task_definition + task_input
        input_ids = tokenizer(model_input, return_tensors="pt").input_ids

        generation_config = model.config
        generation_config.max_length = 512
        generation_config.num_beams = 1

        outputs = model.generate(input_ids, max_length=generation_config.max_length, num_beams=generation_config.num_beams)
        output_selfies = tokenizer.decode(outputs[0], skip_special_tokens=True).replace(' ', '')
        
        output_smiles = sf.decoder(output_selfies)
        
        return f"**Description:** {description}\n\n**SELFIES:** `{output_selfies}`\n\n**SMILES:** `{output_smiles}`"
    except Exception as e:
        return f"Error generating SMILES: {str(e)}"

def add_prefix_to_amino_acids(protein_sequence):
    """Add a prefix '<p>' to each amino acid in the protein sequence."""
    amino_acids = list(protein_sequence)
    prefixed_amino_acids = ['<p>' + aa for aa in amino_acids]
    return ''.join(prefixed_amino_acids)

def predict_drug_target_interaction(SELFIES_and_sequence):
    """
    Predicts whether a given molecule (SELFIES format) and a protein sequence can interact with each other
    and returns the result in Markdown format with a brief explanation.
    
    Parameters:
    - input_data: A string containing the SELFIES of the molecule and the amino acid sequence of the protein,
                  separated by a dot. Extra quotes around the input are handled.
    
    Returns:
    - A Markdown formatted string containing the prediction and its explanation.
    """
    try:
        # Remove possible enclosing quotes and whitespace
        SELFIES_and_sequence = SELFIES_and_sequence.strip().strip("'")

        # Split input data on the first dot found
        split_data = SELFIES_and_sequence.split('.', 1)
        if len(split_data) < 2:
            return "Error: Input must contain a dot separating SELFIES and protein sequence."

        selfies_input, protein_input = split_data

        model_name = "biot5-base-dti-human/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = T5Tokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        protein_input_prefixed = add_prefix_to_amino_acids(protein_input)
        task_definition = 'Definition: Drug target interaction prediction task for the human dataset.\n\n'
        task_input = f'Now complete the following example -\nInput: Molecule: <bom>{selfies_input}<eom>\nProtein: <bop>{protein_input_prefixed}<eop>\nOutput: '

        model_input = task_definition + task_input
        input_ids = tokenizer(model_input, return_tensors="pt").input_ids

        generation_config = model.config
        generation_config.max_length = 8
        generation_config.num_beams = 1

        outputs = model.generate(input_ids, max_length=generation_config.max_length, num_beams=generation_config.num_beams)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return f"### Drug-Target Interaction Prediction\n- **Molecule (SELFIES):** `{selfies_input}`\n- **Protein Sequence:** `{protein_input}`\n- **Prediction:** `{prediction}`"
    except Exception as e:
        return f"Error in prediction: {str(e)}"

def predict_human_protein_interaction(protein_sequence_1: str, protein_sequence_2: str) -> str:
    """
    Predicts whether two given protein sequences can interact with each other
    using a fine-tuned BioT5 model for the protein-protein interaction task with human dataset.
    
    Parameters:
    - protein_sequence_1: The amino acid sequence of the first protein.
    - protein_sequence_2: The amino acid sequence of the second protein.
    
    Returns:
    - A Markdown formatted string containing the two protein sequences and the interaction prediction.
    """
    if not protein_sequence_1 or not protein_sequence_2:
        return "Invalid input: Both protein sequences must be provided."
    
    try:
        model_name = "biot5-base-peer-human_ppi/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        task_definition = 'Definition: Given two human protein sequences, predict whether they can interact with each other.\n\n'
        task_input = f'Now complete the following example -\nInput: Protein 1: {protein_sequence_1} Protein 2: {protein_sequence_2}\nOutput: '

        model_input = task_definition + " " + task_input
        input_ids = tokenizer.encode(model_input, return_tensors="pt", max_length=512, truncation=True)

        # Generate the prediction
        outputs = model.generate(input_ids, max_length=512, num_beams=1)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Format and return the result
        result = f"### Protein-Protein Interaction Prediction\n- **Protein 1 Sequence:** `{protein_sequence_1}`\n- **Protein 2 Sequence:** `{protein_sequence_2}`\n- **Prediction:** {prediction}"
        return result
    except Exception as e:
        return f"Error in prediction: {str(e)}"

def predict_yeast_protein_interaction(sequence_pair: str) -> str:
    """
    Predicts whether two given yeast protein sequences can interact with each other
    using a fine-tuned BioT5 model for the protein-protein interaction task with yeast dataset.
    
    Parameters:
    - input_data: A string containing two amino acid sequences of yeast proteins separated by a dot.
                  Extra quotes around the input are handled.
    
    Returns:
    - A Markdown formatted string containing the two yeast protein sequences and the interaction prediction.
    """
    # Remove possible enclosing quotes and whitespace
    sequence_pair = sequence_pair.strip().strip("'")

    # Split input data on the first dot found
    split_data = sequence_pair.split('.', 1)
    if len(split_data) < 2:
        return "Error: Input must contain a dot separating two protein sequences."

    protein_sequence_1, protein_sequence_2 = split_data

    if not protein_sequence_1 or not protein_sequence_2:
        return "Invalid input: Both protein sequences must be provided."
    try:
        model_name = "biot5-base-peer-yeast_ppi/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        task_definition = 'Definition: Given two yeast protein sequences, predict whether they can interact with each other.\n\n'
        task_input = f'Now complete the following example -\nInput: Protein 1: {protein_sequence_1} Protein 2: {protein_sequence_2}\nOutput: '

        model_input = task_definition + " " + task_input
        input_ids = tokenizer.encode(model_input, return_tensors="pt", max_length=512, truncation=True)

        # Generate the prediction
        outputs = model.generate(input_ids, max_length=512, num_beams=1)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Format and return the result
        result = f"### Yeast Protein-Protein Interaction Prediction\n- **Protein 1 Sequence:** `{protein_sequence_1}`\n- **Protein 2 Sequence:** `{protein_sequence_2}`\n- **Prediction:** {prediction}"
        return result
    except Exception as e:
        return f"Error in prediction: {str(e)}"

def predict_protein_solubility(protein_sequence: str) -> str:
    """
    Predicts the solubility of a given protein sequence using a fine-tuned BioT5 model
    for the protein solubility prediction task.
    
    Parameters:
    - protein_sequence: The amino acid sequence of the protein.
    
    Returns:
    - A Markdown formatted string containing the protein sequence and its solubility prediction.
    """
    if not protein_sequence:
        return "Invalid input: Protein sequence must be provided."
    
    try:
        model_name = "biot5-base-peer-solubility/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)


        # Specific task definition for protein solubility prediction
        task_definition = 'Definition: Predict the solubility of a protein given its amino acid sequence.\n\n'
        task_input = f'Now complete the following example -\nInput: Protein sequence: {protein_sequence}\nOutput: '

        model_input = task_definition + " " + task_input
        input_ids = tokenizer.encode(model_input, return_tensors="pt", max_length=512, truncation=True)

        # Generate the prediction
        outputs = model.generate(input_ids, max_length=512, num_beams=4, early_stopping=True)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Format and return the result
        result = f"### Protein Solubility Prediction\n- **Protein Sequence:** `{protein_sequence}`\n- **Prediction:** {prediction}"
        return result
    except Exception as e:
        return f"Error in prediction: {str(e)}"

def predict_protein_binary_localization(protein_sequence: str) -> str:
    """
    Predicts the binary localization of a given protein sequence using a fine-tuned BioT5 model
    for the protein binary localization prediction task.
    
    Parameters:
    - protein_sequence: The amino acid sequence of the protein.
    
    Returns:
    - A Markdown formatted string containing the protein sequence and its binary localization prediction.
    """
    if not protein_sequence:
        return "Invalid input: Protein sequence must be provided."
    
    try:
        model_name = "biot5-base-peer-binloc/"
        model_path = os.path.join(base_dir, model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, model_max_length=512)
        model = T5ForConditionalGeneration.from_pretrained(model_path)

        # Specific task definition for protein binary localization
        task_definition = 'Definition: Given a protein sequence, predict its binary localization.\n\n'
        task_input = f'Now complete the following example -\nInput: Protein sequence: {protein_sequence}\nOutput: '

        model_input = task_definition + task_input
        input_ids = tokenizer(model_input, return_tensors="pt").input_ids

        # Generate the prediction
        outputs = model.generate(input_ids, max_length=512, num_beams=1)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Format and return the result
        result = f"### Protein Binary Localization Prediction\n- **Protein Sequence:** `{protein_sequence}`\n- **Prediction:** {prediction}"
        return result
    except Exception as e:
        return f"Error in prediction: {str(e)}"
    

import pandas as pd
from typing import Dict, Union
from .utils import calculate_fingerprints, calculate_similarities
from Bio import pairwise2 as pw2
from app.core.config import Config

SMILES_SIMILARITY_THRESHOLD = 0.95
PROTEIN_SIMILARITY_THRESHOLD = 95.0

def check_compound_toxicity(input_smiles: str, db_path: str = Config().TOXIN_COMPOUND) -> Dict[str, Union[float, str]]:
    """
    Check if the input SMILES is similar to any toxic compound in the database.
    """
    df = pd.read_csv(db_path)
    input_fp = calculate_fingerprints([input_smiles])[0]
    db_fps = calculate_fingerprints(df['smiles'].tolist())

    for name, db_fp in zip(df['cmpdname'], db_fps):
        similarity = calculate_similarities(input_fp, db_fp)
        if similarity and similarity >= SMILES_SIMILARITY_THRESHOLD:
            return {'similarity': similarity, 'toxic_compound_name': name}
    return {'similarity': None, 'toxic_compound_name': None}

def check_protein_toxicity_bio(input_sequence: str, db_path: str = Config().TOXIN_PROTEIN) -> Dict[str, Union[float, str]]:
    """
    Check if the input protein sequence is similar to any toxic protein in the database.
    """
    df = pd.read_csv(db_path)
    for name, db_sequence in zip(df['Protein names'], df['Sequence']):
        alignments = pw2.align.localxs(input_sequence, db_sequence, -1, -1)
        percent_match = (alignments[0][2] / min(len(input_sequence), len(db_sequence))) * 100 if alignments else 0
        if percent_match >= PROTEIN_SIMILARITY_THRESHOLD:
            return {'percent_match': percent_match, 'toxic_protein_name': name}
    return {'percent_match': None, 'toxic_protein_name': None}

def check_toxicity_by_type(compounds_or_sequences):
    """
    Check toxicity by type.
    """
    toxic = False
    for compound_or_sequence, type_detected in compounds_or_sequences:
        if type_detected == 'smiles':
            result = check_compound_toxicity(compound_or_sequence)
            if result['similarity']:
                return True
        elif type_detected == 'sequence':
            result = check_protein_toxicity_bio(compound_or_sequence)
            if result['percent_match']:
                return True
    return False

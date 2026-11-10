import re
from typing import List, Tuple
from rdkit import Chem, DataStructs
from rdkit.Chem import rdMolDescriptors
from typing import List, Union

def extract_smiles_or_sequences(data_str: str) -> List[Tuple[str, str]]:
    """
    Extract SMILES or protein sequence from a string.
    """
    if not isinstance(data_str, str):
        return []

    extracted_items = []
    patterns = {
        'sequence': [r"protein sequence: ([^}]*)", r"Protein sequence:\s*([ARNDCQEGHILKMFPSTWYV]+)"],
        'smiles': [r"SMILES: ([^}]*)", r"\*\*Product\*\*:\s*([BCNOFPSIclbrsiH\[\]\(\)=+#%@-]+)"]
    }

    for item_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, data_str)
            extracted_items.extend((match, item_type) for match in matches)

    return extracted_items

def calculate_fingerprints(smiles_list: List[str]) -> List[Union[DataStructs.cDataStructs.ExplicitBitVect, None]]:
    """
    Compute molecular fingerprints for a set of SMILES strings.
    """
    generator = rdMolDescriptors.GetMorganGenerator(radius=2)
    fingerprints = [generator.GetFingerprint(Chem.MolFromSmiles(smiles)) if Chem.MolFromSmiles(smiles) else None for smiles in smiles_list]
    return fingerprints

def calculate_similarities(fp1, fp2) -> Union[float, None]:
    """
    Compute the average similarity score of two molecular fingerprints (Tanimoto, Dice, Cosine).
    """
    if fp1 is None or fp2 is None:
        return None
    similarities = {
        'Tanimoto': DataStructs.TanimotoSimilarity(fp1, fp2),
        'Dice': DataStructs.DiceSimilarity(fp1, fp2),
        'Cosine': DataStructs.CosineSimilarity(fp1, fp2)
    }
    return sum(similarities.values()) / len(similarities)

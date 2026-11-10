import base64
import glob
import os
import pickle
import numpy as np
import pandas as pd
import functools
import shlex
from rdkit import Chem
from rdkit.Chem import rdDetermineBonds, rdCIPLabeler, rdMolEnumerator, rdDeprotect, rdAbbreviations, rdSLNParse, rdMHFPFingerprint, rdMolDescriptors
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import rdEHTTools
from rdkit.Chem import rdTautomerQuery
from rdkit.Chem.rdTautomerQuery import TautomerQuery
from rdkit.Chem import Draw

#PatternFingerprintTemplate
def get_pattern_fingerprint(smiles):
    '''
    This tool is used to generate a pattern fingerprint for a molecule. The pattern fingerprint is a bit vector that encodes the presence or absence of particular substructures in the molecule. The substructures are defined by SMARTS patterns. The SMARTS patterns are converted to molecular fingerprints and then combined to generate the pattern fingerprint.

    Args:
        smiles (str): a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the fingerprint results， or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        query = rdTautomerQuery.TautomerQuery(mol)
        result = query.PatternFingerprintTemplate()


        markdown = f'''
## Pattern Fingerprint Result
{result}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#TautomerQueryCanSerialize
def can_serialize(smiles):
    '''
    This tool is used to check if a TautomerQuery object can be serialized.

    Args:
        smiles (str): a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the serialization result, or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        result = rdTautomerQuery.TautomerQueryCanSerialize()
        markdown = f'''
## Tautomer Query Can Serialize?
**Input SMILES:** {smiles}
**Result:** {result}
{result}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#AssignCIPLabels
def assign_CIPlabels(smiles):
    '''
    This tool is used to assign CIP labels to the atoms in a molecule. The CIP labels are used to describe the stereochemistry of the molecule. The labels are assigned based on the 3D structure of the molecule.

    Args:
        smiles (str): a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the CIP labels, or an error message.
    '''

    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        Chem.rdCIPLabeler.AssignCIPLabels(mol)

        markdown=f'''
##Assign CIP Labels
**Input SMILES:** {smiles}

**Result** 
**Output SMILES:**{Chem.MolToSmiles(mol)} 
**Number of atoms:** {mol.GetNumAtoms()}
**Bond Type:**
'''
        for bond in mol.GetBonds():
            bond_type = bond.GetBondTypeAsDouble()
            markdown += str(bond_type)+"\t"
        return markdown
    except Exception as e:
        markdown = f"An error occurred assiging CIP labels: {e}"
        return markdown

#Enumerate
def Enumerate(smiles):
    '''
    The rdkit.Chem.rdMolEnumerator.Enumerate function is used to perform enumeration on a given molecule and returns a MolBundle object containing multiple molecules generated during the enumeration process.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the enumeration results, or an error message.smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "").replace('.), '
    '''
    try:
        mol = Chem.MolFromSmiles(smiles)

        mol_bundle = rdMolEnumerator.Enumerate(mol)
        num_mols = mol_bundle.Size()

        markdown = f'''
## Enumerate Molecule
**Input SMILES:** {smiles}

**Result**
**Number of molecules:** {num_mols}
**Molecular List:**
'''
        for i in range(num_mols):
            mol = mol_bundle.GetMol(i)
            markdown += Chem.MolToSmiles(mol)
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



def deprotect(smiles: str):
    """
     The rdkit.Chem.rdDeprotect.Deprotect function removes protecting groups from a molecule, returning the deprotected version.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the deprotected SMILES, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        deprotected_mol = rdDeprotect.Deprotect(mol)

        markdown = f'''
## Deprotect Molecule
**Input SMILES:** {smiles}

**Result**
**Deprotected SMILES:** {Chem.MolToSmiles(deprotected_mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#CondenseAbbreviationSubstanceGroups
def condense_abbreviation_substance_groups(smiles):
    '''
    This tool finds and replaces abbreviation substance groups in a molecule, resulting in a compressed version of the molecule where the abbreviations are expanded.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the condensation results, or an error message.smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "").replace('.), '
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        condensed_mol = rdAbbreviations.CondenseAbbreviationSubstanceGroups(mol)
        markdown = f'''
## Condense Abbreviation Substance Groups
**Input SMILES:** {smiles}

**Result**
**Condensed SMILES:** {Chem.MolToSmiles(condensed_mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def sln_to_smiles(sln: str):
    """
    This tool is used to convert a SLN string to a SMILES string. Input SMILES directly without any other characters.
    Args:
        sln: a SLN string. Input SLN directly without any other characters.
    Returns:
        str: A markdown string wtih the SMILES, or an error message.
    """
    try:

        sln = sln.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = rdSLNParse.MolFromSLN(sln)
        if mol is None:
            raise ValueError("Invalid SLN string.")
        smiles = Chem.MolToSmiles(mol)
        markdown = f'''
## SLN to SMILES
**Input SLN:** {sln}
**Output SMILES:** {smiles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def create_shingling(smiles: str):
    """
    This tool is used to create a shingling for a molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the shingling, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        encoder = rdMHFPFingerprint.MHFPEncoder()
        shingling = encoder.CreateShinglingFromMol(mol)

        markdown = f'''
## Create Shingling
**Input SMILES:** {smiles}

**Result**
**Shingling Size:**{len(shingling)}
**Shingling:**
'''
        for element in shingling:
            markdown += element+", "
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def encode_mol(smiles: str):
    """
    This tool creates an MHFP vector from a molecule  using MHFP encoder, capturing structural information of the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the MinHashed Fingerprints.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        encoder = rdMHFPFingerprint.MHFPEncoder()
        MHFP = encoder.EncodeMol(mol)

        markdown = f'''
##MinHashed Fingerprints
**Input SMILES:** {smiles}

**Result**
**MHFP Size:**{len(MHFP)}
**MHFP:**
'''
        for element in MHFP:
            markdown += str(element)+", "
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



def encode_SECFP(smiles: str):
    """
    This tool creates an SECFP vector from a molecule using SECFP encoder, capturing structural information of the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the SECFP vector, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        encoder = rdMHFPFingerprint.MHFPEncoder()
        SECFP = encoder.EncodeSECFPMol(mol)

        markdown = f'''
## SECFP
**Input SMILES:** {smiles}

**Result**
**SECFP Size:**{len(SECFP)}
**SECFP:**
'''
        for element in SECFP:
            markdown += str(element)+", "
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#rdMolDescriptors.BCUT2D
def get_BCUT(smiles: str):
    """
    This tool computes the 2D BCUT descriptors for a given molecule, representing mass, Gasteiger charge, Crippen logP, and Crippen MR values.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the BCUT2D descriptors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        bcut2d = rdMolDescriptors.BCUT2D(mol)
        markdown = f'''
## BCUT2D
**Input SMILES:** {smiles}

**Result**
**mass eigen value high:**{bcut2d[0]}
**mass eigen value low:**{bcut2d[1]}
**gasteiger charge eigenvalue high:**{bcut2d[2]}
**gasteiger charge low:**{bcut2d[3]}
**crippen lowgp eigenvalue high:**{bcut2d[4]}
**crippen lowgp low:**{bcut2d[5]}
**crippen mr eigenvalue high：**{bcut2d[6]}
**crippen mr low:**{bcut2d[7]}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



#CalcAUTOCORR2D
def calculate_Autocorrelation2D(smiles: str):
    """
    This tool computes the 2D autocorrelation descriptors for a given molecule, capturing the spatial arrangement of atoms in the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the 2D autocorrelation descriptors vector, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        autocorr_desc = rdMolDescriptors.CalcAUTOCORR2D(mol)
        markdown = f'''
## 2D Autocorrelation Descriptors
**Input SMILES:** {smiles}

**2D Autocorrelation descriptors vector**
{autocorr_desc}
'''
        return markdown

    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



#CalcAUTOCORR3D
def calculate_Autocorrelation3D(smiles: str):
    """
    This tool computes the 3D autocorrelation descriptors for a given molecule, capturing the spatial arrangement of atoms in the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the 3D autocorrelation descriptors vector, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        AllChem.EmbedMolecule(mol, randomSeed=42)
        autocorr_desc = rdMolDescriptors.CalcAUTOCORR3D(mol)
        markdown = f'''
## 
**Input SMILES:** {smiles}

**3D Autocorrelation descriptors vector**
{autocorr_desc}
'''
        return markdown

    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_asphericity(smiles: str):
    """
    This tool calculates the asphericity descriptor for a molecule, which measures how much the molecule deviates from a perfectly spherical shape.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih asphericity descripto(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        AllChem.EmbedMolecule(mol, randomSeed=42)
        asphericity = rdMolDescriptors.CalcAsphericity(mol)

        markdown = f'''
## Asphericity
**Input SMILES:** {smiles}
**Asphericity:** {asphericity}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_chi0n(smiles: str):
    """
    This tool calculates the chi^0 (chi-zero) cluster index, which represents a topological descriptor related to molecular branching.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^0 (chi-zero) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^0 cluster index
        chi0 = rdMolDescriptors.CalcChi0n(mol)
        markdown = f'''
##Calculta Chi-zero Cluster Index
**Input SMILES:** {smiles}
**Chi-zero Cluster Index:** {chi0}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown
        
def calculate_chi0v(smiles: str):
    """
    This function calculates the Chi^0v (Chi-zero-v) valence molecular graph index for a molecule, which is used to describe the topology of the molecule. It returns a float value.

    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^0 (chi-zero) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^0 cluster index
        chi0 = rdMolDescriptors.CalcChi0v(mol)
        markdown = f'''
##Chi^0v (Chi-zero-v) valence molecular graph index 
**Input SMILES:** {smiles}
**Chi-zero-v Cluster Index:** {chi0}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_chi1n(smiles: str):
    """
    This tool calculates the chi^1 (chi-one) cluster index, which represents a topological descriptor related to molecular branching.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^1 (chi-one) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^1 cluster index
        chi1 = rdMolDescriptors.CalcChi1n(mol)
        markdown = f'''
##Calculta Chi-one Cluster Index
**Input SMILES:** {smiles}
**Chi-one Cluster Index:** {chi1}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_chi1v(smiles: str):
    """
    This function calculates the Chi^1v (Chi-one-v) valence molecular graph index for a molecule, which is used to describe the topology of the molecule. It returns a float value.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^1 (chi-one) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^1 cluster index
        chi1 = rdMolDescriptors.CalcChi1v(mol)
        markdown = f'''##Chi^1v (Chi-one-v) valence molecular graph index
**Input SMILES:** {smiles}
**Chi-one-v Cluster Index:** {chi1}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_chi2n(smiles: str):
    """
    This tool calculates the chi^2 (chi-two) cluster index, which represents a topological descriptor related to molecular branching.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^2 (chi-two) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^2 cluster index
        chi2 = rdMolDescriptors.CalcChi2n(mol)
        markdown = f'''##Calculta Chi-two Cluster Index
**Input SMILES:** {smiles}
**Chi-two Cluster Index:** {chi2}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_chi2v(smiles: str):
    """
    This function calculates the Chi^2v (Chi-two-v) valence molecular graph index for a molecule, which is used to describe the topology of the molecule. It returns a float value.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^2 (chi-two) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^2 cluster index
        chi2 = rdMolDescriptors.CalcChi2v(mol)
        markdown = f'''##Chi^2v (Chi-two-v) valence molecular graph index
**Input SMILES:** {smiles}
**Chi-two-v Cluster Index:** {chi2}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_chi3n(smiles: str):
    """
    This tool calculates the chi^3 (chi-three) cluster index, which represents a topological descriptor related to molecular branching.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^3 (chi-three) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^3 cluster index
        chi3 = rdMolDescriptors.CalcChi3n(mol)
        markdown = f'''##Calculta Chi-three Cluster Index
**Input SMILES:** {smiles}
**Chi-three Cluster Index:** {chi3}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_chi3v(smiles: str):
    """
    This function calculates the Chi^3v (Chi-three-v) valence molecular graph index for a molecule, which is used to describe the topology of the molecule. It returns a float value.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^3 (chi-three) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^3 cluster index
        chi3 = rdMolDescriptors.CalcChi3v(mol)
        markdown = f'''##Chi^3v (Chi-three-v) valence molecular graph index
**Input SMILES:** {smiles}
**Chi-three-v Cluster Index:** {chi3}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_chi4n(smiles: str):
    """
    This tool calculates the chi^4 (chi-four) cluster index, which represents a topological descriptor related to molecular branching.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^4 (chi-four) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^4 cluster index
        chi4 = rdMolDescriptors.CalcChi4n(mol)
        markdown = f'''##Calculta Chi-four Cluster Index
**Input SMILES:** {smiles}
**Chi-four Cluster Index:** {chi4}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_chi4v(smiles: str):
    """
    This function calculates the Chi^4v (Chi-four-v) valence molecular graph index for a molecule, which is used to describe the topology of the molecule. It returns a float value.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih chi^4 (chi-four) cluster index(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.MolFromSmiles('CCO')
        # Calculate the chi^4 cluster index
        chi4 = rdMolDescriptors.CalcChi4v(mol)
        markdown = f'''##Chi^4v (Chi-four-v) valence molecular graph index
**Input SMILES:** {smiles}
**Chi-four-v Cluster Index:** {chi4}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_coulombmatrix(smiles :str):
    """
    This tool calculates the Coulomb matrix for a molecule, which represents the electrostatic interactions between atoms in the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Coulomb matrix, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        coulomb_mat = rdMolDescriptors.CalcCoulombMat(mol)
        markdown = f'''
## Coulomb Matrix
**Input SMILES:** {smiles}
**Coulomb Matrix:** 
'''
        for i, matrix in enumerate(coulomb_mat):
            markdown += f"Coulomb Matrix {i + 1}:\n"
            coulomb_matrices_list = list(matrix)
            markdown += f"{coulomb_matrices_list}\n"
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_crippen_descriptors(smiles: str):
    """
  This function calculates the Wildman-Crippen logP and MR (molecular refractivity) values for a given molecule in RDKit.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Wildman-Crippen logp and mr values, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        logp, mr = rdMolDescriptors.CalcCrippenDescriptors(mol)
        markdown = f'''## Crippen Descriptors
**Input SMILES:** {smiles}
**LogP:** {logp}
**MR:** {mr}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_EEMcharges(smiles: str):
    """

This function computes the EEM (Electronegativity Equalization Method) atomic partial charges for a given molecule using its atomic properties.

    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih a list of partial charges assigned to each atom in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        eem_charges = rdMolDescriptors.CalcEEMcharges(mol)

        markdown = f'''## EEM Charges
**Input SMILES:** {smiles}
**EEM Charges:** {eem_charges}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_Eccentricity(smiles: str):
    '''
    This function calculates the eccentricity of a molecule, which is a measure of its shape.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the eccentricity value(a float value), or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate eccentricity
        eccentricity = rdMolDescriptors.CalcEccentricity(mol)
        markdown = f'''
## Eccentricity
**Input SMILES:** {smiles}
**Eccentricity:** {eccentricity}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_exact_molweight(smiles: str):
    '''
    This function calculates the exact molecular weight of a molecule, which is the sum of the atomic weights of all atoms in the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the exact molecular weight(a float value), or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate exact molecular weight
        exact_molweight = rdMolDescriptors.CalcExactMolWt(mol)
        markdown = f'''## Exact Molecular Weight
**Input SMILES:** {smiles}
**Exact Molecular Weight:** {exact_molweight}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_FractionCSP3(smiles: str):
    '''
    This function calculates the fraction of sp3-hybridized carbon atoms in a molecule, which is a measure of its shape.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the fraction of sp3-hybridized carbon atoms(a float value), or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the fraction of sp3-hybridized carbon atoms
        fraction_csp3 = rdMolDescriptors.CalcFractionCSP3(mol)
        markdown = f'''## Fraction of SP3 hybridized carbon atoms
**Input SMILES:** {smiles}
**Fraction of sp3-hybridized Carbon Atoms:** {fraction_csp3}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_GETAWAY(smiles: str):
    '''
    This function calculates the GETAWAY descriptors for a molecule, which capture the shape and size of the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the GETAWAY descriptors, or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        getaway = rdMolDescriptors.CalcGETAWAY(mol)
        markdown = f'''## GETAWAY Descriptors
**Input SMILES:** {smiles}
**GETAWAY Descriptors:** {getaway}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_HallKierAlpha(smiles: str):
    '''
    This function calculates the Hall-Kier alpha index for a molecule, which is a measure of its shape.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Hall-Kier alpha index(a float value), or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate Hall-Kier alpha index
        alpha = rdMolDescriptors.CalcHallKierAlpha(mol)
        markdown = f'''##Calculate Hall-Kier Alpha
**Input SMILES:** {smiles}
**Hall-Kier Alpha Index:** {alpha}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_InertialShapeFactor(smiles: str):
    '''

    This function calculates the Inertial Shape Factor of a molecule, which is a measure of its shape. The Inertial Shape Factor ranges from 0 to 1, where values closer to 1 indicate a more spherical shape and values closer to 0 indicate a more linear shape.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the inertial shape factor(a float value), or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate inertial shape factor
        inertial_shape_factor = rdMolDescriptors.CalcInertialShapeFactor(mol)
        markdown = f'''## Inertial Shape Factor
**Input SMILES:** {smiles}
**Inertial Shape Factor:** {inertial_shape_factor}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_Kappa1(smiles: str):
    """
    This function computes the Kappa1 (κ1) value of a molecule, which is a topological descriptor representing its shape complexity or branching degree. The Kappa1 value is a floating-point number calculated based on the molecular graph topology.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Kappa1 value(a float value), or an error message.
     """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate Kappa1 shape index
        kappa1 = rdMolDescriptors.CalcKappa1(mol)
        markdown = f'''##Calculate Kappa1
**Input SMILES:** {smiles}
**Kappa1 Shape Index:** {kappa1}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_Kappa2(smiles: str):
    """
    This function computes the Kappa2 (κ2) value of a molecule, which is a topological descriptor representing its shape complexity or branching degree. The Kappa2 value is a floating-point number calculated based on the molecular graph topology.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Kappa2 value(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate Kappa2 shape index
        kappa2 = rdMolDescriptors.CalcKappa2(mol)
        markdown = f'''##Calculate Kappa2
**Input SMILES:** {smiles}
**Kappa2 Shape Index:** {kappa2}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_Kappa3(smiles: str):
    """
    This function computes the Kappa3 (κ3) value of a molecule, which is a topological descriptor representing its shape complexity or branching degree. The Kappa3 value is a floating-point number calculated based on the molecular graph topology.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Kappa3 value(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate Kappa3 shape index
        kappa3 = rdMolDescriptors.CalcKappa3(mol)
        markdown = f'''##Calculate Kappa3
**Input SMILES:** {smiles}
**Kappa3 Shape Index:** {kappa3}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_LabuteASA(smiles: str):
    """
    This function calculates the Labute accessible surface area (ASA) value for a molecule, which is a measure of the solvent-accessible surface area of the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the Labute ASA value(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate Labute ASA
        labute_asa = rdMolDescriptors.CalcLabuteASA(mol)
        markdown = f'''##Calculate Labute ASA
**Input SMILES:** {smiles}
**Labute ASA:** {labute_asa}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_MORSE(smiles: str):
    """
    This tool calculates the Molecule Representation of Structures based on Electron diffraction (MORSE) descriptors for a given molecule. MORSE descriptors provide a representation of molecular structures based on electron diffraction concepts.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih a list containing the calculated MORSE descriptors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        morse = rdMolDescriptors.CalcMORSE(mol)
        markdown = f'''##MORSE Descriptors
**Input SMILES:** {smiles}
**MORSE Descriptors:** {morse}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_MolFormula(smiles: str):
    """
    This function calculates the molecular formula of a molecule, which is a string representing the number and type of atoms in the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the molecular formula, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate molecular formula
        mol_formula = rdMolDescriptors.CalcMolFormula(mol)
        markdown = f'''##Calculate Molecular Formula
**Input SMILES:** {smiles}
**Molecular Formula:** {mol_formula}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NPR1(smiles: str):
    """
    This function calculates the NPR1 (Normalized Principal Moments Ratio) descriptor for a molecule, which serves as a descriptor for the distribution of charges within the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the NPR1 value(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)

        # Calculate NPR1
        npr1 = rdMolDescriptors.CalcNPR1(mol)
        markdown = f'''##Calculate  Normalized Partial Charge(NPR1)
**Input SMILES:** {smiles}
**NPR1:** {npr1}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NPR2(smiles: str):
    """
    This function calculates the NPR2 (Normalized Principal Moments Ratio) descriptor for a molecule, which serves as a descriptor for the distribution of charges within the molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the NPR2 value(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)

        # Calculate NPR2
        npr2 = rdMolDescriptors.CalcNPR2(mol)
        markdown = f'''##Calculate Normalized Partial Charge(NPR2)
**Input SMILES:** {smiles}
**NPR2:** {npr2}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumAliphaticCarbocycles(smiles: str):
    """
    This function calculates the number of aliphatic carbocycles in a molecule. Aliphatic carbocycles are cyclic structures that contain at least one non-aromatic bond.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such carbocycles, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aliphatic rings
        num_aliphatic_rings = rdMolDescriptors.CalcNumAliphaticRings(mol)
        markdown = f'''##The number of aliphatic carbocycles
**Input SMILES:** {smiles}
**Number of aliphatic carbocycles:** {num_aliphatic_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumAliphaticHeterocycles(smiles: str):
    """
    This function calculates the number of aliphatic heterocycles in a molecule. Aliphatic heterocycles are cyclic structures that contain at least one non-aromatic bond and at least one heteroatom (an atom other than carbon).    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such aliphatic heterocycles, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aliphatic rings
        num_aliphatic_rings = rdMolDescriptors.CalcNumAliphaticHeterocycles(mol)
        markdown = f'''##The number of aliphatic heterocycles
**Input SMILES:** {smiles}
**Number of aliphatic heterocycles:** {num_aliphatic_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumAliphaticRings(smiles: str):
    """
    This tool calculates the number of aliphatic rings in a molecule. Aliphatic rings are ring structures that contain at least one non-aromatic bond.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such aliphatic rings, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aliphatic rings
        num_aliphatic_rings = rdMolDescriptors.CalcNumAliphaticRings(mol)
        markdown = f'''##The number of aliphatic rings
**Input SMILES:** {smiles}
**Number of aliphatic rings:** {num_aliphatic_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumAmideBonds(smiles: str):
    """
    This function calculates the number of amide bonds in a molecule. Amide bonds are chemical bonds formed between a carbonyl group and an amino group.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such amide bonds, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of amide bonds
        num_amide_bonds = rdMolDescriptors.CalcNumAmideBonds(mol)
        markdown = f'''##The number of amide bonds
**Input SMILES:** {smiles}
**Number of amide bonds:** {num_amide_bonds}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

        
def calculate_NumAromaticCarbocycles(smiles: str):
    """
    This function calculates the number of aromatic carbocycles in a molecule. Aromatic carbocycles are cyclic structures composed entirely of carbon atoms with alternating single and double bonds (aromaticity) in at least one ring.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such aromatic carbocycles, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aromatic carbocycles
        num_aromatic_carbocycles = rdMolDescriptors.CalcNumAromaticCarbocycles(mol)
        markdown = f'''##The number of aromatic carbocycles
**Input SMILES:** {smiles}
**Number of aromatic carbocycles:** {num_aromatic_carbocycles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



def calculate_NumAromaticHeterocycles(smiles: str):
    """
    This function calculates the number of aromatic heterocycles in a molecule. Aromatic heterocycles are cyclic structures that contain at least one heteroatom (an atom other than carbon) and exhibit aromaticity. es.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such aromatic heterocycl, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aromatic heterocycles
        num_aromatic_heterocycles = rdMolDescriptors.CalcNumAromaticHeterocycles(mol)
        markdown = f'''##The number of aromatic heterocycles
**Input SMILES:** {smiles}
**Number of aromatic heterocycles:** {num_aromatic_heterocycles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumAromaticRings(smiles: str):
    """
    This tool calculates the number of aromatic rings in a molecule. Aromatic rings are cyclic structures composed of alternating single and double bonds (aromaticity) and exhibit stability due to delocalization of electrons.     Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such aromatic rings, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of aromatic rings
        num_aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
        markdown = f'''##The number of aromatic rings
**Input SMILES:** {smiles}
**Number of aromatic rings:** {num_aromatic_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumAtomStereoCenters(smiles: str):
    """
    This function calculates the number of atom stereo centers in a molecule. Atom stereo centers are atoms that are chiral centers and are not part of a ring structure.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of atomic stereocenters, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of atom stereo centers
        num_atom_stereo_centers = rdMolDescriptors.CalcNumAtomStereoCenters(mol)
        markdown = f'''##The number of atom stereo centers
**Input SMILES:** {smiles}
**Number of atom stereo centers:** {num_atom_stereo_centers}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

        
def calculate_NumAtoms(smiles: str):
    """
    This function calculates the number of atoms in a molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of atoms in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of atoms
        num_atoms = mol.GetNumAtoms()
        markdown = f'''##The number of atoms
**Input SMILES:** {smiles}
**Number of atoms:** {num_atoms}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown
        

def calculate_NumBridgeheadAtoms(smiles: str):
    """
    This function calculates the number of bridgehead atoms in a molecule. Bridgehead atoms are atoms that are part of a bridged ring structure.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of bridgehead atoms, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of bridgehead atoms
        num_bridgehead_atoms = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
        markdown = f'''##The number of bridgehead atoms
**Input SMILES:** {smiles}
**Number of bridgehead atoms:** {num_bridgehead_atoms}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumHBA(smiles: str):
    """
    This function calculates the number of hydrogen bond acceptors (HBA) in a molecule. Hydrogen bond acceptors are atoms capable of forming hydrogen bonds by accepting a hydrogen atom.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih integer representing the count of such hydrogen bond acceptors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of hydrogen bond acceptors
        num_h_acceptors = rdMolDescriptors.CalcNumHBA(mol)
        markdown = f'''##The number of hydrogen bond acceptors
**Input SMILES:** {smiles}
**Number of hydrogen bond acceptors:** {num_h_acceptors}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumHBD(smiles: str):
    """
    This function calculates the number of hydrogen bond donors (HBD) in a molecule. Hydrogen bond donors are atoms capable of forming hydrogen bonds by donating a hydrogen atom.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih integer representing the count of hydrogen bond donors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of hydrogen bond donors
        num_h_donors = rdMolDescriptors.CalcNumHBD(mol)
        markdown = f'''##The number of hydrogen bond donors
**Input SMILES:** {smiles}
**Number of hydrogen bond donors:** {num_h_donors}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumHeavyAtoms(smiles: str):
    """
    This tool calculates the number of heavy atoms in a molecule. Heavy atoms are atoms other than hydrogen.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih integer representing the number of heavy atoms for a molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of heavy atoms
        num_heavy_atoms = mol.GetNumHeavyAtoms()
        markdown = f'''##The number of heavy atoms
**Input SMILES:** {smiles}
**Number of heavy atoms:** {num_heavy_atoms}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumHeteroatoms(smiles: str):
    """
    This tool calculates the number of heteroatoms in a molecule. Heteroatoms are atoms other than carbon and hydrogen.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of heteroatoms in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of heteroatoms
        num_heteroatoms = rdMolDescriptors.CalcNumHeteroatoms(mol)
        markdown = f'''##The number of heteroatoms
**Input SMILES:** {smiles}
**Number of heteroatoms:** {num_heteroatoms}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumHeterocycles(smiles: str):
    """
    This tool calculates the number of heterocycles in a molecule. Heterocycles are cyclic structures that contain at least one heteroatom (an atom other than carbon).
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such heterocycles, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of heterocycles
        num_heterocycles = rdMolDescriptors.CalcNumHeterocycles(mol)
        markdown = f'''##The number of heterocycles
**Input SMILES:** {smiles}
**Number of heterocycles:** {num_heterocycles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

        

def calculate_NumLipinskiHBA(smiles: str):
    """
    This tool calculates the number of Lipinski hydrogen bond acceptors (HBA) in a molecule, which is a measure used in drug-likeness evaluation according to Lipinski's rule of five. Lipinski's rule suggests that molecules with no more than five hydrogen bond acceptors tend to have better oral bioavailability.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the number of Lipinski H-bond acceptors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of hydrogen bond acceptors according to the Lipinski rule of five
        num_lipinski_hba = rdMolDescriptors.CalcNumLipinskiHBA(mol)
        markdown = f'''##The number of Lipinski H-bond acceptors
**Input SMILES:** {smiles}
**Number of Lipinski H-bond acceptors:** {num_lipinski_hba}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumLipinskiHBD(smiles: str):
    """
    This tool calculates the number of Lipinski hydrogen bond donors (HBD) in a molecule, which is a measure used in drug-likeness evaluation according to Lipinski's rule of five.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the number of Lipinski H-bond donors, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of hydrogen bond donors according to the Lipinski rule of five
        num_lipinski_hbd = rdMolDescriptors.CalcNumLipinskiHBD(mol)
        markdown = f'''##The number of Lipinski H-bond donors
**Input SMILES:** {smiles}
**Number of Lipinski H-bond donors:** {num_lipinski_hbd}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_NumRings(smiles: str):
    """
    This tool calculates the number of rings in a molecule.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of rings in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of rings
        num_rings = rdMolDescriptors.CalcNumRings(mol)
        markdown = f'''##The number of rings
**Input SMILES:** {smiles}
**Number of rings:** {num_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumRotatableBonds(smiles: str):
    """
    This tool calculates the number of rotatable bonds in a molecule. Rotatable bonds are single bonds that are not part of a ring structure and are not terminal (i.e., not connected to a hydrogen atom).
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of rotatable bonds in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of rotatable bonds
        num_rotatable_bonds = rdMolDescriptors.CalcNumRotatableBonds(mol)
        markdown = f'''##The number of rotatable bonds
**Input SMILES:** {smiles}
**Number of rotatable bonds:** {num_rotatable_bonds}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumSaturatedCarbocycles(smiles: str):
    """
    This function calculates the number of saturated carbocycles in a molecule. Saturated carbocycles are cyclic structures composed entirely of carbon atoms with single bonds (no double bonds).
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such saturated carbocycles, or an error message.
    """
    try:
        cleaned_smiles = smiles.replace(' ', '').replace('\n', '')
        mol = Chem.MolFromSmiles(cleaned_smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of saturated carbocycles
        num_saturated_carbocycles = rdMolDescriptors.CalcNumSaturatedCarbocycles(mol)
        markdown = f'''##The number of saturated carbocycles
**Input SMILES:** {cleaned_smiles}
**Number of saturated carbocycles:** {num_saturated_carbocycles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumSaturatedHeterocycles(smiles: str):
    """
    This function calculates the number of saturated heterocycles in a molecule. Saturated heterocycles are cyclic structures that contain at least one heteroatom (an atom other than carbon) and are composed entirely of single bonds (no double bonds).
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such saturated heterocycles, or an error message.
    """
    try:
        cleaned_smiles = smiles.replace(' ', '').replace('\n', '')
        mol = Chem.MolFromSmiles(cleaned_smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of saturated heterocycles
        num_saturated_heterocycles = rdMolDescriptors.CalcNumSaturatedHeterocycles(mol)
        markdown = f'''##The number of saturated heterocycles
**Input SMILES:** {cleaned_smiles}
**Number of saturated heterocycles:** {num_saturated_heterocycles}
'''
        return  
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumSaturatedRings(smiles: str):
    """
    This tool calculates the number of saturated rings in a molecule. Saturated rings are ring structures composed entirely of single bonds (no double bonds).
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the count of such saturated rings, or an error message.
    """
    try:
        cleaned_smiles = smiles.replace(' ', '').replace('\n', '')
        mol = Chem.MolFromSmiles(cleaned_smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of saturated rings
        num_saturated_rings = rdMolDescriptors.CalcNumSaturatedRings(mol)
        markdown = f'''##The number of saturated rings
**Input SMILES:** {cleaned_smiles}
**Number of saturated rings:** {num_saturated_rings}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumSpiroAtoms(smiles: str):
    """
    This function calculates the number of spiro atoms in a molecule. Spiro atoms are atoms that are part of a spiro ring structure, which consists of two rings that share a single atom.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of spiro atoms, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of spiro atoms
        num_spiro_atoms = rdMolDescriptors.CalcNumSpiroAtoms(mol)
        markdown = f'''##The number of spiro atoms
**Input SMILES:** {smiles}
**Number of spiro atoms:** {num_spiro_atoms}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def calculate_NumUnspecifiedAtomStereoCenters(smiles: str):
    """
    This tool calculates the number of unspecified atomic stereocenters in a molecule. Unspecified atomic stereocenters are atoms that have the potential to be stereocenters but lack explicit specification of their stereochemistry.
    Args:
        smiles: a SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih an integer representing the total number of unspecified atom stereo centers, or an error message.
    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate the number of unspecified atom stereo centers
        num_unspecified_atom_stereo_centers = rdMolDescriptors.CalcNumUnspecifiedAtomStereoCenters(mol)
        markdown = f'''##The number of unspecified atom stereo centers
**Input SMILES:** {smiles}
**Number of unspecified atom stereo centers:** {num_unspecified_atom_stereo_centers}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

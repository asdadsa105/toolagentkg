from rdkit import Chem
import numpy as np
from rdkit.Chem import AllChem, Mol, rdmolops
from rdkit.Chem import rdMolDescriptors, rdfragcatalog
from rdkit.DataStructs import ConvertToNumpyArray
from rdkit.Chem import rdTautomerQuery


#DetermineBondOrders
def determine_bond_orders(smiles):
    """
   The tool is used to determine the bond orders between atoms in a molecule based on their atomic coordinates. It assigns the connectivity information to the molecule by disregarding pre-existing bonds. This function is useful for inferring the chemical bonds in a molecule when the bond information is not already available or needs to be updated based on the 3D structure of the molecule.

    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the results.
    """
    try:
    # Create a molecular object
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        # Hydrogen addition
        mol = Chem.AddHs(mol)

        AllChem.EmbedMolecule(mol, randomSeed=42)

        # Determine key level
        Chem.rdDetermineBonds.DetermineBondOrders(mol)
        markdown = f'''
### Determine Bond Orders
**Input SMILES:** {smiles}

**Result**
**Number of atoms:** {mol.GetNumAtoms()}
**Number of bonds:** {mol.GetNumBonds()}
**Molecular formula:** {rdMolDescriptors.CalcMolFormula(mol)}
**Molecular weight:** {rdMolDescriptors.CalcExactMolWt(mol)}
**SMILES:**{Chem.MolToSmiles(mol)}
**InChI:** {Chem.MolToInchi(mol)}
**InChIKey**{Chem.MolToInchiKey(mol)}

'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#DetermineBonds
def determine_bonds(smiles):
    """
    The tool is used to determine the bond orders between atoms in a molecule based on their atomic coordinates. It assigns the connectivity information to the molecule by disregarding pre-existing bonds. This function is useful for inferring the chemical bonds in a molecule when the bond information is not already available or needs to be updated based on the 3D structure of the molecule.

    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the results.

    """
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        Chem.rdDetermineBonds.DetermineBonds(mol)
        markdown = f'''
        
### Determine Bonds
**Input SMILES:** {smiles}

**Result**
**Number of atoms:** {mol.GetNumAtoms()}
**Number of bonds:** {mol.GetNumBonds()}
**Molecular formula:** {rdMolDescriptors.CalcMolFormula(mol)}
**Molecular weight:** {rdMolDescriptors.CalcExactMolWt(mol)}
**SMILES:**{Chem.MolToSmiles(mol)}
**InChI:** {Chem.MolToInchi(mol)}
**InChIKey**{Chem.MolToInchiKey(mol)}

'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#GetPatternFingerprint
def get_pattern_fingerprint(smiles):
    '''
    This tool is used to generate a pattern fingerprint for a molecule. The pattern fingerprint is a bit vector that encodes the presence or absence of particular substructures in the molecule. The substructures are defined by SMARTS patterns. The SMARTS patterns are converted to molecular fingerprints and then combined to generate the pattern fingerprint.

    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the fingerprint results， or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "").replace(".","")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        result = rdTautomerQuery.PatternFingerprintTautomerTarget(mol)

        markdown = f'''
## Pattern Fingerprint Result

**NumBits:** {result.GetNumBits()}
**NumOnBits:** {result.GetNumOnBits()}
**BitVector:** {result.ToBitString()}
**Binary:** {result.ToBinary()}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


#IsSubstructOf
def is_substructof(target_template):
    '''
    This tool is used to check if a molecule(target) is a substructure of another molecule(template). It returns true if the molecule is a substructure of the other molecule and false otherwise. The substructure search is performed by matching the SMARTS pattern of the query molecule to the target molecule.

    Args:
        target_template (str): Two SMILES strings separated by a '.'. The first SMILES string is the target molecule, and the second SMILES string is the template molecule.
                                Input SMILES directly without any other characters like CR(C)C(=O)O.CC(=O)O.

    Returns:
        str: A markdown string wtih the results, or an error message.
    '''

    try:
        target_template = target_template.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        target_smiles, template_smiles = target_template.split(".")
        template_mol = Chem.MolFromSmiles(template_smiles)
        target_mol = Chem.MolFromSmiles(target_smiles)

        if target_mol is None:
            raise ValueError("Invalid SMILES string.")

        tautomer_query = rdTautomerQuery.TautomerQuery(template_mol)
        result = tautomer_query.IsSubstructOf(target_mol)

        markdown = f'''
## Is Substruct Of Result？

**Target SMILES:** {target_smiles}
**Template SMILES:** {template_smiles}
**Result:** {result}
    '''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


#GetTemplateMolecule
def get_template_molecule(smiles):
    '''
    This tool is used to get the template molecule from a TautomerQuery object.

    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.

    Returns:
        str: A markdown string wtih the template smiles, or an error message.
    '''
    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        template_mol = Chem.MolFromSmiles(smiles)
        if template_mol is None:
            raise ValueError("Invalid SMILES string.")

        tautomer_query = rdTautomerQuery.TautomerQuery(template_mol)

        template_mol = tautomer_query.GetTemplateMolecule()

        template_smiles = Chem.MolToSmiles(template_mol)

        markdown = f'''
## Get Template Molecule
**Input SMILES:** {smiles}

**Template molecule SMILES:**{template_smiles}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

#GetTautomers
def get_tautomers(template_smiles):
    '''
    This tool obtains all possible tautomers of a TautomerQuery object. Tautomers are molecules that have the same atomic composition but differ in the connectivity of atoms. Retrieving all possible tautomers can help in understanding and analyzing changes in chemical reactions and molecular conformations.

    Args:
        template_smiles (str): A SMILES string. Input SMILES directly without any other characters.

    Returns:
        str: A markdown string wtih the number of tautomers and tautomer SMILES, or an error message.

    '''
    try:
        template_smiles = template_smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        template_mol = Chem.MolFromSmiles(template_smiles)
        if template_mol is None:
            raise ValueError("Invalid SMILES string.")

        tautomer_query = rdTautomerQuery.TautomerQuery(template_mol)
        tautomers = tautomer_query.GetTautomers
        markdown = f'''
## Get Tautomers
**Input SMILES:** {template_smiles}

**Number of tautomers:** {len(tautomers)}
'''

        for tautomer in tautomers:
            tautomer_smiles = Chem.MolToSmiles(tautomer)
            markdown += "**Tautomer SMILES:**"+tautomer_smiles

        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


#GetModifiedAtoms
def get_modified_atoms(template_smiles):
    '''
    This tool is used to get the modified atoms of a TautomerQuery object. Modified atoms are atoms that have changed their connectivity in the tautomerization process.

    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.

    Returns:
        str: A markdown string wtih the modified atoms, or an error message.
    '''

    try:
        template_smiles = template_smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        template_mol = Chem.MolFromSmiles(template_smiles)
        if template_mol is None:
            raise ValueError("Invalid SMILES string.")

        tautomer_query = rdTautomerQuery.TautomerQuery(template_mol)
        modified_atoms = tautomer_query.GetModifiedAtoms()
        markdown = f'''## Get Modified Atoms
**Input SMILES:** {template_smiles}
    
**Modified atoms:** '''
        for atom in modified_atoms:
            markdown += str(atom)+"\t"

        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



#GetModifiedBonds
def get_modified_bonds(smiles):
    '''
    This tool is used to get the modified bonds of a TautomerQuery object. Modified bonds are bonds that have changed their connectivity in the tautomerization process.
    Args:
        smiles (str): A SMILES string. Input SMILES directly without any other characters.
    Returns:
        str: A markdown string wtih the modified bonds, or an error message.
    '''

    try:
        smiles = smiles.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        tautomer_query = Chem.rdTautomerQuery.TautomerQuery(mol)
        modified_bonds = tautomer_query.GetModifiedBonds()

        markdown = f'''
## Get Modified Bonds
**Input SMILES:** {smiles}

**Modified bonds:** '''
        for bond_index in modified_bonds:
            markdown += str(bond_index)+", "

        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown



#GetSubstructMatches
def get_substruct_matches(smiles_pair):
    '''
        This tool is to search for substructures in a given target molecule that match the tautomer query.
    Args:
       smiles_pair (str): Two SMILES strings separated by a '.'. The first SMILES string is the target molecule, and the second SMILES string is the template molecule.
    Returns:
        str: A markdown string wtih the substruct matches, or an error message.
    '''
    try:
        smiles_pair = smiles_pair.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        smiles, target_smiles = smiles_pair.split(".")
        mol = Chem.MolFromSmiles(smiles)
        tautomer_query = rdTautomerQuery.TautomerQuery(mol)
        target = Chem.MolFromSmiles(target_smiles)  

        matches = tautomer_query.GetSubstructMatches(target)

        markdown = f'''
    ## Get Substruct Matches
    **Input SMILES:** {smiles}
    **Target SMILES:** {target_smiles}
    
    ## Result
    **Matches:** '''

        for match in matches:
            markdown += str(match)

        markdown += f'''\nIf it is empty, it means there are no matches.'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


# 可靠性middle
def assignOxidationNumbers(smiles: str):
    """
    Adds the oxidation number/state to the atoms of a molecule as property OxidationNumber on each atom.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string wtih smiles of molecular, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Calculate oxidation numbers
        rdMolDescriptors.CalcOxidationNumbers(mol)
        oxidation_numbers = rdMolDescriptors.CalcOxidationNumbers(mol)

        markdown = f'''##Calculate Oxidation Numbers
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

assignOxidationNumbers('O')

def calculate_PBF(smiles: str):
    """
    This tool calculates the PBF (plane of best fit) descriptor for a given molecule. PBF is a molecular descriptor that characterizes the flatness or planarity of a molecule. It is calculated based on the arrangement of atoms in 3D space.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the PBF of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        pbf = rdMolDescriptors.CalcPBF(mol)
        markdown = f'''##Calculate Partial Bond Order
**Input SMILES:** {smiles}
**PBF:** {pbf}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_PMI1(smiles: str):
    """
    This tool calculates the first principal moment of inertia (PMI1) for a given molecule. PMI1 is a molecular descriptor used to characterize the shape and spatial distribution of atoms in a molecule. PMI1 measures the asymmetry or elongation of a molecule along its principal axis. It provides information about the molecule's overall shape and can be useful in various computational chemistry and drug design applications.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the PMI1 of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        pmi1 = rdMolDescriptors.CalcPMI1(mol)
        markdown = f'''##Calculate PMI1
**Input SMILES:** {smiles}
**First principal moment of inertia (PMI1):** {pmi1}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_PMI2(smiles: str):
    """
    This tool is designed to compute the PMI2 (Partial Molecular Information 2) value of a molecule, which serves as a descriptor indicating the shape and structure of the molecule.    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the PMI2 of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        pmi2 = rdMolDescriptors.CalcPMI2(mol)
        markdown = f'''##Calculate PMI2
**Input SMILES:** {smiles}
**PMI2:** {pmi2}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_PMI3(smiles: str):
    """
    This tool is designed to compute the PMI3 (Partial Molecular Information 3) value of a molecule, which serves as a descriptor characterizing the shape and structure of the molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the PMI3 of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        pmi3 = rdMolDescriptors.CalcPMI3(mol)
        markdown = f'''##Calculate PMI3
**Input SMILES:** {smiles}
**PMI3:** {pmi3}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_Phi(smiles: str):
    """
    This tool calculates the Phi (φ) angle of a molecule, which is a torsional angle describing the rotation about a single bond.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the Phi angle of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        phi = rdMolDescriptors.CalcPhi(mol)
        markdown = f'''##Calculate Phi angle
**Input SMILES:** {smiles}
**Phi angle:** {phi}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_RDF(smiles: str):
    """
    This tool calculates the RDF (Radial Distribution Function) descriptor for a given molecule. RDF is a molecular descriptor that characterizes the distribution of atoms in 3D space. It is calculated based on the distances between pairs of atoms in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the RDF of the molecule(a list), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        rdf = rdMolDescriptors.CalcRDF(mol)
        markdown = f'''##Calculate RDF
**Input SMILES:** {smiles}
**RDF:** {rdf}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_RadiusOfGyration(smiles: str):
    """
    This tool is designed to compute the radius of gyration for a given molecule, providing insights into its overall shape and compactness.    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the computed radius of gyration for the specified molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        rg = rdMolDescriptors.CalcRadiusOfGyration(mol)
        markdown = f'''##Calculate Radius of Gyration
**Input SMILES:** {smiles}
**Radius of Gyration (Rg):** {rg}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_SpherocityIndex(smiles: str):
    """

This function calculates the sphericity index for a given molecule. Sphericity index is a measure of how close the shape of a molecule resembles a perfect sphere.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the spherocity index of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        sp = rdMolDescriptors.CalcSpherocityIndex(mol)
        markdown = f'''##Calculate Spherocity Index
**Input SMILES:** {smiles}
**Spherocity Index:** {sp}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_TPSA(smiles: str):
    """
    This tool calculates the TPSA (Topological Polar Surface Area) descriptor for a given molecule, which is a measure of the accessible polar surface area in a molecule. TPSA is a molecular descriptor that characterizes the polarity and hydrophilicity of a molecule. It is calculated based on the distribution of polar atoms and bonds in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the TPSA of the molecule(a float value), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        tpsa = rdMolDescriptors.CalcTPSA(mol)
        markdown = f'''##Calculate TPSA
**Input SMILES:** {smiles}
**TPSA:** {tpsa}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def calculate_WHIM(smiles: str):
    """
    This tool calculates the WHIM (Weighted Holistic Invariant Molecular) descriptor for a given molecule. WHIM is a molecular descriptor that characterizes the 3D shape and electronic properties of a molecule. It is calculated based on the distribution of atomic properties and their spatial arrangement in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the WHIM of the molecule(a list of float values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        whim = rdMolDescriptors.CalcWHIM(mol)
        markdown = f'''##Calculate WHIM
**Input SMILES:** {smiles}
**WHIM:** {whim}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def customprop_vsa(smiles: str):
    """
    This function computes a custom property for a given molecule using the Van der Waals Surface Area (VSA) method, based on user-defined parameters.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the VSA of the molecule(a list of float values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        # Calculate partial bond order
        vsa = rdMolDescriptors.CalcLabuteASA(mol)
        markdown = f'''##Calculate custom property using VSA method
**Input SMILES:** {smiles}
**Custom property using VSA:** {vsa}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_atom_features(smiles: str):
    """
    This function computes a set of atom features for a given molecule, including atomic number, valence, and hybridization.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the atom features of the molecule(a list of dictionaries), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        num_atoms = mol.GetNumAtoms()
        markdown = f'''##Get Atom Features
**Input SMILES:** {smiles}
**Atom Features:** 
'''
        for i in range(num_atoms):
            markdown += f'Atom{i} ' + str(rdMolDescriptors.GetAtomFeatures(mol, i)) + '\n'
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_AtomPairFingerprint(smiles: str):
    """
    This function computes the atom pair for a given molecule. The atom pair fingerprint is a molecular descriptor that characterizes the presence of pairs of atoms in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the atom pair fingerprint of the molecule(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        fingerprint = rdMolDescriptors.GetAtomPairFingerprint(mol)
        numpy_array = np.zeros((1,))
        ConvertToNumpyArray(fingerprint, numpy_array)
        markdown = f'''##Get Atom Pair Fingerprint
**Input SMILES:** {smiles}
**Atom Pair Fingerprint:** {numpy_array}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_ConnectivityInvariants(smiles: str):
    """
    This tool computes connectivity invariants, similar to ECFP (Extended Connectivity Fingerprints), for a given molecule. These invariants serve as a fingerprint representation of the molecule's structural connectivity, aiding in tasks such as similarity comparison and molecular structure representation.    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the connectivity invariants of the molecule(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('.', '')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        invariants = rdMolDescriptors.GetConnectivityInvariants(mol)
        markdown = f'''##Get Connectivity Invariants
**Input SMILES:** {smiles}
**Connectivity Invariants:** {invariants}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_FeatureInvariants(smiles: str):
    """
    This tool computes feature invariants, similar to FCFP (Feature Centroid Fingerprints), for a given molecule. These invariants provide a fingerprint representation of the molecule's features, aiding in tasks such as similarity comparison and molecular structure analysis.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the feature invariants of the molecule(a list of int), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        invariants = rdMolDescriptors.GetFeatureInvariants(mol)
        markdown = f'''##Get Feature Invariants
**Input SMILES:** {smiles}
**Feature Invariants:** {invariants}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown




def get_AtomPairCode(smiles: str):
    """
    This function computes atom pair code (hash) for each atom in a molecular. The atom pair code is a molecular descriptor that characterizes the presence of pairs of atoms in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the atom pair code (hash) for each atom(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        atom_num = Mol.GetNumAtoms(mol)
        markdown = f'''##Get Atom Pair Code
**Input SMILES:** {smiles}
**atom pair code (hash) for each atom:**
'''

        for i in range(atom_num):
            atom = mol.GetAtomWithIdx(i)
            result = rdMolDescriptors.GetAtomPairAtomCode(atom)
            markdown += str(i) + '\t' + str(atom.GetSymbol()) + '\t' + str(result) + '\n'
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_Hybridization(smiles: str):
    """
    This function computes the hybridization of each atom in a molecule. Hybridization is a property of an atom that characterizes its electron configuration and bonding behavior.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the hybridization of each atom(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        markdown = f'''##Get Hybridization
**Input SMILES:** {smiles}
**Hybridization of each atom:**
'''
        for x in mol.GetAtoms():
            markdown += f'Atom{x.GetIdx()} ' + str(x.GetHybridization()) + '\n'
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_ring_systems(smiles: str):
    """
    This function computes the ring systems of a molecule. A ring system is a set of rings that are connected to each other through shared atoms or bonds.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the ring systems of the molecule(a list of lists), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        markdown = f'''##Get Ring Systems
**Input SMILES:** {smiles}
**Ring Systems:**
'''
        ri = mol.GetRingInfo()
        systems = []
        includeSpiro = False
        for ring in ri.AtomRings():
            ringAts = set(ring)
            nSystems = []
            for system in systems:
                nInCommon = len(ringAts.intersection(system))
                if nInCommon and (includeSpiro or nInCommon > 1):
                    ringAts = ringAts.union(system)
                else:
                    nSystems.append(system)
            nSystems.append(ringAts)
            systems = nSystems
        markdown += str(systems)
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


# GetMACCSKeysFingerprint
def get_MACCSKeysFingerprint(smiles: str):
    """
    This function computes the Molecular ACCess System keys fingerprint for a given molecule. The Molecular ACCess System keys fingerprint is a molecular descriptor that characterizes the presence of specific structural features in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the Molecular ACCess System keys fingerprint of the molecule(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        fingerprint = rdMolDescriptors.GetMACCSKeysFingerprint(mol)
        numpy_array = np.zeros((1,))
        ConvertToNumpyArray(fingerprint, numpy_array)
        markdown = f'''##Get MACCS Keys Fingerprint\
{numpy_array}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_MorganFingerprint(smiles: str):
    """
    This tool computes the Morgan fingerprint for a given molecule. The Morgan fingerprint is a widely used method to encode molecular structure information. It captures the local chemical environments around each atom up to a specified radius.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the Morgan fingerprint of the molecule(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        fingerprint = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2)
        numpy_array = np.zeros((1,))
        ConvertToNumpyArray(fingerprint, numpy_array)
        markdown = f'''##Get Morgan Fingerprint
**Input SMILES:** {smiles}
**Morgan Fingerprint:** {numpy_array}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_TopologicalTorsionFingerprint(smiles: str):
    """
    This tool computes the topological torsion fingerprint for a given molecule. The topological torsion fingerprint is a molecular descriptor that characterizes the presence of specific structural features in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the topological torsion fingerprint of the molecule(a list of int values), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        fingerprint = rdMolDescriptors.GetTopologicalTorsionFingerprint(mol)
        numpy_array = np.zeros((1,))
        ConvertToNumpyArray(fingerprint, numpy_array)
        markdown = f'''##Get Topological Torsion Fingerprint
**Input SMILES:** {smiles}
**Topological Torsion Fingerprint:** {numpy_array}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_USR(smiles: str):
    """
    The tool computes the USR (Ultrafast Shape Recognition) descriptor for a given conformer of a molecule and returns it as a list.The USR descriptor is a numerical representation of the shape of a molecule. It captures the 3D shape of a molecule in a compact form, making it particularly useful for comparing molecular shapes efficiently.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the USR descriptor of the molecule(a list), or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        usr = rdMolDescriptors.GetUSR(mol)
        markdown = f'''##Get USR
**Input SMILES:** {smiles}
**USR:** {usr}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_USRCAT(smiles: str):
    """
    This function is designed to compute the USRCAT (Ultrafast Shape Recognition with Coordinate Asymmetric Torsions) descriptor for a specified conformer of a molecule. The USRCAT descriptor is a compact representation of the molecular shape, which is useful for various cheminformatics applications such as similarity searching, clustering, and virtual screening.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the USRCAT descriptor of the molecule(a list), or an error message.
    """

    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        usrcat = rdMolDescriptors.GetUSRCAT(mol)
        markdown = f'''##Get USRCAT
**Input SMILES:** {smiles}
**USRCAT:** {usrcat}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def add_hydrogens(smiles: str):
    """
    This function is used to add hydrogen atoms to the molecular graph of a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the molecule with added hydrogens, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol1 = Chem.AddHs(mol)

        markdown = f'''##Add Hydrogens
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol1)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def add_wavabonds_for_stereoany(smiles: str):
    """
   This tool adds wavy bonds around double bonds with STEREOANY stereochemistry.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the molecule with added wava bonds, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        rdmolops.AddWavyBondsForStereoAny(mol)

        markdown = f'''##Add Wava Bonds
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def assign_AtomChiralTags_FromMolParity(smiles: str):
    """
    This tool sets chiral tags for atoms of the molecular based on the molParity property. This ensures proper definition of the molecule's stereochemistry for further analysis or visualization.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.AssignAtomChiralTagsFromStructure(mol)

        markdown = f'''##Assign Atom Chiral Tags From Mol Parity
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def assign_radicals(smiles: str):
    """
    This tool is used to assign radical counts to atoms within a molecule. It takes a molecule SMILES as input and modifies it, assigning appropriate numbers of radicals to each atom within the molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.AssignRadicals(mol)

        markdown = f'''##Assign Radicals
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def assign_stereochemistry(smiles: str):
    """
    This tool is used for assigning Cahn–Ingold–Prelog (CIP) stereochemistry to atoms (R/S) and double bonds (Z/E) within a molecule. Chiral atoms will have a property _CIPCode indicating their chiral code.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.rdmolops.AssignStereochemistry(mol)
        markdown = f'''##Assign Stereochemistry
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_adjacency_matrix(smiles: str):
    """
    This tool is used to obtain the adjacency matrix of a molecule. The adjacency matrix is a mathematical representation of a molecule where rows and columns correspond to atoms, and matrix elements represent whether pairs of atoms are adjacent (connected by a bond) or not.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the adjacency matrix of the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        adj_matrix = rdmolops.GetAdjacencyMatrix(mol)
        markdown = f'''##Get Adjacency Matrix
**Input SMILES:** {smiles}
**Adjacency Matrix:** 
{adj_matrix}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def get_AllowNontetrahedralChirality(smiles: str):
    """
    This tool is used to determine whether recognition of non-tetrahedral chirality from 3D structures is enabled or not.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string indicating whether recognition of non-tetrahedral chirality from 3D structures is enabled, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        is_enabled = rdmolops.GetAllowNontetrahedralChirality()
        markdown = f'''##whether or not recognition of non-tetrahedral chirality from 3D structures is enabled?
**Input SMILES:** {smiles}
**Result:**{is_enabled}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def get_DistanceMatrix(smiles: str):
    """
    The tool computes the topological distance matrix for a given molecule. This matrix provides information about the shortest path between pairs of atoms in the molecular graph, essentially indicating how many bonds need to be traversed to move from one atom to another.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the distance matrix of the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        dist_matrix = rdmolops.GetDistanceMatrix(mol)
        markdown = f'''##Get Distance Matrix
**Input SMILES:** {smiles}
**Distance Matrix:**
{dist_matrix}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_formal_charge(smiles: str):
    """
    This tool is utilized to determine the total formal charge of a given molecule. Formal charge is a concept in chemistry that describes the net charge of an atom or a molecule, considering the redistribution of electrons based on electronegativity differences.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the formal charge of the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        formal_charge = rdmolops.GetFormalCharge(mol)
        markdown = f'''##Get Formal Charge
**Input SMILES:** {smiles}
**Formal Charge:**{formal_charge}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def get_formal_charge_of_atoms(smiles: str):
    """
    This tool is utilized to determine the formal charge of each atom in a given molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the formal charge of each atom in the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        markdown = f'''##Get Formal Charge
**Input SMILES:** {smiles}
**Formal Charge of each atom:**
'''
        for atom in mol.GetAtoms():
            markdown += f'Atom{atom.GetIdx()}  ' + f'{atom.GetSymbol()}  ' + str(atom.GetFormalCharge()) + '\n'
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_molfrags(smiles: str):
    """
    This tool identifies disconnected fragments within a molecule and returns them as atom identifiers or molecules. It allows for flexible representation and manipulation of the fragments in further analysis.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with a tuple containing the atom identifiers or molecules for each disconnected fragment within the molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        frags = rdmolops.GetMolFrags(mol)
        markdown = f'''##Get Mol Frags
**Input SMILES:** {smiles}
**Mol Frags:**{frags}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def get_UseLegacyStereoPerception(smiles: str):
    """
    This tool is used to determine whether the legacy stereo perception code is being used. The legacy stereo perception code is an older implementation of stereochemistry perception in RDKit, which may be used for compatibility with older versions of the software.
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string indicating whether legacy stereo perception code is being used, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        is_enabled = rdmolops.GetUseLegacyStereoPerception()
        markdown = f'''##whether or not legacy stereo perception is enabled?
**Input SMILES:** {smiles}
**Result:**{is_enabled}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def hapticbonds_to_dative(smiles: str):
    """
    This tool is used to convert a molecule that represents haptic bonds using a dummy atom with a dative bond to a metal atom into a molecule with explicit dative bonds from the atoms of the haptic group to the metal atom.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        rdmolops.HapticBondsToDative(mol)
        markdown = f'''##Haptic Bonds To Dative
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def has_query_hs(smiles: str):
    """
    This tool is used to check if a molecule contains query H (hydrogen) atoms. Query hydrogens are special types of hydrogen atoms that are used to represent specific chemical environments or constraints in a molecule.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string indicating whether the molecule contains query hydrogens, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        has_query_hs, has_unmergable_query_hs = Chem.rdmolops.HasQueryHs(mol)
        markdown = f'''##whether or not the molecule contains query hydrogens?
**Input SMILES:** {smiles}
**Result**
**Has Query Hs:** {has_query_hs}
**Has Unmergable Query Hs:** {has_unmergable_query_hs}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def kekulize(smiles: str):
    """
    This tool is used to perform Kekulization on a molecule. Kekulization is the process of converting aromatic bonds in a molecule to alternating single and double bonds, following the Kekulé structure representation.
     Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the kekulized molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.Kekulize(mol)
        markdown = f'''##Kekulize
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def merge_queryhs(smiles: str):
    """
    This tool is used to merge hydrogen atoms into their neighboring atoms as query atoms. This function is typically used to modify molecules by replacing explicit hydrogen atoms with query atoms, allowing for more flexible substructure searching or atom mapping.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.rdmolops.MergeQueryHs(mol)
        markdown = f'''##Merge Query Hs
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def murcko_decompose(smiles: str):
    """
    This tool is used to perform a Murcko decomposition on a molecule and return the scaffold. The Murcko scaffold represents the core structure of a molecule by removing side chains and retaining the ring system.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the core scaffold, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        core_scaffold = rdmolops.MurckoDecompose(mol)
        markdown = f'''##Murcko Decompose
**Input SMILES:** {smiles}
**Core Scaffold:** {Chem.MolToSmiles(core_scaffold)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def remove_hydrogens(smiles: str):
    """
    This tool is used to remove hydrogen atoms from a molecule's graph. This function is typically used to simplify molecular representations for further analysis or visualization.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        mol = Chem.RemoveHs(mol)
        markdown = f'''##Remove Hydrogens
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def remove_stereo_chemistry(smiles: str):
    """
    This tool is used to remove all stereochemistry information from a molecule. Stereochemistry information in a molecule refers to the spatial arrangement of atoms or groups around a stereocenter or a double bond.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.RemoveStereochemistry(mol)
        markdown = f'''##Remove Stereo Chemistry
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown

def set_aromaticity(smiles: str):
    """
    This tool is used to perform aromaticity perception on a molecule, which means determining the aromaticity of atoms and bonds in the molecule. Aromaticity is a chemical property that describes the stability and reactivity of certain ring structures in organic molecules.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.SetAromaticity(mol)
        markdown = f'''##Set Aromaticity
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


def set_bondstereo_from_directions(smiles: str):
    """
    This tool is used to set the cis/trans stereochemistry on double bonds based on the directions of neighboring bonds.
    Args:
        smiles: a SMILES string. Please Input SMILES directly without any other characters。
    Returns:
        str: A markdown string with the SMILES of the modified molecule, or an error message.
    """
    try:
        smiles = smiles.replace(' ', '').replace('\n', '').replace('\'', '').replace('\"', '').replace('.','')
        if 'smiles=' in smiles:
            name, smiles = smiles.split('=')
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        Chem.SetBondStereoFromDirections(mol)
        markdown = f'''##Set Bond Stereo From Directions
**Input SMILES:** {smiles}
**Output SMILES:** {Chem.MolToSmiles(mol)}
'''
        return markdown
    except Exception as e:
        markdown = f"An error occurred: {e}"
        return markdown


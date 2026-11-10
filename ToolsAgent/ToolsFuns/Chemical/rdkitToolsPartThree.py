import base64
import glob
import os
import pickle
import numpy as np
import pandas as pd
import rdkit
from rdkit import Chem
from rdkit.Chem.AtomPairs.Pairs import pyScorePair, ExplainPairScore, GetAtomPairFingerprintAsBitVect
from rdkit.Chem.AtomPairs.Sheridan import AssignPattyTypes
from rdkit.Chem.AtomPairs.Utils import ExplainAtomCode, GetAtomCode
from rdkit.Chem.ChemUtils.BulkTester import TestMolecule
from rdkit.Chem.ChemUtils import SDFToCSV
from rdkit.Chem.Draw.IPythonConsole import ShowMols
from rdkit.Chem import Draw, rdMolDescriptors, AllChem, DataStructs, rdMolDescriptors
from rdkit.Chem.EState.AtomTypes import TypeAtoms
from rdkit.Chem.EState import EStateIndices,EState_VSA,Fingerprinter
from rdkit.rdBase import rdkitVersion
from rdkit.Chem.Fingerprints import FingerprintMols, MolSimilarity
from rdkit.ML.Cluster import Murtagh
from rdkit.Chem.Fingerprints.ClusterMols import GetDistanceMatrix, ClusterPoints, ClusterFromDetails
from rdkit.Chem.Fingerprints.FingerprintMols import FingerprintMol, FingerprintsFromMols, FoldFingerprintToTargetDensity, GetRDKFingerprint
from rdkit.DataStructs.cDataStructs import ExplicitBitVect
from rdkit.Chem.Fraggle.FraggleSim import GetFraggleSimilarity, generate_fraggle_fragmentation, isValidRingCut
from rdkit.Chem.AtomPairs import Pairs, Torsions
from rdkit.Chem.MolDb.FingerprintUtils import BuildSigFactory, BuildPharm2DFP, BuildMorganFP, BuildRDKitFP, BuildAvalonFP
from rdkit.Chem import ChemicalFeatures
from rdkit.Chem.Pharm2D import SigFactory, Generate
from rdkit.Chem.inchi import MolToInchi
from rdkit.Chem.MolKey import MolKey
from rdkit.Avalon.pyAvalonTools import Generate2DCoords
# from tools.utils import param_decorator, timer_decorator
from ..utils.common import param_decorator

@param_decorator
def explain_atom_pair_score(smiles, atom_idx1, atom_idx2):
    """
    Explain the pair score for a directly connected atom pair in a molecule.

    Args:
        molecule (str): SMILES representation of the molecule.
        atom_idx1 (int): Index of the first atom.
        atom_idx2 (int): Index of the second atom.

    Returns:
        str: A Markdown string explaining the pair score, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str) or not isinstance(atom_idx1, int) or not isinstance(atom_idx2, int):
            raise ValueError("Invalid input types for molecule or atom indices.")

        # 将SMILES字符串转换为分子对象
        m = Chem.MolFromSmiles(smiles)
        if m is None:
            raise ValueError("Invalid SMILES string.")

        # 检查原子索引是否在分子范围内
        if atom_idx1 >= m.GetNumAtoms() or atom_idx2 >= m.GetNumAtoms() or atom_idx1 < 0 or atom_idx2 < 0:
            raise IndexError("Atom index out of range.")

        atom1 = m.GetAtomWithIdx(atom_idx1)
        atom2 = m.GetAtomWithIdx(atom_idx2)

        # 计算原子对的分数
        score = pyScorePair(atom1, atom2, dist=1)

        # 解释分数
        explanation = ExplainPairScore(score)

        # 生成Markdown格式的字符串
        markdown_output = f"""
### Pair Score Explanation

**Molecule:** `{smiles}`

**Atom Indices:** {atom_idx1} and {atom_idx2}

**Score:** {score}

**Explanation:**
- **First Atom:** `{explanation[0]}`
- **Second Atom:** `{explanation[2]}`
- **Distance:** `{explanation[1]}` (This is typically the bond distance in the molecule)
"""
    except Exception as e:
        # 发生异常时返回错误消息
        markdown_output = f"An error occurred: {e}"

    return markdown_output

# 输出中的数字：每个数字代表在位向量中被设置为 1 的位置。
# 这些位置对应于分子中特定的原子对配置。换句话说，这些数字是用于唯一标识分子中原子对的编码。
# 例如，数字 541732 表示分子中的一个特定原子对，其特定的空间排列和化学性质使得这个位置在位向量中被设置为 1。
def get_atom_pair_fingerprint_as_bit_vect(smiles):
    """
    Generate the atom pair fingerprint of a molecule as a SparseBitVect. 
    This fingerprint represents the presence of atom pairs, not just their counts.

    Args:
        molecule (str): SMILES representation of the molecule.

    Returns:
        str: Markdown formatted string of the bit vector fingerprint, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Molecule must be a string.")

        # 将SMILES字符串转换为分子对象
        m = Chem.MolFromSmiles(smiles)
        if m is None:
            raise ValueError("Invalid SMILES string.")

        # 计算原子对指纹作为SparseBitVect
        fp = GetAtomPairFingerprintAsBitVect(m)
        on_bits = list(fp.GetOnBits())

        # 生成Markdown格式的字符串
        markdown_output = f"""
### Atom Pair Fingerprint

**Molecule:** `{smiles}`

**Fingerprint (SparseBitVect) On Bits:**
`{on_bits}`
"""
    except Exception as e:
        # 发生异常时返回错误消息
        markdown_output = f"An error occurred: {e}"

    return markdown_output

def assign_patty_types(smiles):
    """
    Assign Patty types to the atoms of a molecule.

    Args:
    molecule (Mol): RDKit molecule object.

    Returns:
        str: Markdown formatted string listing the Patty types of each atom, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Molecule must be a string.")

        # 将SMILES字符串转换为分子对象
        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            raise ValueError("Invalid SMILES string.")
        
        # 计算Patty类型
        types = AssignPattyTypes(molecule)
        
        # 构建Markdown格式的结果字符串
        result = "| Atom Index | Patty Type |\n|------------|------------|\n"
        for index, type in enumerate(types, start=1):
            result += f"| {index} | {type} |\n"
    except Exception as e:
        # 发生异常时返回错误消息
        result = f"An error occurred: {e}"

    return result

# include_chirality 手性信息
@param_decorator
def explain_atom_code(smiles, atom_idx, include_chirality=True):
    """
    Explain the code for a specific atom in a molecule, including chirality by default.

    Args:
        molecule (str): SMILES representation of the molecule.
        atom_idx (int): Index of the atom to explain.
        include_chirality (bool): Whether to include chirality in the explanation. Default is True.

    Returns:
        str: Markdown formatted string explaining the atom code, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str) or not isinstance(atom_idx, int):
            raise ValueError("Invalid input types for molecule or atom index.")

        # 将SMILES字符串转换为分子对象
        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None or atom_idx >= molecule.GetNumAtoms() or atom_idx < 0:
            raise ValueError("Invalid SMILES string or atom index out of range.")

        atom = molecule.GetAtomWithIdx(atom_idx)

        # 获取并解释原子代码
        code = GetAtomCode(atom, includeChirality=include_chirality)
        explanation = ExplainAtomCode(code, includeChirality=include_chirality)

        # 生成Markdown格式的字符串
        markdown_output = f"""
### Atom Code Explanation

**Molecule:** `{smiles}`

**Atom Index:** {atom_idx}

**Atom Code:** `{code}`

**Explanation:**
- **Element:** `{explanation[0]}`
- **Number of Neighbors (after subtracting branchSubtract):** `{explanation[1]}`
- **Number of Pi Electrons:** `{explanation[2]}`
"""
        chirality = explanation[3] if len(explanation) > 3 and explanation[3] else ''
        if chirality:
            markdown_output += f"- **Chirality:** `{chirality}`\n"

    except Exception as e:
        # 发生异常时返回错误消息
        markdown_output = f"An error occurred: {e}"

    return markdown_output

def test_molecule(smiles):
    """
    Perform a series of tests on a molecule, including sanitization, removal of hydrogens,
    and canonicalization check. This function helps in validating the molecule's structure 
    and consistency.

    Args:
        smiles (str): SMILES representation of the molecule.

    Returns:
        str: A string summarizing the test results. Returns 'Valid and consistent molecule structure.'
        if tests are passed, otherwise provides an error code indicating the type of issue encountered.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return "Error: Invalid SMILES string."

        # 对分子进行测试
        result_code = TestMolecule(mol)
        if result_code == 0:
            return "Valid and consistent molecule structure."
        elif result_code == -1:
            return "Error: Molecule failed during sanitization."
        elif result_code == -2:
            return "Error: Exception occurred during processing."
        elif result_code == -3:
            return "Error: Molecule failed during canonicalization check."
        else:
            return f"Error: Unknown issue encountered. Error code: {result_code}"
    except Exception as e:
        # 发生异常时返回错误消息
        return f"Error occurred during molecule testing: {e}"

def convert_sdf_to_csv(sdf_file):
    """
    Convert a single SDF file to a CSV file and provide a download link.

    Args:
        sdf_file (str): Path to the SDF file.

    Returns:
        str: A Markdown string with a link to the converted CSV file, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(sdf_file, str):
            raise ValueError("Input must be a file path.")

        # 检查文件是否存在
        if not os.path.exists(sdf_file):
            raise FileNotFoundError(f"No SDF file found at {sdf_file}")

        server_ip = "10.99.150.19"
        download_folder = "/data/huangjj/Download/"
        csv_filename = os.path.basename(sdf_file).replace('.sdf', '.csv')
        csv_file_path = os.path.join(download_folder, csv_filename)

        # 使用 RDKit 分子供应器读取 SDF 文件
        suppl = Chem.SDMolSupplier(sdf_file)
        if not suppl:
            raise ValueError("Failed to read SDF file.")

        # 打开 CSV 文件以进行写入
        with open(csv_file_path, 'w', newline='') as csv_file:
            SDFToCSV.Convert(suppl, csv_file)

        # 使用服务器IP地址和文件名构建下载链接
        download_link = f"http://{server_ip}/downloads/{csv_filename}"

        markdown_output = f"### Converted CSV File\n\n- [{csv_filename}]({download_link})\n"
    except Exception as e:
        # 发生异常时返回错误消息
        markdown_output = f"An error occurred during conversion: {e}"

    return markdown_output

def show_mol(smiles):
    """
    Generate a molecule image from its SMILES representation and embed it directly in Markdown.

    Args:
        smiles (str): A SMILES representation of the molecule to be displayed.

    Returns:
        str: A Markdown string with embedded molecule image, or an error message.
    """
    useSVG = True
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("SMILES must be a string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        markdown_output = f"### Molecule Information\n\n**SMILES:** `{smiles}`\n\n"

        # 生成分子图像
        if useSVG:
            svg = Draw.MolsToGridImage([mol], useSVG=useSVG, subImgSize=(300, 300)).data
            svg_base64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
            markdown_output += f"![Molecule Image](data:image/svg+xml;base64,{svg_base64})"
        else:
            img = Draw.MolToImage(mol, size=(300, 300))
            temp_img_path = 'temp_img.png'
            img.save(temp_img_path)
            with open(temp_img_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            markdown_output += f"![Molecule Image](data:image/png;base64,{img_base64})"
            os.remove(temp_img_path)

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while generating molecule image: {e}"

def type_atoms_in_molecule(smiles):
    """
    Assigns EState types to each atom in a molecule based on its SMILES representation.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the EState types of atoms in the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        # 分配每个原子的EState类型
        atom_types = TypeAtoms(mol)

        # 格式化输出
        markdown_output = f"### EState Atom Types for Molecule: `{smiles}`\n\n"
        for i, types in enumerate(atom_types):
            types_str = ', '.join(types)
            markdown_output += f"- Atom {i + 1}: {types_str}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while typing atoms in molecule: {e}"

def calculate_estate_indices(smiles):
    """
    Calculate EState indices for each atom in a molecule based on its SMILES representation.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the EState indices of atoms in the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        # 计算EState指数
        indices = EStateIndices(mol)

        # 格式化输出
        markdown_output = f"## EState Indices for Molecule: `{smiles}`\n\n"
        for i, index in enumerate(indices):
            markdown_output += f"- Atom {i + 1}: {index:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating EState indices: {e}"

def calculate_estate_vsa(smiles):
    """
    Calculate EState VSA indices for a molecule based on its SMILES representation.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the EState VSA indices of the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        vsa_functions = [
            EState_VSA.EState_VSA1, EState_VSA.EState_VSA2, EState_VSA.EState_VSA3,
            EState_VSA.EState_VSA4, EState_VSA.EState_VSA5, EState_VSA.EState_VSA6,
            EState_VSA.EState_VSA7, EState_VSA.EState_VSA8, EState_VSA.EState_VSA9,
            EState_VSA.EState_VSA10, EState_VSA.EState_VSA11
        ]

        # 计算EState VSA指数
        vsa_indices = [func(mol) for func in vsa_functions]

        # 格式化输出
        markdown_output = f"### EState VSA Indices for Molecule: `{smiles}`\n\n"
        for i, index in enumerate(vsa_indices):
            markdown_output += f"- VSA Index {i + 1}: {index:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating EState VSA indices: {e}"

def generate_estate_fingerprint(smiles):
    """
    Generate the EState fingerprint for a molecule based on its SMILES representation.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the EState fingerprint of the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        # 生成 EState 指纹
        counts, sums = Fingerprinter.FingerprintMol(mol)

        # 获取非零计数的索引
        nonzero_indices = np.nonzero(counts)[0]

        # 格式化输出
        markdown_output = f"### EState Fingerprint for Molecule: `{smiles}`\n\n"
        markdown_output += "**Counts of Atom Types:**\n"
        for idx in nonzero_indices:
            markdown_output += f"- Atom Type {idx + 1}: Count = {counts[idx]}\n"

        markdown_output += "\n**Sum of EState Indices for Atom Types:**\n"
        for idx in nonzero_indices:
            markdown_output += f"- Atom Type {idx + 1}: EState Index Sum = {sums[idx]:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while generating EState fingerprint: {e}"

def extract_rotatable_dihedrals_from_sdf(sdffile):
    """
    Extract rotatable dihedrals from a molecule in an SDF file.

    Args:
        sdffile (str): The file path of the SDF file containing the molecule.

    Returns:
        str: A Markdown formatted string listing the indices of atoms forming each 
             rotatable dihedral in the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(sdffile, str):
            raise ValueError("Input must be a file path.")

        # 读取SDF文件
        mols_suppl = Chem.SDMolSupplier(sdffile)
        if not mols_suppl or len(mols_suppl) == 0:
            raise ValueError("No molecules found in the SDF file.")

        mol = mols_suppl[0]  # 取第一个分子
        if mol is None:
            raise ValueError("Invalid molecule in the SDF file.")

        def getdihes(mol):
            dihes = []
            for bond in mol.GetBonds():
                if bond.GetBondType().name == 'SINGLE' and not bond.IsInRing():
                    atom2id = bond.GetBeginAtomIdx()
                    atom3id = bond.GetEndAtomIdx()
                    atom2 = bond.GetBeginAtom()
                    atom3 = bond.GetEndAtom()

                    if len(atom3.GetNeighbors()) == 1 or len(atom2.GetNeighbors()) == 1:
                        continue
                    else:
                        atom1s = [at.GetIdx() for at in atom2.GetNeighbors() if at.GetIdx() != atom3id]
                        atom4s = [at.GetIdx() for at in atom3.GetNeighbors() if at.GetIdx() != atom2id]

                        if atom1s and atom4s:
                            dihes.append([atom1s[0], atom2id, atom3id, atom4s[0]])
            return dihes

        dihedrals = getdihes(mol)
        
        markdown_output = "### Rotatable Dihedrals in Molecule\n\n"
        markdown_output += "Extracted from file: `{}`\n\n".format(sdffile)
        for i, dihedral in enumerate(dihedrals):
            markdown_output += f"- Dihedral {i+1}: Atoms {dihedral[0]}, {dihedral[1]}, {dihedral[2]}, {dihedral[3]}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while extracting rotatable dihedrals: {e}"

def calculate_molecular_center(sdffile):
    """
    Calculate the geometric center of a molecule from an SDF file.

    Args:
        sdffile (str): The file path of the SDF file containing the molecule.

    Returns:
        str: A Markdown formatted string describing the x, y, and z coordinates 
             of the molecular center, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(sdffile, str):
            raise ValueError("Input must be a file path.")

        # 读取SDF文件
        mols_suppl = Chem.SDMolSupplier(sdffile)
        if not mols_suppl or len(mols_suppl) == 0:
            raise ValueError("No molecules found in the SDF file.")

        mol = mols_suppl[0]  # 取第一个分子
        if mol is None:
            raise ValueError("Invalid molecule in the SDF file.")

        mol3d = mol.GetConformer()
        num_atoms = mol.GetNumAtoms()
        if num_atoms == 0:
            raise ValueError("Molecule does not have atoms.")

        # 计算几何中心
        x, y, z = 0, 0, 0
        for ind in range(num_atoms):
            pos = mol3d.GetAtomPosition(ind)
            x += pos.x
            y += pos.y
            z += pos.z
        center = [x / num_atoms, y / num_atoms, z / num_atoms]

        markdown_output = "### Molecular Center Coordinates\n\n"
        markdown_output += f"Extracted from file: `{sdffile}`\n\n"
        markdown_output += f"- X-coordinate: {center[0]:.3f}\n"
        markdown_output += f"- Y-coordinate: {center[1]:.3f}\n"
        markdown_output += f"- Z-coordinate: {center[2]:.3f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating molecular center: {e}"

def calculate_fsp3(smiles):
    """
    Calculate the fraction of SP3 hybridized carbons (FSP3) for a given molecule.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the FSP3 value of the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        # 计算 FSP3
        FSP3 = rdMolDescriptors.CalcFractionCSP3(mol)

        markdown_output = f"### FSP3 Descriptor for Molecule: `{smiles}`\n\n"
        markdown_output += f"- FSP3 (Fraction of SP3 hybridized carbons): {FSP3:.3f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating FSP3: {e}"

def calculate_usrcat_scores(sdffile):
    """
    Calculate USRCAT scores and Tanimoto coefficients for molecules in an SDF file.

    Args:
        sdf_path (str): The file path of the SDF file containing the molecules.

    Returns:
        str: A Markdown formatted string summarizing the USRCAT scores and Tanimoto 
             coefficients for molecule pairs, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(sdffile, str):
            raise ValueError("Input must be a file path.")

        # 读取SDF文件
        mols = [mol for mol in Chem.SDMolSupplier(sdffile) if mol is not None]
        valid_mols = []
        for mol in mols:
            if AllChem.EmbedMolecule(mol, useExpTorsionAnglePrefs=True, useBasicKnowledge=True) == 0:
                valid_mols.append(mol)

        if not valid_mols:
            return "No valid molecules with conformers found in the file."

        # 计算USRCAT分数和Tanimoto系数
        usrcats = [rdMolDescriptors.GetUSRCAT(mol) for mol in valid_mols]
        fps = [AllChem.GetMorganFingerprintAsBitVect(mol, 2) for mol in valid_mols]

        data = {"tanimoto": [], "usrscore": []}
        for i in range(len(usrcats)):
            for j in range(i):
                tc = DataStructs.TanimotoSimilarity(fps[i], fps[j])
                score = rdMolDescriptors.GetUSRScore(usrcats[i], usrcats[j])
                data["tanimoto"].append(tc)
                data["usrscore"].append(score)

        df = pd.DataFrame(data)
        markdown_output = "### USRCAT Scores and Tanimoto Coefficients\n\n"
        markdown_output += "Calculated for molecule pairs in the file.\n\n"

        for i in range(len(df)):
            markdown_output += f"- Pair {i+1}: USR Score = {df['usrscore'][i]:.4f}, Tanimoto Coefficient = {df['tanimoto'][i]:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating USRCAT scores and Tanimoto coefficients: {e}"

def calculate_shape_similarity(smiles_list):
    """
    Calculate shape similarity scores using USRCAT for a list of molecules defined by their SMILES.

    Args:
        smiles_list (list): A list of SMILES strings representing the molecules.

    Returns:
        str: A Markdown formatted string summarizing the SMILES strings, their indices, and 
             the USRCAT scores for each pair of molecules, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles_list, list) or not all(isinstance(smi, str) for smi in smiles_list):
            raise ValueError("Input must be a list of SMILES strings.")

        mols3d = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                raise ValueError(f"Invalid SMILES string: {smi}")
            m2 = Chem.AddHs(mol)
            if AllChem.EmbedMolecule(m2) != 0 or AllChem.MMFFOptimizeMolecule(m2, maxIters=2000) != 0:
                raise ValueError(f"Could not generate 3D conformation for molecule: {smi}")
            mols3d.append(m2)

        usrcats = [rdMolDescriptors.GetUSRCAT(mol) for mol in mols3d]

        markdown_output = "### Molecules and Their Indices\n\n"
        for idx, smi in enumerate(smiles_list):
            markdown_output += f"- Index {idx}: `{smi}`\n"

        markdown_output += "\n### Shape Similarity Scores (USRCAT)\n\n"
        for i in range(len(usrcats)):
            for j in range(i + 1, len(usrcats)):
                score = rdMolDescriptors.GetUSRScore(usrcats[i], usrcats[j])
                markdown_output += f"- Pair ({i}, {j}): USRCAT Score = {score:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating shape similarity: {e}"

def calculate_pmi(smiles):
    """
    Calculate the normalized principal moments of inertia (NPR1 and NPR2) for a molecule.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the NPR1 and NPR2 values of the molecule, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        m2 = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(m2) != 0 or AllChem.MMFFOptimizeMolecule(m2, maxIters=2000) != 0:
            raise ValueError("Could not generate or optimize 3D conformation for molecule.")

        # 计算NPR1和NPR2
        npr1 = rdMolDescriptors.CalcNPR1(m2)
        npr2 = rdMolDescriptors.CalcNPR2(m2)

        markdown_output = f"### NPR1 and NPR2 for Molecule: `{smiles}`\n\n"
        markdown_output += f"- NPR1 (Normalized Principal Moment of Inertia 1): {npr1:.4f}\n"
        markdown_output += f"- NPR2 (Normalized Principal Moment of Inertia 2): {npr2:.4f}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating NPR1 and NPR2: {e}"

def calculate_distance_matrix(smiles_list):
    """
    Calculate the distance matrix for a list of molecules based on their fingerprints.

    Args:
        smiles_list (list of str): A list of SMILES strings representing the molecules.

    Returns:
        str: A Markdown formatted string representing the distance matrix, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles_list, list) or not all(isinstance(smi, str) for smi in smiles_list):
            raise ValueError("Input must be a list of SMILES strings.")

        # 生成分子和它们的指纹
        data = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                raise ValueError(f"Invalid SMILES string: {smi}")
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2)
            data.append((smi, fp))  # 使用元组存储分子ID和指纹

        # 计算距离矩阵
        nPts = len(data)
        distsMatrix = np.zeros((nPts * (nPts - 1) // 2), dtype=np.float64)
        idx = 0
        for i in range(nPts):
            for j in range(i):
                distsMatrix[idx] = 1.0 - DataStructs.FingerprintSimilarity(data[i][1], data[j][1])
                idx += 1

        # 格式化为Markdown表格
        markdown_output = "### Molecules and Their Indices\n\n"
        for idx, smi in enumerate(smiles_list):
            markdown_output += f"- Mol {idx}: `{smi}`\n"
        markdown_output += "\n### Distance Matrix\n\n"
        markdown_output += "|   | " + " | ".join([f"Mol {i+1}" for i in range(nPts)]) + " |\n"
        markdown_output += "|---" * (nPts + 1) + "|\n"
        idx = 0
        for i in range(nPts):
            markdown_output += f"| Mol {i+1} | " + " | ".join(["{:.4f}".format(distsMatrix[idx + j - i - 1]) if i < j else "-" for j in range(nPts)]) + " |\n"
            idx += nPts - i - 1

        markdown_output += "\n*The distance matrix is calculated using Tanimoto similarity metric for the given SMILES strings.*"
        
        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while calculating the distance matrix: {e}"

def tanimoto_similarity(fp1, fp2):
    return DataStructs.TanimotoSimilarity(fp1, fp2)

def cluster_molecules(smiles_list, metric=tanimoto_similarity, algorithm_id=Murtagh.WARDS):
    """
    Clusters molecules based on their fingerprints and returns the clustering results in Markdown format.

    Args:
        smiles_list (list of str): A list of SMILES strings representing the molecules.
        metric (callable): A function to calculate the distance or similarity between fingerprints.
        algorithm_id (int): Identifier for the clustering algorithm to be used.

    Returns:
        str: A Markdown formatted string representing the clustering results, or an error message.
    """
    try:
        # 检查输入类型
        if not isinstance(smiles_list, list) or not all(isinstance(smi, str) for smi in smiles_list):
            raise ValueError("Input must be a list of SMILES strings.")

        # 生成分子和它们的指纹
        data = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                raise ValueError(f"Invalid SMILES string: {smi}")
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2)
            data.append((smi, fp))

        # 执行聚类
        clust_tree = ClusterPoints(data, metric, algorithm_id)

        # 分析聚类结果
        num_clusters = len(set([pt.GetIndex() for pt in clust_tree.GetPoints()]))
        
        # 格式化聚类结果为Markdown
        markdown_output = "### Clustering Results\n\n"
        markdown_output += f"Total number of clusters: {num_clusters}\n\n"
        for pt in clust_tree.GetPoints():
            idx = pt.GetIndex() - 1
            label = data[idx][0]  # 获取分子的SMILES字符串
            markdown_output += f"- {label}: Cluster Index = {idx}\n"

        return markdown_output
    except Exception as e:
        # 发生异常时返回错误消息
        return f"An error occurred while clustering molecules: {e}"
# 未实现
def cluster_molecules_from_details(details):
    """
    Clusters molecules based on the provided details and returns the clustering results in Markdown format.

    Args:
        details (SimpleDetails): An object containing data, metric, and cluster algorithm.

    Returns:
        str: A Markdown formatted string representing the clustering results, including the number of clusters.
    """
    # 检查是否有足够的数据
    if not details.data:
        return "### Clustering Results\n\nNo data available for clustering."

    # 使用ClusterPoints函数进行聚类
    clust_tree = ClusterPoints(details.data, details.metric, details.cluster_algo)

    # 分析聚类结果
    num_clusters = len(set([pt.GetIndex() for pt in clust_tree.GetPoints()]))

    # 格式化聚类结果为Markdown
    markdown_output = "### Clustering Results\n\n"
    markdown_output += f"Total number of clusters: {num_clusters}\n\n"
    for pt in clust_tree.GetPoints():
        idx = pt.GetIndex() - 1
        label = details.data[idx][0]  # 获取分子的SMILES字符串
        markdown_output += f"- {label}: Cluster Index = {idx}\n"

    return markdown_output

def process_fingerprint_mol(smiles):
    """
    Process the molecular fingerprint generated by FingerprintMol function.

    Args:
        mol (rdkit.Chem.rdchem.Mol): The molecule object to fingerprint.
        fingerprinter (function, optional): The fingerprinting function to use. Defaults to Chem.RDKFingerprint.

    Returns:
        str: A Markdown formatted string representing the molecular fingerprint in binary or hexadecimal format.
    """
    try:
        # 检查输入类型
        fingerprinter=Chem.RDKFingerprint
        if not isinstance(smiles, str):
            raise ValueError("Input must be a SMILES string.")

        # 将SMILES字符串转换为分子对象
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")
        # Generate fingerprint
        fp = FingerprintMol(mol)
        # Convert ExplicitBitVect to a readable format (binary or hexadecimal)
        if isinstance(fp, ExplicitBitVect):
            # Convert to a binary string representation
            binary_string = fp.ToBitString()
            # Alternatively, for a shorter representation, convert to hexadecimal
            hex_string = ''.join([f'{int(binary_string[i:i+8], 2):02x}' for i in range(0, len(binary_string), 8)])

            # Formatting the output in Markdown
            markdown_output = "### Molecular Fingerprint\n\n"
            markdown_output += f"**Binary Format:**\n`{binary_string}`\n\n"
            markdown_output += f"**Hexadecimal Format:**\n`{hex_string}`\n\n"

            return markdown_output
        else:
            return "Error: The fingerprint generated is not an ExplicitBitVect instance."
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def fingerprints_from_smiles(smiles_list):
    """
    Generate fingerprints for a list of SMILES strings.

    Args:
        smiles_list (list of str): List of SMILES strings.
        fingerprinter (function, optional): The fingerprinting function to use. Defaults to Chem.RDKFingerprint.
    Returns:
        str: A Markdown formatted string representing the fingerprints of the molecules.
    """
    try:
        reportFreq = 10
        maxMols = -1
        fingerprinter = Chem.RDKFingerprint
        # Convert SMILES to RDKit Mol objects with IDs
        mols = [(idx, Chem.MolFromSmiles(smi)) for idx, smi in enumerate(smiles_list)]
        res = []
        nDone = 0

        for ID, mol in mols:
            if mol:
                fp = FingerprintMols.FingerprintMol(mol, fingerprinter)
                # Convert to a binary string representation for display
                binary_string = fp.ToBitString()
                res.append((ID, binary_string))
                nDone += 1
                if reportFreq > 0 and not nDone % reportFreq:
                    print(f'Done {nDone} molecules\n')
                if maxMols > 0 and nDone >= maxMols:
                    break
            else:
                print(f'Problems with SMILES string: {smiles_list[ID]}\n')

        # Formatting the output in Markdown
        markdown_output = "### Molecular Fingerprints\n\n"
        for idx, smi in enumerate(smiles_list):
            markdown_output += f"Index {idx}: `{smi}`\n"
        markdown_output += '\n'
        for ID, fp_str in res:
            markdown_output += f"- Molecule {ID}: `{fp_str}`\n"

        return markdown_output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

@param_decorator
def fold_fingerprint_from_smiles(smiles, tgtDensity=0.3, minSize=64):
    """
    Generate a fingerprint from a SMILES string, fold it using a provided function, and provide detailed information.

    Args:
        smiles (str): The SMILES string of the molecule.
        tgtDensity (float, optional): The target density to achieve by folding. Defaults to 0.3.
        minSize (int, optional): The minimum size of the fingerprint after folding. Defaults to 64.

    Returns:
        str: A Markdown formatted string representing the original and folded fingerprints with additional details.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate fingerprint
        original_fp = FingerprintMols.FingerprintMol(mol)
        original_binary_fp = original_fp.ToBitString()
        original_nOn = original_fp.GetNumOnBits()
        original_nTot = original_fp.GetNumBits()

        # Fold the fingerprint using the provided function
        folded_fp = FoldFingerprintToTargetDensity(original_fp, tgtDensity=tgtDensity, minSize=minSize)
        folded_binary_fp = folded_fp.ToBitString()
        folded_nOn = folded_fp.GetNumOnBits()
        folded_nTot = folded_fp.GetNumBits()

        # Formatting the output in Markdown
        markdown_output = "### Fingerprint Folding Details\n\n"
        markdown_output += f"**SMILES:** `{smiles}`\n\n"
        markdown_output += "**Original Fingerprint:**\n"
        markdown_output += f"`{original_binary_fp}`\n"
        markdown_output += f"Bit count: {original_nTot}, On bits: {original_nOn}\n\n"
        markdown_output += "**Folded Fingerprint:**\n"
        markdown_output += f"`{folded_binary_fp}`\n"
        markdown_output += f"Bit count: {folded_nTot}, On bits: {folded_nOn}\n\n"

        return markdown_output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def get_rdk_fingerprint_from_smiles(smiles):
    """
    Generate an RDKit fingerprint from a SMILES string using default parameters.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A Markdown formatted string representing the RDKit fingerprint in binary format.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate RDKit fingerprint using default parameters
        fp = FingerprintMols.GetRDKFingerprint(mol)

        # Convert fingerprint to binary string
        binary_fp = fp.ToBitString()

        # Formatting the output in Markdown
        markdown_output = "### RDKit Fingerprint\n\n"
        markdown_output += f"**SMILES:** `{smiles}`\n\n"
        markdown_output += f"**Fingerprint:** `{binary_fp}`\n"

        return markdown_output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

@param_decorator
def get_fraggle_similarity(smiles1, smiles2, tverskyThresh=0.8):
    """
    Calculate the Fraggle similarity between two molecules represented by SMILES strings.

    Args:
        smiles1 (str): The SMILES string of the first molecule (query molecule).
        smiles2 (str): The SMILES string of the second molecule (reference molecule).
        tverskyThresh (float, optional): Tversky threshold for similarity. Defaults to 0.8.

    Returns:
        str: A Markdown formatted string representing the Fraggle similarity and the matching substructure.
    """
    try:
        # Generate molecules from SMILES
        queryMol = Chem.MolFromSmiles(smiles1)
        refMol = Chem.MolFromSmiles(smiles2)

        if not queryMol or not refMol:
            return "Invalid SMILES string(s)."

        # Calculate Fraggle similarity
        sim, match = GetFraggleSimilarity(queryMol, refMol, tverskyThresh)

        # Formatting the output in Markdown
        markdown_output = "### Fraggle Similarity\n\n"
        markdown_output += f"**SMILES 1:** `{smiles1}`\n"
        markdown_output += f"**SMILES 2:** `{smiles2}`\n\n"
        markdown_output += f"**Similarity Score:** `{sim}`\n"
        markdown_output += f"**Matching Substructure:** `{match}`\n"

        return markdown_output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def generate_fraggle_fragments(smiles):
    """
    Generate all possible Fraggle fragmentations for a molecule represented by a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A Markdown formatted string representing the list of possible fragmentations.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Fraggle fragmentations
        fragments = generate_fraggle_fragmentation(mol)

        # Sorting and formatting the fragments
        sorted_fragments = sorted(['.'.join(sorted(s.split('.'))) for s in fragments])

        # Formatting the output in Markdown
        markdown_output = "### Fraggle Fragmentations\n\n"
        markdown_output += f"**SMILES:** `{smiles}`\n\n"
        markdown_output += "**Fragments:**\n"
        for fragment in sorted_fragments:
            markdown_output += f"- `{fragment}`\n"

        return markdown_output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def check_valid_ring_cut(smiles):
    """
    Check if the molecule represented by a SMILES string is a valid ring cut.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A message indicating whether the molecule is a valid ring cut or not.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Check for valid ring cut
        is_valid = isValidRingCut(mol)

        return "Valid ring cut." if is_valid else "Not a valid ring cut."
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def build_atom_pair_fp_from_smiles(smiles):
    """
    Generate an Atom Pair Fingerprint from a SMILES string and display the results in a readable format.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A detailed message representing the Atom Pair Fingerprint.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Atom Pair Fingerprint
        fp = Pairs.GetAtomPairFingerprintAsIntVect(mol)

        # Formatting the output
        output = f"SMILES: `{smiles}`\n"
        output += "Atom Pair Fingerprint:\n"
        for idx, cnt in sorted(fp.GetNonzeroElements().items()):
            output += f"  Pair {idx}: Count {cnt}\n"

        return output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def build_torsions_fp_from_smiles(smiles):
    """
    Generate a Torsions Fingerprint from a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A detailed message representing the Torsions Fingerprint.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Torsions Fingerprint
        fp = Torsions.GetTopologicalTorsionFingerprintAsIntVect(mol)

        # Formatting the output
        output = f"SMILES: {smiles}\n"
        output += "Torsions Fingerprint:\n"
        for idx, cnt in sorted(fp.GetNonzeroElements().items()):
            output += f"  Torsion {idx}: Count {cnt}\n"

        return output
    except Exception as e:
        # In case of an error
        return f"An error occurred: {e}"

def build_rdkit_fp_from_smiles(smiles):
    """
    Generate an RDKit fingerprint from a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A detailed message representing the RDKit fingerprint.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate RDKit fingerprint
        fp = Chem.RDKFingerprint(mol, nBitsPerHash=1)

        # Formatting the output
        output = f"SMILES: {smiles}\n"
        output += "RDKit Fingerprint:\n"
        binary_fp = fp.ToBitString()
        output += f"{binary_fp}\n"

        return output
    except Exception as e:
        return f"An error occurred: {e}"
# 未实现
def build_pharm2d_fp_from_smiles(smiles, fdef_file=None):
    """
    Generate a Pharm2D fingerprint from a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.
        fdef_file (str, optional): Path to the feature definition file. If None, use RDKit default.

    Returns:
        str: A detailed message representing the Pharm2D fingerprint.
    """
    try:
        # Use RDKit's default feature definition file if none provided
        if fdef_file is None:
            fdef_file = Chem.GetDefaultRDKitDir() + '/Data/BaseFeatures.fdef'

        # Initialize SigFactory with the feature definition file
        featFactory = ChemicalFeatures.BuildFeatureFactory(fdef_file)
        sigFactory = SigFactory.SigFactory(featFactory, trianglePruneBins=False)
        sigFactory.SetBins([(2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 100)])

        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Pharm2D fingerprint
        fp = Generate.Gen2DFingerprint(mol, sigFactory)

        # Formatting the output
        output = f"SMILES: {smiles}\n"
        output += "Pharm2D Fingerprint:\n"
        binary_fp = fp.ToBitString()
        output += f"{binary_fp}\n"

        return output
    except Exception as e:
        return f"An error occurred: {e}"

# 'UIntSparseIntVect' object has no attribute 'ToBitString'
def build_morgan_fp_from_smiles(smiles):
    """
    Generate a Morgan fingerprint from a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A detailed message representing the Morgan fingerprint.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Morgan fingerprint
        fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2)  # Using radius 2 as an example

        # Formatting the output
        output = f"SMILES: {smiles}\n"
        output += "Morgan Fingerprint:\n"
        for idx in fp.GetOnBits():
            output += f"  Bit {idx}\n"

        return output
    except Exception as e:
        return f"An error occurred: {e}"
    
def build_avalon_fp_from_smiles(smiles):
    """
    Generate an Avalon fingerprint from a SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A detailed message representing the Avalon fingerprint.
    """
    try:
        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."

        # Generate Avalon fingerprint
        fp = BuildAvalonFP(mol)

        # Formatting the output
        output = f"SMILES: {smiles}\n"
        output += "Avalon Fingerprint:\n"
        binary_fp = fp.ToBitString()
        output += f"{binary_fp}\n"

        return output
    except Exception as e:
        return f"An error occurred: {e}"

def convert_smiles_to_inchi(smiles):
    """
    Converts a SMILES string to its corresponding InChI string.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the InChI representation of the molecule.
             If an error occurs during conversion, an error message is returned.
    """
    markdown_output = f"### SMILES to InChI Conversion\n\n- SMILES: `{smiles}`\n"

    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return "Invalid SMILES string."
        
        inchi = MolToInchi(mol)
        markdown_output += f"- InChI: `{inchi}`\n"
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}\n"

    return markdown_output

def generate_mol_key_from_smiles(smiles):
    """
    Generates a molecular key for a given molecule represented by a SMILES string.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the molecular key.
             If an error occurs during the process, an error message is returned.
    """
    markdown_output = f"### Molecular Key Generation\n\n- SMILES: `{smiles}`\n"

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        ctab = Generate2DCoords(smiles, True)
        res = MolKey.GetKeyForCTAB(ctab)
        markdown_output += f"- Molecular Key: `{res.mol_key}`\n"
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}\n"

    return markdown_output

def get_stereo_code_from_smiles(smiles):
    """
    Generates the stereo code for a given molecule represented by a SMILES string.

    Args:
        smiles (str): A SMILES representation of the molecule.

    Returns:
        str: A Markdown formatted string describing the stereo code of the molecule.
             If an error occurs during the process, an error message is returned.
    """
    markdown_output = f"### Stereo Code Generation\n\n- SMILES: `{smiles}`\n"

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string.")

        ctab = Generate2DCoords(smiles, True)
        res = MolKey.GetKeyForCTAB(ctab)
        markdown_output += f"- Stereo Code: `{res.stereo_code}`\n"
    except Exception as e:
        markdown_output += f"Error occurred: {str(e)}\n"

    return markdown_output


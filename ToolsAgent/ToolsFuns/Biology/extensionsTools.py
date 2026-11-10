import os
import MDAnalysis
import numpy as np
from config import Config

from Bio.Seq import Seq
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.Blast import NCBIWWW, NCBIXML
## from MDAnalysis api
def analyze_atom_count(file_name: str) -> str:
    """
    Analyzes the number of atoms in a PDB file using MDAnalysis.

    Args:
        pdb_file (str): The path to the PDB file.

    Returns:
        str: A Markdown formatted string summarizing the atom count or an error message if the analysis fails.
    """
    try:
        pdb_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name if file_name.endswith('.pdb') else file_name + '.pdb')
        u = MDAnalysis.Universe(pdb_file)
        atom_count = len(u.atoms)
        return f"## Atom Count Analysis\n\n- **PDB File**: `{file_name}`\n- **Total Atoms**: `{atom_count}`\n"
    except Exception as e:
        return f"Error occurred while analyzing atom count: {str(e)}\n"

def calculate_molecular_weight(file_name: str) -> str:
    """
    Calculates the molecular weight of a structure in a PDB file using MDAnalysis.

    Args:
        pdb_file (str): The path to the PDB file.

    Returns:
        str: A Markdown formatted string with the molecular weight or an error message if the calculation fails.
    """
    try:
        pdb_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name if file_name.endswith('.pdb') else file_name + '.pdb')
        u = MDAnalysis.Universe(pdb_file)
        weights = u.atoms.masses
        molecular_weight = sum(weights)
        return f"## Molecular Weight Calculation\n\n- **PDB File**: `{file_name}`\n- **Molecular Weight**: `{molecular_weight:.2f} g/mol`\n"
    except Exception as e:
        return f"Error occurred while calculating molecular weight: {str(e)}\n"

def calculate_center_of_mass(file_name: str) -> str:
    """
    Calculates the center of mass of the molecule in a PDB file using MDAnalysis.

    Args:
        pdb_file (str): The path to the PDB file.

    Returns:
        str: A Markdown formatted string with the center of mass coordinates or an error message if the calculation fails.
    """
    try:
        pdb_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name if file_name.endswith('.pdb') else file_name + '.pdb')
        u = MDAnalysis.Universe(pdb_file)
        center_of_mass = u.atoms.center_of_mass()
        return f"## Center of Mass Calculation\n\n- **PDB File**: `{file_name}`\n- **Center of Mass**: `({center_of_mass[0]:.2f}, {center_of_mass[1]:.2f}, {center_of_mass[2]:.2f})`\n"
    except Exception as e:
        return f"Error occurred while calculating center of mass: {str(e)}\n"
    
def calculate_average_coordinates(file_name: str) -> str:
    """
    Calculates the average coordinates of all atoms in a PDB file using MDAnalysis.

    Args:
        pdb_file (str): The path to the PDB file.

    Returns:
        str: A Markdown formatted string with the average coordinates or an error message if the calculation fails.
    """
    try:
        pdb_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name if file_name.endswith('.pdb') else file_name + '.pdb')
        u = MDAnalysis.Universe(pdb_file)
        average_coordinates = u.atoms.positions.mean(axis=0)
        return (f"## Average Coordinates Calculation\n\n"
                f"- **PDB File**: `{file_name}`\n"
                f"- **Average Coordinates**: `({average_coordinates[0]:.2f}, {average_coordinates[1]:.2f}, {average_coordinates[2]:.2f})`\n")
    except Exception as e:
        return f"Error occurred while calculating average coordinates: {str(e)}\n"

def calculate_atom_distance(file_name: str) -> str:
    """
    Calculates the distance between the first two atoms in a PDB file using MDAnalysis.

    Args:
        pdb_file (str): The path to the PDB file.

    Returns:
        str: A Markdown formatted string with the distance or an error message if the calculation fails.
    """
    try:
        pdb_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name if file_name.endswith('.pdb') else file_name + '.pdb')
        u = MDAnalysis.Universe(pdb_file)
        if len(u.atoms) < 2:
            return "Error: Not enough atoms in the PDB file to calculate distance.\n"

        atom1_pos = u.atoms[0].position
        atom2_pos = u.atoms[1].position
        distance = np.linalg.norm(atom1_pos - atom2_pos)
        return f"## Atom Distance Calculation\n\n- **PDB File**: `{file_name}`\n- **Distance between Atom 1 and Atom 2**: `{distance:.2f} Å`\n"
    except Exception as e:
        return f"Error occurred while calculating atom distance: {str(e)}\n"

## from Biopython


def get_amino_acid_frequency(sequence: str) -> str:
    """
    Calculates the frequency of each amino acid in a protein sequence.

    Args:
        sequence (str): The protein sequence.

    Returns:
        str: A Markdown formatted string summarizing the amino acid frequency.
    """
    try:
        # 计算氨基酸频率
        amino_acid_count = {}
        total_length = len(sequence)
        
        for amino_acid in sequence:
            if amino_acid in amino_acid_count:
                amino_acid_count[amino_acid] += 1
            else:
                amino_acid_count[amino_acid] = 1
        
        frequency_table = "| Amino Acid | Frequency (%) |\n"
        frequency_table += "|-------------|----------------|\n"
        
        for amino_acid, count in sorted(amino_acid_count.items()):
            frequency = (count / total_length) * 100
            frequency_table += f"| `{amino_acid}` | `{frequency:.2f}` |\n"

        return (f"## Amino Acid Frequency\n\n"
                f"- **Sequence**: `{sequence}`\n"
                f"{frequency_table}")
    except Exception as e:
        return f"Error occurred while calculating amino acid frequency: {str(e)}\n"


def get_reverse_complement(sequence: str) -> str:
    """
    Generates the reverse complement of a DNA sequence.

    Args:
        sequence (str): The DNA sequence.

    Returns:
        str: A Markdown formatted string with the reverse complement.
    """
    try:
        seq = Seq(sequence)
        reverse_complement = seq.reverse_complement()
        return (f"## Reverse Complement Sequence\n\n"
                f"- **Original Sequence**: `{sequence}`\n"
                f"- **Reverse Complement**: `{reverse_complement}`\n")
    except Exception as e:
        return f"Error occurred while generating reverse complement: {str(e)}\n"   


def calculate_hydrophobicity_and_polarity(sequence: str) -> str:
    """
    Calculates the hydrophobicity and polarity of a protein sequence.

    Args:
        sequence (str): The protein sequence.

    Returns:
        str: A Markdown formatted string with hydrophobicity and polarity.
    """
    try:
        # 清理序列，移除非氨基酸字符
        sequence = ''.join(filter(lambda x: x in 'ACDEFGHIKLMNPQRSTVWY', sequence.upper()))
        
        if not sequence:
            return "Error: The input sequence is empty or contains invalid characters.\n"
        
        analyzed_seq = ProteinAnalysis(sequence)
        hydropathy_index = analyzed_seq.gravy()  # Hydropathy index (GRAVY)
        polarity = analyzed_seq.isoelectric_point()  # Isoelectric point for polarity estimation

        return (f"## Hydrophobicity and Polarity Calculation\n\n"
                f"- **Sequence**: `{sequence}`\n"
                f"- **Hydropathy Index (GRAVY)**: `{hydropathy_index:.2f}`\n"
                f"- **Estimated Isoelectric Point (pI)**: `{polarity:.2f}`\n")
    except Exception as e:
        return f"Error occurred while calculating hydrophobicity and polarity: {str(e)}\n"
    
def predict_secondary_structure(sequence: str) -> str:
    """
    Predicts the secondary structure content (alpha helix, beta sheet) of a protein sequence.

    Args:
        sequence (str): The protein sequence.

    Returns:
        str: A Markdown formatted string summarizing the predicted secondary structure.
    """
    try:
        analyzed_seq = ProteinAnalysis(sequence)
        helix_fraction = analyzed_seq.secondary_structure_fraction()[0]  # 计算α螺旋的比例
        sheet_fraction = analyzed_seq.secondary_structure_fraction()[1]  # 计算β折叠的比例
        
        return (f"## Secondary Structure Prediction\n\n"
                f"- **Sequence**: `{sequence}`\n"
                f"- **Alpha Helix Fraction**: `{helix_fraction:.2%}`\n"
                f"- **Beta Sheet Fraction**: `{sheet_fraction:.2%}`\n")
    except Exception as e:
        return f"Error occurred while predicting secondary structure: {str(e)}\n"

def perform_blast_query(sequence_data: str, max_results: int = 20) -> str:
    """
    对给定的蛋白质序列使用 NCBI 的 BLAST 服务执行查询，并限制输出结果的数量。

    参数：
        sequence_data (str): 以 FASTA 格式提供的蛋白质序列字符串。
        max_results (int): 要输出的最大对齐结果数量，默认值为 20。

    返回：
        str: 包含 BLAST 查询结果的 Markdown 格式字符串或错误信息。
    """
    try:
        # Use the blastp program to query the nr (non-redundant protein) database
        result_handle = NCBIWWW.qblast("blastp", "nr", sequence_data)
        blast_record = NCBIXML.read(result_handle)
        
        markdown_output = "## BLAST Query Results\n\n"
        
        significant_alignments = False
        alignment_count = 0  # 添加计数器
        
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                if hsp.expect < 0.01:
                    significant_alignments = True
                    markdown_output += f"### Alignment\n\n"
                    markdown_output += f"- **Sequence**: `{alignment.title}`\n"
                    markdown_output += f"- **Length**: `{alignment.length}`\n"
                    markdown_output += f"- **E-value**: `{hsp.expect}`\n"
                    markdown_output += f"- **Query**: `{hsp.query[0:75]}...`\n"
                    markdown_output += f"- **Match**: `{hsp.match[0:75]}...`\n"
                    markdown_output += f"- **Subject**: `{hsp.sbjct[0:75]}...`\n\n"
                    
                    alignment_count += 1
                    if alignment_count >= max_results:
                        break  # 达到最大结果数量，退出循环
            if alignment_count >= max_results:
                break  # 达到最大结果数量，退出循环
        
        if not significant_alignments:
            markdown_output += "No significant alignments found.\n"
        
        return markdown_output
    except Exception as e:
        return f"Error occurred while performing BLAST query: {str(e)}\n"
    
# if __name__ == '__main__':
#     pdb_file = "/home/hjj/project/ToolsKG/DataFiles/pdb/esmfold/_temp.pdb"

#     res = analyze_atom_count(pdb_file)
#     # res = calculate_molecular_weight(pdb_file)
#     # res = calculate_center_of_mass(pdb_file)

#     # res = calculate_average_coordinates(pdb_file)
#     # res = calculate_atom_distance(pdb_file)
#     print(res)
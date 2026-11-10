
import os
from moffragmentor.mof import MOF
from moffragmentor import fragmentor
from pymatgen.core import Structure
from config import Config

# @param_decorator
def get_symbol_of_site(cif_file_name: str, site: int) -> str:
    """
    Get the elemental symbol of the site indexed by 'site' in a MOF structure from a cif file name.
    This function is useful for identifying the elemental composition of specific sites within MOF structures.
    
    Args:
        cif_file_name (str): The name of the MOF cif file.
        site (int): The index of the site for which the elemental symbol is to be found.
    
    Returns:
        str: A string or Markdown formatted text with the elemental symbol for the specified site, 
             or an error message including the name of the cif file.
    """
    try:

        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        # Check if the file exists
        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        # Load the MOF structure from the CIF file
        mof = MOF.from_cif(cif_file_path)
        
        # Check if the site index is within the valid range
        if site < 0 or site >= len(mof.structure.sites):
            return f"Error: The site index {site} is out of range. The valid site index should be between 0 and {len(mof.structure.sites) - 1}."
 
        # Get the elemental symbol of the specified site
        elemental_symbol = mof.get_symbol_of_site(site)
        
        # Return the result in Markdown format
        return f"## Elemental Symbol for Site {site} in {cif_file_name}\n\n" + \
               f"The elemental symbol of site {site} is: `{elemental_symbol}`."
    
    except Exception as e:
        return f"Error occurred while processing the file: {e}"

def plot_adjacency_matrix(cif_file_name: str) -> str:
    """
    Generate a base64-encoded adjacency matrix plot for a given MOF structure from a CIF file,
    and return it as a Markdown image tag.
    
    Args:
        cif_file_name (str): The name of the MOF cif file, without the '.cif' extension.
    
    Returns:
        str: A Markdown string with the base64 encoded image of the adjacency matrix.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        # Check if the file exists
        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        # Create MOF object from CIF
        mof = MOF.from_cif(cif_file_path)
        
        # Generate the base64-encoded plot
        markdown_image = mof.show_adjacency_matrix_base64(highlight_metals=False)
        
        # Compose descriptive information
        description = f"## Adjacency Matrix for {cif_file_name}\n\n" + \
                      "This image represents the adjacency matrix of the MOF structure. " + \
                      ("Metals are not highlighted.") + "\n\n"
        
        return description + markdown_image
    except Exception as e:
        return f"Error occurred while processing the file {cif_file_name}: {e}"

def get_terminal_indices(cif_file_name: str) -> str:
    """
    Generate a Markdown string listing the indices of terminal sites in a MOF structure from a CIF file.
    
    Terminal sites are defined as sites having only one neighbor and are connected via a bridge to the rest of the structure. 
    Splitting the bond between the terminal site and the rest of the structure will increase the number of connected components. 
    Typical examples of terminal sites include hydrogen atoms or halogen functional groups.
    
    Args:
        cif_file_name (str): The name of the MOF cif file, without the '.cif' extension.
    
    Returns:
        str: A Markdown string with a description and list of the indices of terminal sites.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        # Check if the file exists
        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."
        
        # Create MOF object from CIF
        mof = MOF.from_cif(cif_file_path)
        
        # Get the indices of terminal sites
        terminal_indices = mof.terminal_indices
        
        # Prepare the Markdown output
        markdown_output = f"## Terminal Sites in {cif_file_name}\n\n" + \
                          "Terminal sites are defined as sites having only one neighbor and are " + \
                          "connected via a bridge to the rest of the structure. " + \
                          "Splitting the bond between the terminal site and the rest of the structure " + \
                          "will increase the number of connected components. " + \
                          "Typical examples of terminal sites include hydrogen atoms or halogen functional groups.\n\n" + \
                          "**Indices of Terminal Sites:**\n" + \
                          ', '.join(str(index) for index in terminal_indices)
        
        return markdown_output
    except Exception as e:
        return f"Error occurred while processing the file {cif_file_name}: {e}"

def get_floating_solvent_molecules(cif_file_name: str) -> str:
    """
    Generate a Markdown string listing the composition and quantity of floating solvent molecules in a MOF structure from a CIF file.
    
    Floating solvent molecules are identified as NonSbuMolecules that are not part of the structural building units (SBUs) of the MOF.
    
    Args:
        cif_file_name (str): The name of the MOF cif file, without the '.cif' extension.
    
    Returns:
        str: A Markdown string with a description and list of the composition and quantity of floating solvent molecules.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        # Check if the file exists
        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."
        
        # Create MOF object from CIF
        mof = MOF.from_cif(cif_file_path)
        
        # Get the collection of floating solvent molecules
        solvent_collection = fragmentor.solventlocator.get_floating_solvent_molecules(mof)
        
        markdown_output = f"## Floating Solvent Molecules in {cif_file_name}\n\n" + \
                          "Floating solvent molecules are identified as NonSbuMolecules that are not part " + \
                          "of the structural building units (SBUs) of the MOF.\n\n" + \
                          "**Composition and Quantity:**\n"
        
        if len(solvent_collection) == 0:
            markdown_output += "No floating solvent molecules were detected in this MOF structure."
        else:
            composition_dict = solvent_collection.composition
            for molecule_type, quantity in composition_dict.items():
                markdown_output += f"- {molecule_type}: {quantity}\n"
        
        return markdown_output
    except Exception as e:
        return f"Error occurred while processing the file {cif_file_name}: {e}"



def get_structure_info(file_name: str) -> str:
    """
    Reads a structure file and returns basic information about the structure.

    Args:
        file_name (str): The name of the structure file (e.g., POSCAR, CIF).

    Returns:
        str: A Markdown formatted string with structure information or an error message if the operation fails.
    """
    try:
        structure_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name)
        structure = Structure.from_file(structure_file)
        return (f"## Structure Information\n\n"
                f"- **File Name**: `{file_name}`\n"
                f"- **Number of Sites**: `{len(structure)}`\n"
                f"- **Lattice Parameters**: `{structure.lattice}`\n")
    except Exception as e:
        return f"Error occurred while reading structure: {str(e)}\n"


def calculate_density(file_name: str) -> str:
    """
    Calculates the density of a structure from a file.

    Args:
        file_name (str): The name of the structure file (e.g., POSCAR, CIF).

    Returns:
        str: A Markdown formatted string with the density or an error message if the calculation fails.
    """
    try:
        structure_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name)
        structure = Structure.from_file(structure_file)
        density = structure.density
        return (f"## Density Calculation\n\n"
                f"- **File Name**: `{file_name}`\n"
                f"- **Density**: `{density:.2f} g/cm³`\n")
    except Exception as e:
        return f"Error occurred while calculating density: {str(e)}\n"

def get_element_composition(file_name: str) -> str:
    """
    Returns the elemental composition of a structure from a file.

    Args:
        file_name (str): The name of the structure file (e.g., POSCAR, CIF).

    Returns:
        str: A Markdown formatted string with the elemental composition or an error message if the operation fails.
    """
    try:
        structure_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name)
        structure = Structure.from_file(structure_file)
        composition = structure.composition
        return (f"## Element Composition\n\n"
                f"- **File Name**: `{file_name}`\n"
                f"- **Composition**: `{composition}`\n")
    except Exception as e:
        return f"Error occurred while getting element composition: {str(e)}\n"

def calculate_symmetry(file_name: str) -> str:
    """
    Calculates the symmetry of a structure from a file.

    Args:
        file_name (str): The name of the structure file (e.g., POSCAR, CIF).

    Returns:
        str: A Markdown formatted string with the symmetry information or an error message if the operation fails.
    """
    try:
        structure_file = os.path.join(Config().UPLOAD_FILES_BASE_PATH, file_name)
        structure = Structure.from_file(structure_file)
        symmetry = structure.get_space_group_info()
        return (f"## Symmetry Information\n\n"
                f"- **File Name**: `{file_name}`\n"
                f"- **Space Group**: `{symmetry[0]}`\n"
                f"- **Number of Symmetry Operations**: `{symmetry[1]}`\n")
    except Exception as e:
        return f"Error occurred while calculating symmetry: {str(e)}\n"
    

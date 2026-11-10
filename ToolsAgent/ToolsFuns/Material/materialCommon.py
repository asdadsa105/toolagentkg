import os
from pathlib import Path
from matplotlib import pyplot as plt
import json
import requests
import re
from config import Config
from rdkit import Chem

from moffragmentor.mof import MOF
from moffragmentor import fragmentor
from ToolsFuns.Chemical.utils import is_smiles

def mof_to_smiles(cif_files: str) -> str:
    """
    Convert multiple MOF materials into SMILES representations and return the results in Markdown table format.

    Args:
        cif_files (str): Comma-separated file names of the mof materials.
    
    Return:
        str: A string containing a Markdown table with the names, SMILES, and status of MOF materials.
    """
    cif_file_names = [name.strip() for name in cif_files.split(',')]
    results = []
    
    base_path = Config().UPLOAD_FILES_BASE_PATH
    # print(f"base_path in fun:{base_path}")
    markdown_table = "| Name | SMILES | Status |\n"
    markdown_table += "|------|--------|--------|\n"

    for cif_file_name in cif_file_names:
        if not cif_file_name.endswith('.cif'):
            cif_file_name += '.cif'
        
        cif_file_path = os.path.join(base_path, cif_file_name)
        
        result = {"Name": Path(cif_file_name).stem, "SMILES": "", "Status": ""}

        if not os.path.exists(cif_file_path):
            result["Status"] = "File not found"
            results.append(result)
            markdown_table += f"| {result['Name']} | {result['SMILES']} | {result['Status']} |\n"
            continue

        try:
            mof = MOF.from_cif(cif_file_path)
            fragments = mof.fragment()
            
            if not fragments or not fragments.linkers:
                result["Status"] = "No linkers found"
            else:
                result["SMILES"] = fragments.linkers[0].smiles
                result["Status"] = "Success"

        except Exception as e:
            result["Status"] = f"Error: {e}"

        markdown_table += f"| {result['Name']} | {result['SMILES']} | {result['Status']} |\n"
        results.append(result)
    
    return markdown_table

def smiles_to_cas(smiles: str) -> str:
    """
    Query a SMILES and return their CAS numbers in string.
    
    Args:
        smiles (str): String containing smiles .
    
    Returns:
        cas (str): A string of dictionaries containing SMILES string and their CAS number.
    """
    try:
        smiles = smiles.strip("'\"").strip("'\`'")
        
        mode = "smiles"
        if not is_smiles(smiles):
            raise ValueError(f"Invalid SMILES string: {smiles}")
        
        url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{mode}/{smiles}/cids/JSON"
        cid_response = requests.get(url_cid)
        cid_response.raise_for_status()
        cid = cid_response.json()["IdentifierList"]["CID"][0]

        url_data = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        data_response = requests.get(url_data)
        data_response.raise_for_status()
        data = data_response.json()

        cas_number = None
        for section in data["Record"]["Section"]:
            if section.get("TOCHeading") == "Names and Identifiers":
                for subsection in section["Section"]:
                    if subsection.get("TOCHeading") == "Other Identifiers":
                        for subsubsection in subsection["Section"]:
                            if subsubsection.get("TOCHeading") == "CAS":
                                cas_number = subsubsection["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                                break

        if cas_number:
            return f"#### Smiles \n {smiles}\n #### CAS \n {cas_number}"
        else:
            return f"CAS number not found for {smiles}"
    except Exception as e:
        return f"Tool function execution error, Error querying for {smiles}: {str(e)}"
        
def cas_to_values(cas: str):
    """
    Fetches data for a given chemical substance identified by its CAS number.

    Args:
    cas_number (str): The CAS number of the chemical substance.

    Returns:
    dict: The response data as a dictionary.
    """
    session = requests.Session()

    session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
    }
    data = {
        "searchString": f'{{"cas":"{cas}","keywords":"{cas}","brandBm":{{}},"spec":{{}},"classMap":{{}},"bpbSourcenm":"","deliveryDate":"","labelId":"","pattern":"列表模式","elementId":"","smiles":"","searchStruType":"","similarValue":""}}',
        # "searchString": f'{{"cas":"{cas_number}","keywords":"{cas_number}","brandBm":{{}},"spec":{{}},"classMap":{{}},"bpbSourcenm":"","deliveryDate":"","labelId":"","pattern":"列表模式","elementId":"","smiles":"","searchStruType":"","similarValue":""}}',
        "currentPage": "1",
        "groupValue": "试剂产品"
    }

    url = "https://www.energy-chemical.com/front/searchProductList.htm"
    try:
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
        return None

def extract_weight_and_convert_to_grams(string):
    """
    Extracts the weight from a string and converts it to grams.

    Args:
    string (str): A string containing a weight (e.g., "500g", "1kg").

    Returns:
    int: The weight in grams.
    """
    # Regular expression to find the numeric value and the unit
    match = re.search(r'(\d+)([kKgG]+)', string)
    if match:
        # Extract the number and the unit
        number, unit = match.groups()

        # Convert the number to an integer
        number = int(number)

        # Convert to grams if necessary
        if unit.lower() == 'kg':
            number *= 1000  # Convert kilograms to grams

        return number
    else:
        return None

def calculate_average_values(response_text: str):
    AverageValue = 0
    data_json = json.loads(response_text)
    data = data_json['resultList'][0]['list2'][0]['mstList'][0]['pkgList']
    size_number = len(data)
    if data:
        for pkg in data:
            uniPack = extract_weight_and_convert_to_grams(pkg['bppPack'])
            if not uniPack:
                continue
            # print(uniPack)
            AverageValue += pkg['price']/ uniPack
    AverageValue /= size_number
    return AverageValue
    
def cas_to_price(cas: str) -> str:
    """
    Fetches average price for multiple chemical substances identified by their CAS numbers.
    This tool is usually a must-have if someone asks directly about the price of mof materials. And it is often used as a third tool.
    Note: If someone ask the price of MOF materials, you need to convert the MOF material to Smiles first, then convert Smiles into CAS, and finally query the price through CAS.
    
    Args:
        cas_number (str): String containing a cas number.
    
    Returns:
        str: A string of dictionaries containing CAS number and their average price.
    """

    try:
        response_text = cas_to_values(cas)
        if response_text:
            average_price = calculate_average_values(response_text)
            markdown_content = f"#### CAS \n{cas}\n #### Average price \n ￥{average_price}"
            # price_results.append({"name": item["name"], "price": average_price})
        else:
            markdown_content = f"Failed to get response for CAS number {cas}"
    except Exception as e:
        print(f"Error processing CAS number {cas}: {e}")

    return markdown_content

def get_mof_lattice(cif_file_name: str) -> str:
    """
    Obtain lattice structure information from the provided MOF cif file name.
    Note: Please directly pass the cif file name, such as 'HKUST-1', as Action Input. The function will construct the file path based on a predefined directory.
    The function returns the information in a Markdown table format.
    """
    try:  
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        mof = MOF.from_cif(str(cif_file_path))
        lattice = mof.lattice  

        markdown_table = f"""
| Property     | Value                                  |
|--------------|----------------------------------------|
| name         | {cif_file_name}                        |
| abc          | {', '.join(map(str, lattice.abc))}     |
| angles       | {', '.join(map(str, lattice.angles))}  |
| volume       | {lattice.volume}                       |
| A vector     | {', '.join(map(str, lattice.matrix[0]))} |
| B vector     | {', '.join(map(str, lattice.matrix[1]))} |
| C vector     | {', '.join(map(str, lattice.matrix[2]))} |
| Periodic BCs | {lattice.pbc}                          |
"""
    except Exception as e:
        markdown_table = f"Error occurred: {e}"

    return markdown_table

# Not implemented
def show_mof_structure(mof_file_path: str):
    """
    Show the structure diagram of mof
    """
    mof = MOF.from_cif(mof_file_path)
    mof.show_structure()
    pass

# @timer_decorator
def get_mof_fractional_coordinates(cif_file_name: str):
    """
    Obtain fractional coordinates from a provided MOF cif file name and return them in Markdown format.
    Note: Please directly pass the cif file name, such as 'HKUST-1', as Action Input. The function will construct the file path based on a predefined directory.
    Args:
        cif_file_name (str): The name of the MOF cif file.

    Returns:
        str: Markdown formatted table of fractional coordinates, including the cif file name.
    """
    try:
        
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        mof = MOF.from_cif(str(cif_file_path))
        frac_coords = mof.frac_coords

        markdown_table = f"#### Fractional Coordinates for {cif_file_name}\n\n| Index | x    | y    | z    |\n|-------|------|------|------|\n"
        for i, (x, y, z) in enumerate(frac_coords):
            markdown_table += f"| {i+1} | {x:.3f} | {y:.3f} | {z:.3f} |\n"

    except Exception as e:
        markdown_table = f"Error occurred while processing the file: {e}"

    return markdown_table


# @param_decorator
def get_neighbor_indices(cif_file_name: str, site_index: int) -> str:
    """
    Get a list of neighbor indices for a given site in a MOF structure from a cif file name, presented in a simple text format.
    Note: Please directly pass the cif file name, such as 'HKUST-1', as Action Input. The function will construct the file path based on a predefined directory.
    Args:
        cif_file_name (str): The name of the MOF cif file.
        site_index (int): The index of the site for which neighbors are to be found.

    Returns:
        str: A string listing the neighbor indices or an error message, including the name of the cif file.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        mof = MOF.from_cif(str(cif_file_path))
    
        # Check the total number of sites in the MOF
        total_sites = len(mof.structure.sites)
        if site_index < 0 or site_index >= total_sites:
            return f"Invalid site index {site_index}. It should be between 0 and {total_sites - 1}."

        neighbor_indices = mof.get_neighbor_indices(site_index)

        # Format the output as a string
        neighbor_indices_str = ", ".join(map(str, neighbor_indices))
        return f"This MOF material, {cif_file_name}, has a total of {total_sites} sites. Neighbor Indices for Site {site_index} are: {neighbor_indices_str}."

    except Exception as e:
        return f"Error occurred while processing the file: {e}"

# @timer_decorator
def get_branch_points(cif_file_name: str):
    """
    Get all branch points in a MOF structure from a cif file name. This function is useful for identifying critical connection points in MOF structures.
    Note: Please directly pass the cif file name, such as 'HKUST-1', as Action Input. The function will construct the file path based on a predefined directory.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        mof = MOF.from_cif(str(cif_file_path))
        branch_points = fragmentor.branching_points.get_branch_points(mof)
        
        markdown_table = f"#### Branch Points for {cif_file_name}\n\n| Index | Branch Point |\n|-------|--------------|\n"
        for index, point in enumerate(branch_points, start=1):
            markdown_table += f"| {index} | {point} |\n"

    except Exception as e:
        markdown_table = f"Error occurred while processing the file: {e}"

    return markdown_table


def get_bridges(cif_file_name: str):
    """
    Query and obtain all bridge point information of MOF materials from a cif file name.
    Note: Please directly pass the cif file name, such as 'HKUST-1', as Action Input. The function will construct the file path based on a predefined directory.
    """
    try:
        cif_file_path = Config().UPLOAD_FILES_BASE_PATH

        if not cif_file_path:
            return "File does not exist: Please check the cif file name and directory."

        mof = MOF.from_cif(str(cif_file_path))
        bridges = mof.bridges
        
        markdown_table = f"#### Bridge Points for {cif_file_name}\n\n| Bridge Point ID | Associated Points |\n|-----------------|--------------------|\n"
        for bridge_point_id, associated_points in bridges.items():
            associated_points_str = ', '.join(map(str, associated_points))
            markdown_table += f"| {bridge_point_id} | {associated_points_str} |\n"

    except Exception as e:
        markdown_table = f"Error occurred while processing the file: {e}"

    return markdown_table



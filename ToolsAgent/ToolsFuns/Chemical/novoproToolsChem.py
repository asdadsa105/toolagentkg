import logging
import re
from rdkit import Chem
import html2text
import selfies as sf
import random

from .utils import is_smiles
from ToolsFuns.utils.sendRequest import send_chemspider_request

# IsValidInChIKey
def is_valid_inchikey(inchikey: str) -> str:
    """
    Check if an InChIKey string is valid.
    Args:
        inchikey: InChIKey string.
    Return:
        str: true or false
    """
    try:
        cleaned_inchikey = inchikey.replace('\n', '').replace(' ', '')
        data = {
            "inchi_key": cleaned_inchikey,
        }
        response = send_chemspider_request(
            "http://legacy.chemspider.com/InChI.asmx/IsValidInChIKey", data)
        h = html2text.HTML2Text()
        result = h.handle(response).replace("\n", "").replace(" ", "")
        return result
    except Exception as e:
        return f"Error is valid InChIKey: {e}"


def smiles_to_inchi(smiles: str) -> str:
    """
    Convert a SMILES string to an InChI string.
    Args:
        smiles: SMILES string.
    Return:
        str: The Markdown content with InChI.
    """
    try:
        cleaned_smiles = smiles.replace('\n', '').replace(' ', '')
        mol = Chem.MolFromSmiles(cleaned_smiles)
        inchi = Chem.MolToInchi(mol)
        if is_smiles(cleaned_smiles):
        #     data ={
        #         "smiles": cleaned_smiles,
        #     }
        #     response = send_chemspider_request("http://legacy.chemspider.com/InChI.asmx/SMILESToInChI", data)
        #     h = html2text.HTML2Text()
        #     result = h.handle(response)
            markdown = f'''
**SMILES to InChI**
SMILES={cleaned_smiles}
**Result:**
{inchi}
'''
            return markdown
        else:
            return "Invalid SMILES input."
    except Exception as e:
        logging.error(f"Error SMILES to InChI: {e}")


# InChIKeyToSMILES
def inchikey_to_smiles(inchikey: str) -> str:
    """
    Convert an InChIKey string to a SMILES string.
    """
    try:
        if is_valid_inchikey(inchikey) == "true":
            data = {
                "inchi_key": inchikey,
                "out_format": "InChI"
            }
            response = send_chemspider_request("https://legacy.chemspider.com/InChI.asmx/ResolveInChIKey", data)
            h = html2text.HTML2Text()
            result = h.handle(response)
            result = result.split('\n')
            inchi = result[0]
            data = {
                "inchi": inchi,
            }
            response = send_chemspider_request("https://legacy.chemspider.com/InChI.asmx/InChIToSMILES", data)

            h = html2text.HTML2Text()
            result = h.handle(response)
            markdown = f'''
**InChIKey to SMILES**
{inchikey}
**SMILES:**
{result}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error InChIKey to SMILES: {e}")


# InChIKeyToInChI
def inchikey_to_inchi(inchikey: str) -> str:
    """
    Convert an InChIKey string to InChI.
    Args:
        inchikey: InChIKey string.
    """
    try:
        if is_valid_inchikey(inchikey) == "true":
            data ={
                "inchi_key": inchikey,
                "out_format": "InChI"
            }
            response = send_chemspider_request("http://legacy.chemspider.com/InChI.asmx/ResolveInChIKey", data)
            h = html2text.HTML2Text()
            result = h.handle(response)
            result = result.split('\n')
            markdown = f'''
**InChIKey to InChi**
InChIKey = {inchikey}
**Result:** 
{result[0]}
'''
            return markdown
        else:
            return "Invalid InChIKey input."
    except Exception as e:
        logging.error(f"Error InChIKey to InChI: {e}")

# InChIKeyToMOL
def inchikey_to_mol(inchikey: str) -> str:
    """
    Convert an InChI string to a MOL string.
    Args:
        inchikey: InChIKey string.
    """
    try:
        cleaned_inchikey = inchikey.replace('\n', '').replace(' ', '')
        if is_valid_inchikey(inchikey) == "true":
            data ={
                "inchi_key": cleaned_inchikey,
                "out_format": "MOL"
            }
            response = send_chemspider_request("http://legacy.chemspider.com/InChI.asmx/ResolveInChIKey", data)
            h = html2text.HTML2Text()
            result = h.handle(response)
            markdown = f'''
**InChIKey to MOL**
Input InChI = {cleaned_inchikey}

**Result:**
{result}
'''
            return markdown
        else:
            return "Invalid InChIKey input."
    except Exception as e:
        logging.error(f"Error InChIKey to MOL: {e}")


# InChIToSMILES
def inchi_to_smiles(inchi: str) -> str:
    """
    Convert an InChI string to a SMILES string.
    Args:
        inchi: InChI string.
    Return:
        str: The Markdown content with SMILES.
    """
    try:
        cleaned_inchi = inchi.replace('\n', '').replace(' ', '')
        if cleaned_inchi.startswith("InChI="):
            # The string already has an InChI value starting with "InChI=" and will not be changed
            processed_inchi = cleaned_inchi
        else:
            # add "InChI="
            processed_inchi = "InChI=" + cleaned_inchi
        data ={
            "inchi": processed_inchi,
        }
        response = send_chemspider_request("http://legacy.chemspider.com/InChI.asmx/InChIToSMILES", data)
        h = html2text.HTML2Text()
        result = h.handle(response)
        markdown = f'''
**InChI to SMILES**
{processed_inchi}
**SMILES:**
{result}
'''
        return markdown
    except Exception as e:
        return f"Tool function execution error, Error InChI to SMILES: {e}"

def inchi_to_inchikey(inchi: str) -> str:
    """
    Convert an InChI string to an InChIKey string.
    Args:
        inchi: InChI string.
    Return:
        str: The Markdown content with InChIKey.
    """
    try:
        cleaned_inchi = inchi.replace('\n', '').replace(' ', '')
        data ={
            "inchi": cleaned_inchi
        }
        response = send_chemspider_request("http://legacy.chemspider.com/InChI.asmx/InChIToInChIKey", data)
        h = html2text.HTML2Text()
        result = h.handle(response)
        markdown = f'''
**InChI to InChIKey**
Input: {cleaned_inchi}
**Reuslt**
{result}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error InChI to InChIKey: {e}")


# InChIToCSID
def inchi_to_csid(inchi: str) -> str:
    """
    Convert InChI to ChemSpider ID.
    Args:
        inchi: InChI string.
    Return:
        str: The Markdown content with CSID.
    """
    try:
        cleaned_inchi = inchi.replace('\n', '').replace(' ', '')
        data = {
            "inchi": cleaned_inchi,
        }
        response = send_chemspider_request(
            "http://legacy.chemspider.com/InChI.asmx/InChIToCSID", data)
        h = html2text.HTML2Text()
        result = h.handle(response)
        markdown = f'''
**InChI to CSID**
Input: {cleaned_inchi}
**Reuslt**
{result}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error InChI to CSID: {e}")


# SMILEStoSELFIES
def smiles_to_selfies(smiles: str) -> str:
    """
    Translates a SMILES string into its corresponding SELFIES string.
    Args:
        smiles: SMILES string.
    Return:
        str: The Markdown content with SELFIES.
    """
    try:
        cleaned_smiles = smiles.replace('\n', '').replace(' ', '')
        if is_smiles(cleaned_smiles):
            selfies = sf.encoder(cleaned_smiles)
            markdown = f'''
**SMILES to SELFIES**
Input: {cleaned_smiles}

**Reuslt**
{selfies}
'''
            return markdown
        else:
            return "Invalid SMILES input."
    except Exception as e:
        logging.error(f"Error SMILES to SELFIES: {e}")


# SELFIEStoSMILES
def selfies_to_smiles(selfies: str) -> str:
    """
    Translates a SELFIES string into its corresponding SMILES string.
    Args:
        selfies: SELFIES string.
    Return:
        str: The Markdown content with SMILES.
    """
    try:
        smiles = sf.decoder(selfies)
        markdown = f'''
**SELFIES to SMILES**
Input: {selfies}

**Reuslt**
{smiles}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error SELFIES to SMILES: {e}")


# RandomMoelcule
def generate_random_molecule(length: str) -> str:
    """
    Generates a random molecule.
    Args:
        length(int): The length of the SELFIES you want. You should only input a integer. example：‘10’
    Return:
        str: The Markdown content with SELFIES.
    """
    try:
        #Extract a number from length
        length = int(re.findall(r'\d+', length)[0])

        alphabet = sf.get_semantic_robust_alphabet()  # Gets the alphabet of robust symbols
        rnd_selfies = ''.join(random.sample(list(alphabet), length))
        rnd_smiles = sf.decoder(rnd_selfies)
        markdown = f'''
**Random SELFIES**
Input: {length}

**Reuslt**
SELFIES: {rnd_selfies}
SMILES: {rnd_smiles}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error random SELFIES: {e}")


# Length_SELFIES
def length_selfies(selfies: str) -> str:
    """
    Computes the length of a SELFIES string.
    Args:
        selfies: SELFIES string.
    Return:
        str: The Markdown content with length.
    """
    try:
        length = sf.len_selfies(selfies)
        markdown = f'''
**Length of SELFIES**
Input: {selfies}

**Reuslt**
length: {length}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error length of SELFIES: {e}")


# Split_SELFIES
def split_selfies(selfies: str) -> str:
    """
    Splits a SELFIES string into its individual tokens.
    Args:
        selfies: SELFIES string.
    Return:
        str: The Markdown content with tokens.
    """
    try:
        tokens = list(sf.split_selfies(selfies))
        markdown = f'''
**Split SELFIES**
Input: {selfies}

**Reuslt**
tokens: {tokens}
'''
        return markdown
    except Exception as e:
        logging.error(f"Error split SELFIES: {e}")



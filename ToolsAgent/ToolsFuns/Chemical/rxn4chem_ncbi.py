import logging
import time
import requests
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, rdMolDescriptors
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
import molbloom

from ToolsFuns.utils.sendRequest import send_novopro_request

from ToolsFuns.Chemical.utils import *

def query_name_to_smiles(molecule_name: str) -> str:
    """
    Query a molecule name and return its SMILES string in Markdown format.

    Args:
        molecule_name (str): The name of the molecule to query.

    Returns:
        str: A Markdown formatted string containing the molecule's SMILES and additional information.
    """
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/{}"
    try:
        response = requests.get(
            base_url.format(molecule_name, "property/SMILES/JSON"),
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        smi = data["PropertyTable"]["Properties"][0]["SMILES"]
        canonical_smiles = Chem.CanonSmiles(largest_mol(smi))
        
        markdown_result = f"""
### Molecule: {molecule_name}

#### SMILES

- **SMILES**: `{canonical_smiles}`

#### More Information

- [PubChem Compound](https://pubchem.ncbi.nlm.nih.gov/compound/{molecule_name})
"""
        return markdown_result

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error occurred: {e}")
        return "Network error occurred. Unable to process the request."

    except KeyError:
        return f"Could not find a molecule matCHing the name: {molecule_name}."

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return f"An error occurred while processing the request for: {molecule_name}."

def query_name_to_cas(molecule_name: str) -> str:
    """
    Query a molecule name and return its CAS number in Markdown format.
    """
    try:
        mode = "name"
        if is_smiles(molecule_name):
            mode = "smiles"
        url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{mode}/{molecule_name}/cids/JSON"
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
            markdown_result = f"""
### Molecule: {molecule_name}

#### CAS Number

- **CAS**: `{cas_number}`

#### More Information

- [PubChem Compound](https://pubchem.ncbi.nlm.nih.gov/compound/{cid})
"""
            return markdown_result
        else:
            return "CAS number not found."

    except (requests.exceptions.RequestException, KeyError):
        return "Invalid molecule input, no Pubchem entry."

def check_patent_status(smiles: str) -> str:
    """
    Check if a molecule (represented by SMILES) is patented, and return the result in Markdown format.
    """
    try:
        # is_patented = molbloom.buy(smiles, canonicalize=True, catalog="surechembl")
        is_patented = molbloom.buy(smiles)
        patent_status = "Patented" if is_patented else "Novel"
        markdown_result = f"""
### Molecule: {smiles}

#### Patent Status

- **Status**: `{patent_status}`

#### More Information

- [SureChEMBL](https://www.surechembl.org/search/?query={smiles})
"""
        return markdown_result

    except:
        return "Invalid SMILES string or error in patent check."
    
def predict_reaction(reactants: str) -> str:
    """
    Predict the outcome of a chemical reaction and return the result in Markdown format.
    Args:
        reactants (str): The SMILES string of the reactants separated by a dot '.'.
    Returns:
        str: A Markdown formatted string containing the reaction prediction.
    """
    if not is_smiles(reactants):
        return "Incorrect input."

    while True:
        time.sleep(2)
        response = rxn4chem.predict_reaction(reactants)
        if "prediction_id" in response.keys():
            break
    while True:
        time.sleep(2)

        results = rxn4chem.get_predict_reaction_results(
            response["prediction_id"]
        )
        if "payload" in results["response"].keys():
            break

    res_dict = results["response"]["payload"]["attempts"][0]
    product = res_dict["productMolecule"]["smiles"]

    markdown_result = f"""
### Reaction Prediction

#### Reactants

- **Reactants**: `{reactants}`

#### Predicted Product

- **Product**: `{product}`

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
    return markdown_result
        
def predict_retrosynthetic_pathway(product: str) -> str:
    """
    Predicts a retrosynthetic pathway for a given product SMILES and returns the first predicted pathway in Markdown format.
    Args:
        product (str): The SMILES string of the product.
    Returns:
        str: A Markdown formatted string containing the first retrosynthetic pathway.
    """
    

    response = rxn4chem.predict_automatic_retrosynthesis(product)
    results = rxn4chem.get_predict_automatic_retrosynthesis_results(
        response['prediction_id']
    )
    if results['status'] == 'SUCCESS':
        path = results['retrosynthetic_paths'][0]
        markdown_result = f"""
### Retrosynthetic Pathway Prediction

#### Product

- **Product**: `{product}`

#### Path

- **Path ID**: `{path['sequenceId']}`

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
        return markdown_result
    else:
        return "Prediction failed."

def predict_reaction_properties(reactions: list) -> str:
    """
    Predicts reaction properties such as atom-to-atom mapping and reaction yield based on the provided model.
    Args:
        reactions (list): A list of reaction SMILES strings.
        ai_model (str): Model identifier, e.g., 'atom-mapping-2020' or 'yield-2020-08-10'.
    Returns:
        str: A Markdown formatted string containing predicted properties.
    """
    response = rxn4chem.predict_reaction_properties(
        reactions=reactions,
        ai_model="atom-mapping-2020"
    )
    properties = []
    for item in response["response"]["payload"]["content"]:
        properties.append(f"- **Property**: `{item['value']}`")

    markdown_result = f"""
### Reaction Properties Prediction

#### Reactions

- **Reactions**: `{', '.join(reactions)}`

#### Predicted Properties

{chr(10).join(properties)}

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
    return markdown_result

def create_and_start_synthesis(sequence_id: str) -> str:
    """
    Creates a synthesis from a given sequence ID and starts it, returning the status and the synthesis plan.
    Args:
        sequence_id (str): The sequence ID from a retrosynthetic path.
    Returns:
        str: A Markdown formatted string containing the synthesis status and plan.
    """

    response = rxn4chem.create_synthesis_from_sequence(sequence_id)
    synthesis_id = response['synthesis_id']
    synthesis_tree, ordered_tree_nodes, ordered_list_of_actions = rxn4chem.get_synthesis_plan(synthesis_id)
    actions = [f"- **Action**: `{action}`" for action in ordered_list_of_actions]
    status = rxn4chem.start_synthesis(synthesis_id)

    markdown_result = f"""
### Synthesis Creation and Start

#### Sequence ID

- **Sequence ID**: `{sequence_id}`

#### Synthesis Actions

{chr(10).join(actions)}

#### Synthesis Status

- **Status**: `{status['status']}`

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
    return markdown_result


def calculate_molecule_similarity(smiles_pair: str) -> str:
    """
    Calculate the Tanimoto similarity between two molecules given their SMILES strings.
    
    Args:
        smiles_pair (str): Two SMILES strings separated by a dot '.'.

    Returns:
        str: A Markdown formatted string containing the similarity result.
    """
    smi_list = smiles_pair.split(".")
    if len(smi_list) != 2:
        return "Input error, please input two smiles strings separated by '.'"
    else:
        smiles1, smiles2 = smi_list

    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        similarity = DataStructs.TanimotoSimilarity(fp1, fp2)

        sim_score = {
            0.9: "very similar",
            0.8: "similar",
            0.7: "somewhat similar",
            0.6: "not very similar",
            0: "not similar",
        }
        if similarity == 1:
            return "Error: Input Molecules Are Identical"
        else:
            val = sim_score[
                max(key for key in sim_score.keys() if key <= round(similarity, 1))
            ]
            message = f"The Tanimoto similarity between {smiles1} and {smiles2} is {round(similarity, 4)},\
            indicating that the two molecules are {val}."

        markdown_result = f"""
### Molecule Similarity

#### Input Molecules

- **SMILES 1**: `{smiles1}`
- **SMILES 2**: `{smiles2}`

#### Similarity Result

- **Tanimoto Similarity**: `{round(similarity, 4)}`
- **Interpretation**: {val}

"""
        return markdown_result
    except (TypeError, ValueError, AttributeError) as e:
        return "Error: Not a valid SMILES string"
        
def calculate_molecular_weight(smiles: str) -> str:
    """
    Calculate the molecular weight of a molecule given its SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A Markdown formatted string containing the molecular weight.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Invalid SMILES string"

    mol_weight = rdMolDescriptors.CalcExactMolWt(mol)

    markdown_result = f"""
### Molecular Weight Calculation

#### Input Molecule

- **SMILES**: `{smiles}`

#### Molecular Weight

- **Weight**: `{mol_weight:.2f} g/mol`

"""
    return markdown_result
    
def list_functional_groups(smiles: str) -> str:
    """
    Identify and list the functional groups in a molecule given its SMILES string.

    Args:
        smiles (str): The SMILES string of the molecule.

    Returns:
        str: A Markdown formatted string listing the functional groups.
    """
    #A dictionary of functional groups
    dict_fgs = {
        "furan": "o1cccc1",
        "aldehydes": " [CX3H1](=O)[#6]",
        "esters": " [#6][CX3](=O)[OX2H0][#6]",
        "ketones": " [#6][CX3](=O)[#6]",
        "amides": " C(=O)-N",
        "thiol groups": " [SH]",
        "alcohol groups": " [OH]",
        "methylamide": "*-[N;D2]-[C;D3](=O)-[C;D1;H3]",
        "carboxylic acids": "*-C(=O)[O;D1]",
        "carbonyl methylester": "*-C(=O)[O;D2]-[C;D1;H3]",
        "terminal aldehyde": "*-C(=O)-[C;D1]",
        "amide": "*-C(=O)-[N;D1]",
        "carbonyl methyl": "*-C(=O)-[C;D1;H3]",
        "isocyanate": "*-[N;D2]=[C;D2]=[O;D1]",
        "isothiocyanate": "*-[N;D2]=[C;D2]=[S;D1]",
        "nitro": "*-[N;D3](=[O;D1])[O;D1]",
        "nitroso": "*-[N;R0]=[O;D1]",
        "oximes": "*=[N;R0]-[O;D1]",
        "Imines": "*-[N;R0]=[C;D1;H2]",
        "terminal azo": "*-[N;D2]=[N;D2]-[C;D1;H3]",
        "hydrazines": "*-[N;D2]=[N;D1]",
        "diazo": "*-[N;D2]#[N;D1]",
        "cyano": "*-[C;D2]#[N;D1]",
        "primary sulfonamide": "*-[S;D4](=[O;D1])(=[O;D1])-[N;D1]",
        "methyl sulfonamide": "*-[N;D2]-[S;D4](=[O;D1])(=[O;D1])-[C;D1;H3]",
        "sulfonic acid": "*-[S;D4](=O)(=O)-[O;D1]",
        "methyl ester sulfonyl": "*-[S;D4](=O)(=O)-[O;D2]-[C;D1;H3]",
        "methyl sulfonyl": "*-[S;D4](=O)(=O)-[C;D1;H3]",
        "sulfonyl chloride": "*-[S;D4](=O)(=O)-[Cl]",
        "methyl sulfinyl": "*-[S;D3](=O)-[C;D1]",
        "methyl thio": "*-[S;D2]-[C;D1;H3]",
        "thiols": "*-[S;D1]",
        "thio carbonyls": "*=[S;D1]",
        "halogens": "*-[#9,#17,#35,#53]",
        "t-butyl": "*-[C;D4]([C;D1])([C;D1])-[C;D1]",
        "tri fluoromethyl": "*-[C;D4](F)(F)F",
        "acetylenes": "*-[C;D2]#[C;D1;H]",
        "cyclopropyl": "*-[C;D3]1-[C;D2]-[C;D2]1",
        "ethoxy": "*-[O;D2]-[C;D2]-[C;D1;H3]",
        "methoxy": "*-[O;D2]-[C;D1;H3]",
        "side-chain hydroxyls": "*-[O;D1]",
        "ketones": "*=[O;D1]",
        "primary amines": "*-[N;D1]",
        "nitriles": "*#[N;D1]",
    }

    def _is_fg_in_mol(mol_smiles, fg_smarts):
        fgmol = Chem.MolFromSmarts(fg_smarts)
        mol = Chem.MolFromSmiles(mol_smiles.strip())
        return len(Chem.Mol.GetSubstructMatches(mol, fgmol, uniquify=True)) > 0

    try:
        fgs_in_molec = [
            name
            for name, fg in dict_fgs.items()
            if _is_fg_in_mol(smiles, fg)
        ]
        if not fgs_in_molec:
            return "No functional groups identified."
        elif len(fgs_in_molec) == 1:
            fgs_list = fgs_in_molec[0]
        else:
            fgs_list = f"{', '.join(fgs_in_molec[:-1])}, and {fgs_in_molec[-1]}"

        markdown_result = f"""
### Functional Groups Analysis

#### Input Molecule

- **SMILES**: `{smiles}`

#### Identified Functional Groups

- **Functional Groups**: {fgs_list}

"""
        return markdown_result
    except Exception as e:
        return f"Error: {e}"
    

def safety_summary(cas: str) -> str:
    """
    Returns a summary of safety information for a given CAS number.The summary includes Operator safety, GHS information,Environmental risks, and Societal impact. 

    Args:
        cas (str): The CAS number of the molecule.

    Returns:
        str: A Markdown formatted string containing the safety summary.
    """
    from config import Config

    base_llm = ChatOpenAI(
        model_name=Config().MODEL_NAME,
        openai_api_base=Config().OPENAI_API_BASE,
        openai_api_key=Config().OPENAI_API_KEY,
        temperature=0
    )
    mol_safety = MoleculeSafety(llm = base_llm )

    data = mol_safety._fetch_pubchem_data(cas)
    if isinstance(data, str):
        return "Molecule not found in Pubchem."
    data = mol_safety.get_safety_summary(cas)
    prompt = PromptTemplate(
        template=safety_summary_prompt,
        input_variables=["data"]
    )
    llm_chain = LLMChain(prompt=prompt, llm=base_llm)
    summary = llm_chain.run(" ".join(data))

    markdown_result = f"""
### Safety Summary

#### CAS Number

- **CAS**: `{cas}`

#### Summary

{summary}
"""
    return markdown_result
    
def check_explosiveness(cas: str) -> str:
    """
    Checks if a molecule with the given CAS number is explosive.

    Args:
        cas_number (str): The CAS number of the molecule.

    Returns:
        str: A Markdown formatted string indicating whether the molecule is explosive.
    """
    from config import Config

    base_llm = ChatOpenAI(
        model_name=Config().MODEL_NAME,
        openai_api_base=Config().OPENAI_API_BASE,
        openai_api_key=Config().OPENAI_API_KEY,
        temperature=0
    )
    mol_safety = MoleculeSafety(llm = base_llm )

    cls = mol_safety.ghs_classification(cas)
    if cls is None:
        return "Explosive Check Error. The molecule may not be assigned a GHS rating."

    cls_lower = [c.lower() for c in cls]

    # Check if "Explosive" is in the classification
    if any("explos" in c for c in cls_lower):
        explosiveness = "The molecule is explosive"
    elif any("flammable" in c or "toxic" in c or "hazard" in c for c in cls_lower):
        explosiveness = "The molecule is not explosive but has other hazardous properties"
    else:
        explosiveness = "The molecule is not explosive"

    markdown_result = f"""
### Explosiveness Check

#### CAS Number

- **CAS**: `{cas}`

#### Result

- **Explosiveness**: {explosiveness}
"""
    return markdown_result


def smiles_to_pdb(smiles):
    """
    Convert the SMILES of the compound into 3D structures and return them in Markdown format.

    Args:
        smiles (str): The SMILES of the compound.

    Returns:
        str: The Markdown content with SMILES to 3D structures.
    """
    data = {
        "sr": "smiles2pdb",
        "sq": smiles,
        "fmt": "pdb"
    }
    data_str = send_novopro_request(data=data)
    data_list = eval(data_str)

    BASE_URL_NOVOPRO = "https://www.novopro.cn/plus/tmp/"

    generated_markdown = ""
    if data_list is not None:
        pdb_url = BASE_URL_NOVOPRO + data_list[1]
        png_url = BASE_URL_NOVOPRO + data_list[2]

        generated_markdown = f'''
**2D图**

![GIF 图片]({png_url})

[点击下载3D模型文件]({pdb_url})
'''
    return generated_markdown


def predict_retrosynthetic_pathway(product: str) -> str:
    """
    Predicts a retrosynthetic pathway for a product SMILES and returns the first pathway with detailed SMILES for each step
    Args:
        product (str): The SMILES string of the product.
    Returns:
        str: A Markdown formatted string containing the first retrosynthetic pathway and reactions details.
    """
    response = rxn4chem.predict_automatic_retrosynthesis(product)
    
    # Check whether prediction_id was obtained successfully
    if 'prediction_id' not in response:
        return "Failed to initiate retrosynthesis prediction. Response may lack 'prediction_id'."
    
    prediction_id = response['prediction_id']
    max_retries = 10  # Set a maximum number of retries to avoid infinite loops
    retries = 0

    while retries < max_retries:
        results = rxn4chem.get_predict_automatic_retrosynthesis_results(prediction_id)
        status = results.get('status', 'PENDING')

        if status == 'SUCCESS':
            if 'retrosynthetic_paths' in results and results['retrosynthetic_paths']:
                path = results['retrosynthetic_paths'][0]
                reactions = collect_reactions(path)
                reaction_details = "\n".join([f"- **Reaction**: `{reaction}`" for reaction in reactions])
                markdown_result = f"""
### Retrosynthetic Pathway Prediction

#### Product

- **Product**: `{product}`

#### Path

- **Path ID**: `{path['sequenceId']}`

#### Reactions Details

{reaction_details}

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
                return markdown_result
            else:
                return "No retrosynthetic paths found in the results."
        elif status in ['NEW', 'PENDING', 'PROCESSING']:
            time.sleep(15)  # Wait for 15 seconds before rechecking
            retries += 1
        else:
            error_message = results.get('errorMessage', 'Unknown error occurred.')
            return f"Prediction failed with status: {status}. Error message: {error_message}."

    return "Prediction process exceeded maximum retries or timed out."

def collect_reactions(tree):
    reactions = []
    if 'children' in tree and tree['children']:
        reaction_smarts = '{}>>{}'.format(
            '.'.join([node['smiles'] for node in tree['children']]),
            tree['smiles']
        )
        reactions.append(reaction_smarts)
    for node in tree['children']:
        reactions.extend(collect_reactions(node))
    return reactions

def predict_reaction_properties(reaction: str) -> str:
    """
    Predicts reaction properties such as atom-to-atom mapping and reaction yield for a single reaction SMILES string.
    Args:
        reaction (str): A reaction SMILES string.
    Returns:
        str: A Markdown formatted string containing predicted properties.
    """
    reactions = [reaction]

    response = rxn4chem.predict_reaction_properties(
        reactions=reactions,
        ai_model="atom-mapping-2020"
    )

    if response and "response" in response and "payload" in response["response"] and "content" in response["response"]["payload"]:
        properties = []
        for item in response["response"]["payload"]["content"]:
            properties.append(f"- **Property**: `{item['value']}`")

        markdown_result = f"""
### Reaction Properties Prediction

#### Reaction

- **Reaction**: `{reaction}`

#### Predicted Properties

{chr(10).join(properties)}

#### More Information

- [IBM RXN for Chemistry](https://rxn.res.ibm.com)
"""
        return markdown_result
    else:
        return "Failed to fetch reaction properties due to an invalid response."
    

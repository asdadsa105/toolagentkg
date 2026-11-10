from mp_api.client import MPRester
from emmet.core.xas import Edge, XASDoc, Type
import requests
import logging
from config import Config

api_key = Config().MP_KEY   


def search_materials_containing_elements(element):
    """
    Search for materials containing at least the specified elements. Maximum 50 results will be returned.
    Args:
        element(str): The elements contained in the material to be queried
        You should provide the elements in the form of a string and use '.' to separate them.  e.g. "Si.O"
    Returns:
        A markdown string containing the results of the query
    """
    try:
        mpr = MPRester(api_key)
        element = element.replace("\"","").replace("\'","")
        elements_list = element.split(".")
        # Query the data and save it to list docs
        docs = mpr.materials.summary.search(elements=elements_list,
                                            fields=["material_id",
                                                    "band_gap",
                                                    "volume"])

        markdown = f"""##Get results for materials containing {elements_list}:##
"""
        if not docs:
            markdown += "No materials found"
        else:
            i = 0
            for doc in docs:
                material_id = doc.material_id
                band_gap = doc.band_gap
                volume = doc.volume
                markdown += f"Material ID: {material_id}\tBand Gap: {band_gap}\tVolume: {volume}\n"
                i = i + 1
                if i == 50:
                    break
        return markdown
    except Exception as e:
        logging.error(f"Error in get_by_elements: {e}")


def search_materials_by_chemsys(chemsys: str):
    """
    Search for materials containing only specified chemsys(elements)
    Args:
        chemsys(str): The chemsys of the material. You should use '-' to separate the elements. e.g. "Si-O"
    Returns:
        A markdown string containing the results of the query
    """
    try:
        mpr = MPRester(api_key)
        chemsys = chemsys.replace("\"","").replace("\'","")
        docs = mpr.materials.summary.search(chemsys=chemsys,
                                            fields=["material_id",
                                                    "band_gap",
                                                    "volume"])
        markdown = f"""##Get results for materials with chemsys {chemsys}:##
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                material_id = doc.material_id
                band_gap = doc.band_gap
                volume = doc.volume
                markdown += f"Material ID: {material_id}\tBand Gap: {band_gap}\tVolume: {volume}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in search_materials_by_chemsys: {e}")


def get_doc_by_material_id(material_id: str):
    """
    get the detailed information of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the detailed information of the material
        """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, id = cleaned_id.split("=")
        else:
            id = cleaned_id

        id_list = [id]
        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list,
                                            fields=["material_id",
                                                    "band_gap",
                                                    "volume"])
        markdown = f"""Material ID: {id}
##Document:##
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                material_id = doc.material_id
                band_gap = doc.band_gap
                volume = doc.volume
                markdown += f"Material ID: {material_id}\tBand Gap: {band_gap}eV\tVolume: {volume}\n"
                markdown += f"---------------------------------------------------------------------\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_doc_by_material_id: {e}")


def get_formula_by_material_id(material_id: str):
    """
    Get the formula of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the formula of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, id = cleaned_id.split("=")
        else:
            id = cleaned_id

        id_list = [id]

        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list,
                                            fields=["material_id",
                                                    "formula_pretty"])
        markdown = f"""##Input Material ID: {id}
##Formula:"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                markdown += f"**Input material id:** {doc.material_id}\t\t"
                markdown += f"**Formula:** {doc.formula_pretty}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_by_material_id: {e}")


def get_material_id_by_formula(formula: str):
    """
    Get the material_id of a material by its formula
    Args:
        formula(str): The formula of the material. You should only provide one formula.
    Returns:
        A markdown string containing the material_id of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_formula:
            name, id = cleaned_formula.split("=")
        else:
            id = cleaned_formula

        formula_list = [id]

        docs = mpr.materials.summary.search(formula=formula_list,
                                            fields=["material_id"])
        markdown = f"""##Input Formula: {formula_list[0]}
##Material ID: """
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                markdown += f"{doc.material_id}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_material_id_by_formula: {e}")


def get_band_gap_by_material_id(material_id: str):
    """
    Get the band gap of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the band gap of the material
    """
    try:

        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, id = cleaned_id.split("=")
        else:
            id = cleaned_id

        id_list = [id]
        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list,
                                            fields=["material_id",
                                                    "band_gap"])
        markdown = f"""##Get Band Gap
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                material_id = doc.material_id
                band_gap = doc.band_gap
                markdown += f"**Input material id:** {material_id}\t\t"
                markdown += f"**Band gap:** {band_gap}eV\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_band_gap_by_material_id: {e}")


def get_band_gap_by_formula(formula: str):
    """
    Get the band gap of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "Al2O3.SiO2"
    Returns:
        A markdown string containing the band gap of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get Band Gap by formula
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                markdown += f"**Input formula:** {doc.composition_reduced}\t\t"
                markdown += f"**Band Gap;** {doc.band_gap}eV\n"
        return markdown
    except Exception as e:
        return f"Error in get_band_gap_by_formula: {e}"


def get_volume_by_formula(formula: str):
    """
    Get the volume of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "Al2O3.SiO2"
    Returns:
        A markdown string containing the volume of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get Volume by formula
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                markdown += f"**Input formula:** {doc.composition_reduced}\t\t"
                markdown += f"**Volume:** {doc.volume}A^3\n"
        return markdown
    except Exception as e:
        return f"Error in get_volume_by_formula: {e}"


def get_volume_by_material_id(material_id: str):
    """
    Get the volume of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should input only one material id directly without any other characters.
    Returns:
        A markdown string containing the volume of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id

        id_list = [mid]

        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get Volume by material id
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                markdown += f"**Input material id:** {doc.material_id}\t\t"
                markdown += f"**Volume:** {doc.volume}A^3\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_volume_by_material_id: {e}")


def get_density_by_material_id(material_id: str):
    """
    get the density of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the density of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id

        id_list = [mid]
        mpr = MPRester(api_key)

        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get density by material id
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                density = doc.density
                markdown += f"**Input material id:** {doc.material_id}\t\t"
                markdown += f"**Desity:** {density}g/cm^3\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_density_by_material_id: {e}")


def get_density_by_formula(formula: str):
    """
    get the density of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "Al2O3.SiO2"
    Returns:
        A markdown string containing the density of the material
    """
    try:
        mpr = MPRester(api_key)
        formula = formula.replace(" ", "").replace("\n", "")
        formula_list = formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get density by formula
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                density = (doc.density)
                markdown += f"**Input formula:**{doc.composition_reduced}\t\t"
                markdown += f"**Density:**{density}g/cm^3\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_density_by_formula: {e}")


def get_density_atomic_by_material_id(material_id: str):
    """
    Get the atomic density of a material by its material_id. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Args:
        material_id(str): The material_id of the material
    Returns:
        A markdown string containing the atomic density of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get atomic density
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                density = doc.density_atomic
                markdown += f"**Input material id:**{doc.material_id}\t\t"
                markdown += f"**Atomic density:**{density}g/cm^3\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_density_atomic_by_material_id: {e}")


def get_density_atomic_by_formula(formula: str):
    """
    Get the atomic density of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "SiO2.Al2O3"
    Returns:
        A markdown string containing the atomic density of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get atomic density
##Results"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                density = doc.density_atomic
                formula = doc.composition_reduced
                material_id = doc.material_id
                markdown += f"**Input formula:**{formula}\t**Material ID:**{material_id}\t"
                markdown += f"{density}g/cm^3\n"
        return markdown
    except Exception as e:
        return f"Error in get_density_atomic_by_formula: {e}"


def get_energy_above_hull_by_material_id(material_id: str):
    """
    Get the energy above hull of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the energy above hull of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get results for materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                energy_above_hull = doc.energy_above_hull
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Energy above hull:**{energy_above_hull}eV/atom\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_energy_above_hull_by_material_id: {e}")


def get_initial_structures_by_material_id(material_id: str):
    """
    Get the initial structures of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the initial structures of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id

        id_list = [mid]
        mpr = MPRester(api_key)

        docs = mpr.materials.search(material_ids=id_list, fields=["initial_structures"])
        markdown = f"""##Get initial structures
**Input Material ID:** {mid}
##Rsults:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                initial_structures = doc.initial_structures
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Initial structures:**{initial_structures}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_initial_structures_by_material_id: {e}")


def get_initial_structures_by_formula(formula: str):
    """
    Get the initial structures of a material by its formula
    Args:
        formula(str): The formula of the material. You should only provide one formula.
    Returns:
        A markdown string containing the initial structures of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_formula:
            name, formula = cleaned_formula.split("=")
        else:
            formula = cleaned_formula

        formula_list = [cleaned_formula]

        docs = mpr.materials.search(formula=formula_list, fields=["initial_structures"])
        markdown = f"""##Get initial structures
**Input Formula:** {formula}
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                initial_structures = doc.initial_structures
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Initial structures:**{initial_structures}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_initial_structures_by_material_id: {e}")




def search_by_band_gap(band_gap_range: str):
    """
    Search for materials with band gap equal to the specified value. Maximum 50 results will be returned.
    Args:
        band_gap_range(str): The band gap range of the material to be queried. You should provide the band gap range in the form of a string, and use 'None' to indicate no upper limit. e.g. "0.5-1.5" and "3-None"

    Returns:
        A markdown string containing the results of the query
    """
    try:
        cleaned_range = band_gap_range.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        mpr = MPRester(api_key)
        low, high = cleaned_range.split("-")
        docs = mpr.summary.search(band_gap=(float(low), float(high) if high != "None" else None),
                                  is_stable=True,
                                  fields=["material_id", "band_gap"])
        markdown = f"""##Get results for materials with band gap range: {band_gap_range}eV
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            i = 0
            for doc in docs:
                material_id = doc.material_id
                band_gap = doc.band_gap
                markdown += f"**Material ID:**{material_id}\t\t"
                markdown += f"**Band Gap:**{band_gap}eV\n"
                i = i + 1
                if i == 50:
                    break
        return markdown
    except Exception as e:
        logging.error(f"Error in search_by_band_gap: {e}")


def search_xas_by_formula(formula_absorbing_element: str):
    """
    Search for materials with XAS data. Maximum 20 results will be returned.
    Args:
        formula_absorbing_element(str): The formula of the material and absorbing element. You should only provide one formula and its absorbing element. You should use '.' to separate the formula and absorbing element. e.g. "TiO2.Ti"
    Returns:
        A markdown string containing the results of the query
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula_absorbing_element.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        formula, absorbing_element = cleaned_formula.split(".")
        xas = mpr.xas.search_xas_docs(formula=formula,
                                      absorbing_element=absorbing_element,
                                      edge=Edge.K)
        markdown = f"""##Get results for materials with XAS data
**Input Formula:** {formula}
##Results:
"""
        if not xas:
            markdown += "No materials found"
        else:
            i = 0
            for doc in xas:
                i += 1
                xas_doc = doc
                markdown_info = f"""
### XAS Document Information
**Number of Sites:** {xas_doc.nsites}
**Number of Elements:** {xas_doc.nelements}
**Reduced Composition:** {xas_doc.composition_reduced.formula}
**Pretty Formula:** {xas_doc.formula_pretty}
**Anonymous Formula:** {xas_doc.formula_anonymous}
**Chemical System:** {xas_doc.chemsys}
**Volume:** {xas_doc.volume} cubic angstroms
**Density:** {xas_doc.density} g/cm^3
**Material ID:** {xas_doc.material_id}
**Spectrum ID:** {xas_doc.spectrum_id}
**Last Updated:** {xas_doc.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
**Spectrum XLABEL:** {xas_doc.spectrum.XLABEL}
**Spectrum YLABEL:** {xas_doc.spectrum.YLABEL}
**Spectrum Type:** {xas_doc.spectrum_type.name}
**Edge:** {xas_doc.edge.name}
**Composition:** {xas_doc.composition}
--------------------------------------------------
"""
                markdown += markdown_info
                if i == 20:
                    break
        return markdown
    except Exception as e:
        logging.error(f"Error in search_xas: {e}")


def get_cbm_by_material_id(material_id: str):
    """
    Get the Conduction Band Minimum of a material by its material_id
    Args:
        material_id(str): One or several material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the CBM of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get CBM
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                cbm = doc.cbm
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**CBM:**{cbm}eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_cbm_by_material_id: {e}")


def get_cbm_by_formula(formula: str):
    """
    Get the Conduction Band Minimum of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "SiO2.Al2O3"
    Returns:
        A markdown string containing the CBM of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get CBM
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                cbm = doc.cbm
                formula = doc.composition_reduced
                material_id = doc.material_id
                markdown += f"**Input formula:**{formula}\t**Material ID:**{material_id}\t"
                markdown += f"**CBM:** {cbm}eV\n"
        return markdown
    except Exception as e:
        return f"Error in get_cbm_by_formula: {e}"


def get_energy_per_atom_by_material_id(material_id: str):
    """
    Get the energy per atom of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the energy per atom of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get results for materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                energy_per_atom = doc.energy_per_atom
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Energy per atom:**{energy_per_atom}eV/atom\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_energy_per_atom_by_material_id: {e}")


def get_energy_per_atom_by_formula(formula: str):
    """
    Get the energy per atom of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "SiO2.Al2O3"
    Returns:
        A markdown string containing the energy per atom of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get energy per atom
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                energy_per_atom = doc.energy_per_atom
                formula = doc.composition_reduced
                material_id = doc.material_id
                markdown += f"**Input formula:**{formula}\t**Material ID:**{material_id}\t"
                markdown += f"**Energy per atom:**{energy_per_atom}eV/atom\n"
        return markdown
    except Exception as e:
        return f"Error in get_energy_per_atom_by_formula: {e}"


def get_efermi_by_material_id(material_id: str):
    """
    Get the Fermi energy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the Fermi energy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get results for materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                efermi = doc.efermi
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**E_fermi energy:**{efermi}eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_efermi_by_material_id: {e}")


def get_efermi_by_formula(formula: str):
    """
    Get the Fermi energy of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "SiO2.Al2O3"
    Returns:
        A markdown string containing the Fermi energy of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get Fermi energy
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                efermi = doc.efermi
                formula = doc.composition_reduced
                material_id = doc.material_id
                markdown += f"**Input formula:**{formula}\t**Material ID:**{material_id}\t"
                markdown += f"**E_fermi energy:**{efermi}eV\n"
        return markdown
    except Exception as e:
        return f"Error in get_efermi_by_formula: {e}"


def get_vbm_by_material_id(material_id: str):
    """
    Get the Valence Band Maximum of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the VBM of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get VBM
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                vbm = doc.vbm
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**VBM:**{vbm}eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_vbm_by_material_id: {e}")


def get_vbm_by_formula(formula: str):
    """
    Get the Valence Band Maximum of a material by its formula
    Args:
        formula(str): The formula of the material. If you want to get for multiple materials, you should provide the formulas in the form of a string and use '.' to separate them.  e.g. "SiO2.Al2O3"
    Returns:
        A markdown string containing the VBM of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get VBM
##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                vbm = doc.vbm
                formula = doc.composition_reduced
                material_id = doc.material_id
                markdown += f"**Input formula:**{formula}\t**Material ID:**{material_id}\t"
                markdown += f"**VBM:**{vbm}eV\n"
        return markdown
    except Exception as e:
        return f"Error in get_vbm_by_formula: {e}"


def get_formation_energy_per_atom_by_material_id(material_id: str):
    """
    Get the formation energy per atom of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the formation energy per atom of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get the formation energy per atom of a materials:
##Results: 
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                formation_energy_per_atom = doc.formation_energy_per_atom
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\n"
                markdown += f"**Formation energy per atom:**{formation_energy_per_atom}eV/atom\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formation_energy_per_atom_by_material_id: {e}")


def get_formation_energy_Per_atom_by_formula(formula: str):
    """
    Get the formation energy per atom of a material by its formula.
    Args:
        formula(str): The formula of the material. You should provide only one formula without any other characters.
    Returns:
        A markdown string containing the formation energy per atom of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list,
                                            fields=["material_id"])
        if not docs:
            return f"Your formula is not found"
        else:
            material_id = docs[0].material_id
            id_list = material_id.split(".")
            docs = mpr.materials.summary.search(material_ids=id_list)
            markdown = f"""##Get the formation energy per atom of a materials:
##Results: 
"""
            if not docs:
                markdown += "No materials found"
            else:
                for doc in docs:
                    formation_energy_per_atom = doc.formation_energy_per_atom
                    material_id = doc.material_id
                    markdown += f"**Input material id:**{material_id}\n"
                    markdown += f"**Formation energy per atom:**{formation_energy_per_atom}eV/atom\n"
            return markdown
    except Exception as e:
        return f"Error in get_formation_energy_Per_atom_by_formula: {e}"


def get_e_total_by_material_id(material_id: str):
    """
    Get the total energy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the total energy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get total energy of materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                e_total = doc.e_total
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\n"
                markdown += f"**Total energy:**{e_total} eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_e_total_by_material_id: {e}")


def get_e_total_by_formula(formula: str):
    """
    Get the total energy of a material by its formula
    Args:
        formula(str): The formula of the material. You should provide only one formula withou any onther characters.
    Returns:
        A markdown string containing the total energy of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_formula:
            name, formula = cleaned_formula.split("=")
        else:
            formula = cleaned_formula

        formula_list = [formula]
        docs = mpr.materials.summary.search(formula=formula_list,
                                            fields=["material_id"])
        if not docs:
            return f"Your formula is not found"
        else:
            material_id = docs[0].material_id
            mpr = MPRester(api_key)
            id_list = material_id.split(".")
            docs = mpr.materials.summary.search(material_ids=id_list)
            markdown = f"""##Get total energy of materials:
**Input formula:**{formula}

##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                e_total = doc.e_total
                material_id = doc.material_id
                markdown += f"**material id:**{material_id}\n"
                markdown += f"**Total energy:**{e_total} eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_e_total_by_formula: {e}")


def get_e_ionic_by_material_id(material_id: str):
    """
    Get the ionic energy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the ionic energy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get ionic energy of materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                e_ionic = doc.e_ionic
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Ionic energy:**{e_ionic} eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_e_ionic_by_material_id: {e}")


def get_e_ionic_by_formula(formula: str):
    """
    Get the ionic energy of a material by its formula
    Args:
        formula(str): The formula of the material. You should provide only one formula without any other characters.
    Returns:
        A markdown string containing the ionic energy of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list,
                                            fields=["material_id"])
        if not docs:
            return f"Your formula is not found"
        else:
            material_id = docs[0].material_id
            mpr = MPRester(api_key)
            id_list = material_id.split(".")
            docs = mpr.materials.summary.search(material_ids=id_list)
            markdown = f"""##Get ionic energy of materials:
**Input formula:**{formula}

##Results:
"""
            if not docs:
                markdown += "No materials found"
            else:
                for doc in docs:
                    e_ionic = doc.e_ionic
                    material_id = doc.material_id
                    markdown += f"**Input material id:**{material_id}\n"
                    markdown += f"**Ionic energy:**{e_ionic} eV\n"
            return markdown
    except Exception as e:
        logging.error(f"Error in get_e_ionic_by_formula: {e}")


def get_e_electronic_by_material_id(material_id: str):
    """
    Get the electronic energy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the electronic energy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get electronic energy of materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                e_electronic = doc.e_electronic
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Electronic energy:**{e_electronic}eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_e_electronic_by_material_id: {e}")


def get_e_electronic_by_formula(formula: str):
    """
    Get the electronic energy of a material by its formula
    Args:
        formula(str): The formula of the material. You should provide only one formula without any other characters.
    Returns:
        A markdown string containing the electronic energy of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_formula:
            name, formula = cleaned_formula.split("=")
        else:
            formula = cleaned_formula

        formula_list = [formula]

        docs = mpr.materials.summary.search(formula=formula_list,
                                            fields=["material_id"])
        if not docs:
            return f"Your formula is not found"
        else:
            material_id = docs[0].material_id
            mpr = MPRester(api_key)
            id_list = material_id.split(".")

            docs = mpr.materials.summary.search(material_ids=id_list)
            markdown = f"""##Get electronic energy of materials:
**Input formula:**{formula}

##Results:
"""
            if not docs:
                markdown += "No materials found"
            else:
                for doc in docs:
                    e_electronic = doc.e_electronic
                    material_id = doc.material_id
                    markdown += f"**material id:**{material_id}\n"
                    markdown += f"**Electronic energy:**{e_electronic}eV\n"
            return markdown

    except Exception as e:
        logging.error(f"Error in get_e_electronic_by_formula: {e}")


def get_equilibrium_reaction_energy_per_atom(material_id: str):
    """
    Get the equilibrium reaction energy per atom of a material by its material_id
    Args:
        material_id(str): The material_id of the material. If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the equilibrium reaction energy per atom of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get results for materials:
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                equilibrium_reaction_energy_per_atom = doc.equilibrium_reaction_energy_per_atom
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Equilibrium reaction energy per atom:**{equilibrium_reaction_energy_per_atom}eV\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_equilibrium_reaction_energy_per_atom: {e}")


def get_formula_anonymous_by_material_id(material_id: str):
    """
    Get the anonymous formula of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the anonymous formula of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id

        id_list = [mid]
        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get anonymous formula
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                anonymous_formula = doc.formula_anonymous
                formula_pretty = doc.formula_pretty
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Formula:**{formula_pretty}\t"
                markdown += f"**Anonymous formula:**{anonymous_formula}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_anonymous_by_material_id: {e}")


def get_formula_anonymous_by_formula(formula: str):
    """
    Get the anonymous formula of a material by its formula
    Args:
        formula(str): The formula of the material. You should only provide one formula without any other characters.
    Returns:
        A markdown string containing the anonymous formula of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Get anonymous formula
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                anonymous_formula = doc.formula_anonymous
                formula_pretty = doc.formula_pretty
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Formula:**{formula_pretty}\t"
                markdown += f"**Anonymous formula:**{anonymous_formula}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_anonymous_by_formula: {e}")


def is_magnetic_by_material_id(material_id: str):
    """
    Check if a material is magnetic by its material_id
    Args:
        material_id(str): The material_id of the material.
        If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the magnetic information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Check if material is magnetic
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                is_magnetic = doc.is_magnetic
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Is magnetic:**{is_magnetic}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in is_magnetic_by_material_id: {e}")


def is_magnetic_by_formula(formula: str):
    """
    Check if a material is a metal by its formula
    Args:
        formula(str): The formula of the material. You should only provide one formula directly without any other characters.
    Returns:
        A markdown string containing the metal information of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Check if material is a metal
**Input formula:**{formula}
"""
        if not docs:
            markdown += "No materials found"
        else:
            id_list = []
            for doc in docs:
                id_list.append(doc.material_id)

            mpr = MPRester(api_key)
            docs = mpr.materials.summary.search(material_ids=id_list)

            for doc in docs:
                is_magnetic = doc.is_magnetic
                material_id = doc.material_id
                markdown += f"**material id:**{material_id}\t"
                markdown += f"**Is magnetic:**{is_magnetic}\n"

            return markdown

    except Exception as e:
        logging.error(f"Error in is_magnetic_by_formula: {e}")


def is_metal_by_material_id(material_id: str):
    """
    Check if a material is a metal by its material_id
    Args:
        material_id(str): The material_id of the material.
        If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the metal information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids = id_list)
        markdown = f"""##Check if material is a metal
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                is_metal = doc.is_metal
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Is metal:**{is_metal}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in is_metal_by_material_id: {e}")



def is_metal_by_formula(formula: str):
    """
    Check if a material is metal by its formula
    Args:
        formula(str): The formula of the material. You should only provide one formula.
        If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the metal information of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Check if material is metal
**Input formula:**{formula}

##Results
"""
        if not docs:
            markdown += "No materials found"
        else:
            id_list = []
            for doc in docs:
                id_list.append(doc.material_id)

            mpr = MPRester(api_key)
            docs = mpr.materials.summary.search(material_ids=id_list)

            for doc in docs:
                is_metal = doc.is_metal
                material_id = doc.material_id
                markdown += f"**material id:**{material_id}\t"
                markdown += f"**Is metal:**{is_metal}\n"

        return markdown

    except Exception as e:
        logging.error(f"Error in is_metal_by_formula: {e}")


def is_stable_by_material_id(material_id: str):
    """
    Check if a material is stable by its material_id
    Args:
        material_id(str): The material_id of the material.
        If you want to get for multiple materials, you should provide the material_id in the form of a string and use '.' to separate them.  e.g. "mp-1.mp-555322"
    Returns:
        A markdown string containing the stability information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        mpr = MPRester(api_key)
        id_list = cleaned_id.split(".")
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Check if material is stable
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                is_stable = doc.is_stable
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Is stable:**{is_stable}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in is_stable_by_material_id: {e}")


def is_stable_by_formula(formula: str):
    """
    Check if a material is stable by its material_id
    Args:
        formula(str): The formula of the material. You should only provide one formula directly without any other characters like "Al2O3"
    Returns:
        A markdown string containing the stability information of the material
    """
    try:
        mpr = MPRester(api_key)
        cleaned_formula = formula.replace(" ", "").replace("\n", "").replace("\"","").replace("\'","")
        formula_list = cleaned_formula.split(".")
        docs = mpr.materials.summary.search(formula=formula_list)
        markdown = f"""##Check if material is stable
**Input formula:**{formula}

##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            id_list = []
            for doc in docs:
                id_list.append(doc.material_id)

            docs = mpr.materials.summary.search(material_ids=id_list)
            if not docs:
                markdown += "No materials found"
            else:
                for doc in docs:
                    is_stable = doc.is_stable
                    material_id = doc.material_id
                    markdown += f"**Input material id:**{material_id}\t"
                    markdown += f"**Is stable:**{is_stable}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in is_stable_by_formula: {e}")


def get_num_magnetic_sites_by_material_id(material_id: str):
    """
    Get the number of magnetic sites of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the number of magnetic sites of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id

        id_list = [mid]

        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get number of magnetic sites
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                num_magnetic_sites = doc.num_magnetic_sites
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Number of magnetic sites:**{num_magnetic_sites}\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_num_magnetic_sites_by_material_id: {e}")


def get_total_magnetization_by_material_id(material_id: str):
    """
    Get the total magnetization of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the total magnetization of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id
        id_list = [mid]

        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get total magnetization
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                total_magnetization = doc.total_magnetization
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Total magnetization:** {total_magnetization}μB/f.u.\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_total_magnetization_by_material_id: {e}")


def get_total_magnetization_normalized_formula_units_by_material_id(material_id: str):
    """
    Get the total magnetization normalized to formula units of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the total magnetization normalized to formula units of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id
        id_list = [mid]

        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get total magnetization normalized to formula units
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                total_magnetization_normalized_formula_units = doc.total_magnetization_normalized_formula_units
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Total magnetization normalized to formula units:** {total_magnetization_normalized_formula_units}μ_B/f.u.\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_total_magnetization_normalized_formula_units_by_material_id: {e}")


def get_total_magnetization_normalized_vol_by_material_id(material_id: str):
    """
    Get the total magnetization normalized to volume of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the total magnetization normalized to volume of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id
        id_list = [mid]
        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)
        markdown = f"""##Get total magnetization normalized to volume
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                total_magnetization_normalized_vol = doc.total_magnetization_normalized_vol
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\n"
                markdown += f"**Total magnetization normalized to volume:** {total_magnetization_normalized_vol}μ_B/A^3\n"
        return markdown
    except Exception as e:
        logging.error(f"Error in get_total_magnetization_normalized_vol_by_material_id: {e}")


def get_uncorrected_energy_per_atom_by_material_id(material_id: str):
    """
    Get the energy per atom of a material calculated using Density Functional Theory (DFT) before corrections by its material_id.
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the uncorrected energy per atom of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, mid = cleaned_id.split("=")
        else:
            mid = cleaned_id
        id_list = [mid]
        mpr = MPRester(api_key)
        docs = mpr.materials.summary.search(material_ids=id_list)

        markdown = f"""##Get uncorrected energy per atom
##Results:
"""
        if not docs:
            markdown += "No materials found"
        else:
            for doc in docs:
                uncorrected_energy_per_atom = doc.uncorrected_energy_per_atom
                material_id = doc.material_id
                markdown += f"**Input material id:**{material_id}\t"
                markdown += f"**Uncorrected energy per atom:**{uncorrected_energy_per_atom}eV/atom\n"
        return markdown

    except Exception as e:
        logging.error(f"Error in get_uncorrected_energy_per_atom_by_material_id: {e}")


def get_eos_info_by_material_id(material_id: str):
    """
    Get the equation of state(EOS) information of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the equation of state information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")


        # 设置请求的URL
        url = 'https://api.materialsproject.org/materials/eos/'

        # 设置请求的参数
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # 设置请求的头部信息
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)

        json_data = response.json()

        # 解析基础信息
        material_id = json_data['data'][0]['material_id']
        api_version = json_data['meta']['api_version']
        time_stamp = json_data['meta']['time_stamp']

        # 准备Markdown字符串
        markdown = f"### Material Eos Data for {material_id}\n\n"
        markdown += "#### Basic Information\n"
        markdown += f"- **Material ID**: {material_id}\n"
        markdown += f"- **API Version**: {api_version}\n"
        markdown += f"- **Time Stamp**: {time_stamp}\n\n"

        # Energies
        energies = ", ".join([f"{e:.3f}" for e in json_data['data'][0]['energies']])
        markdown += "#### Energies\n```\n" + energies + "\n```\n\n"

        # 构建方程状态模型表格
        markdown += "#### Equation of State Models and Parameters\n\n"
        markdown += "| Model Name             | Volume (V0) | Bulk Modulus (B) | Shear Modulus (C) | Ground State Energy (E0) |\n"
        markdown += "|------------------------|-------------|------------------|-------------------|---------------------------|\n"

        for model_name, model_data in json_data['data'][0]['eos'].items():
            model_name_formatted = model_name.replace('_', ' ').title()
            V0 = f"{model_data['V0']:.3f}"
            B = f"{model_data['B']:.3f}"
            C = f"{model_data['C']:.3f}"
            E0 = f"{model_data['E0']:.3f}"
            markdown += f"| {model_name_formatted:<24} | {V0:>11} | {B:>16} | {C:>17} | {E0:>25} |\n"

        # Volumes
        volumes = ", ".join([f"{v:.3f}" for v in json_data['data'][0]['volumes']])
        markdown += "\n#### Volumes (Sampled)\n```\n" + volumes + "\n```\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_eos_info_by_material_id: {e}")


def get_phonon_info_by_material_id(material_id: str):
    """
    Get the phonon band structure of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the phonon band structure of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # 设置请求的URL
        url = 'https://api.materialsproject.org/materials/phonon/'

        # 设置请求的参数
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'ph_dos',
            '_all_fields': 'false'
        }

        # 设置请求的头部信息
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)
        json_data = response.json()

        data = json_data['data'][0]
        ph_dos = data['ph_dos']
        structure = ph_dos['structure']

        # 准备Markdown字符串
        markdown = "### Phonon Density of States (DOS) Data\n\n"
        markdown += "#### Basic Information\n"
        markdown += f"- **Module**: {ph_dos['@module']}\n"
        markdown += f"- **Class**: {ph_dos['@class']}\n\n"

        markdown += "#### Phonon DOS Data\n"
        markdown += "- **Densities**: \n```\n" + ", ".join([f"{d:.5e}" for d in ph_dos['densities']]) + "\n```\n"
        markdown += "- **Frequencies**: \n```\n" + ", ".join(
            [f"{f:.3f}" for f in ph_dos['frequencies']]) + "\n```\n\n"

        markdown += "#### Partial DOS\n"
        markdown += "- **PDOS**: \n```\n" + ", ".join([f"{pd:.5e}" for pd in ph_dos['pdos'][0]]) + "\n```\n\n"

        markdown += "#### Crystal Structure\n"
        markdown += f"- **Lattice Constants**: a = {structure['lattice']['a']:.3f}, b = {structure['lattice']['b']:.3f}, c = {structure['lattice']['c']:.3f}\n"
        markdown += f"- **Angles**: α = {structure['lattice']['alpha']:.2f}°, β = {structure['lattice']['beta']:.2f}°, γ = {structure['lattice']['gamma']:.2f}°\n"
        markdown += f"- **Volume**: {structure['lattice']['volume']:.3f} Å³\n\n"

        markdown += "#### Atomic Positions\n"
        for site in structure['sites']:
            species = ", ".join([f"{s['element']} ({s['occu']})" for s in site['species']])
            markdown += f"- **{site['label']}**: Position = {site['xyz']}, Species = {species}\n"

        return markdown

    except Exception as e:
        logging.error(f"Error in get_phonon_info_by_material_id: {e}")


def get_crystal_structure_by_material_id(material_id: str):
    """
    Get the crystal structure of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the crystal structure of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # 设置请求的URL
        url = 'https://api.materialsproject.org/materials/phonon/'

        # 设置请求的参数
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'ph_dos',
            '_all_fields': 'false'
        }

        # 设置请求的头部信息
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)
        json_data = response.json()

        data = json_data['data'][0]
        ph_dos = data['ph_dos']
        structure = ph_dos['structure']

        # 准备Markdown字符串
        markdown = "### Crystal Structure\n\n"
        markdown += f"#### **Material ID**: {cleaned_id}\n"

        markdown += "#### Crystal Structure\n"
        markdown += f"- **Lattice Constants**: a = {structure['lattice']['a']:.3f}, b = {structure['lattice']['b']:.3f}, c = {structure['lattice']['c']:.3f}\n"
        markdown += f"- **Angles**: α = {structure['lattice']['alpha']:.2f}°, β = {structure['lattice']['beta']:.2f}°, γ = {structure['lattice']['gamma']:.2f}°\n"
        markdown += f"- **Volume**: {structure['lattice']['volume']:.3f} Å³"

        return markdown

    except Exception as e:
        logging.error(f"Error in getting crystal structure: {e}")


def get_atomic_positions_material_id(material_id: str):
    """
    Get the atomic positions of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the atomic positions of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # 设置请求的URL
        url = 'https://api.materialsproject.org/materials/phonon/'

        # 设置请求的参数
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'ph_dos',
            '_all_fields': 'false'
        }

        # 设置请求的头部信息
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)
        json_data = response.json()

        data = json_data['data'][0]
        ph_dos = data['ph_dos']
        structure = ph_dos['structure']

        # 准备Markdown字符串
        # 准备Markdown字符串
        markdown = "### Get Atomic Positions\n\n"
        markdown += f"#### **Material ID**: {cleaned_id}\n"

        markdown += "#### Atomic Positions\n"
        for site in structure['sites']:
            species = ", ".join([f"{s['element']} ({s['occu']})" for s in site['species']])
            markdown += f"- **{site['label']}**: Position = {site['xyz']}, Species = {species}\n"

        return markdown

    except Exception as e:
        logging.error(f"Error in get_phonon_info_by_material_id: {e}")


def get_magnetism_info_by_material_id(material_id: str):
    """
    Get the magnetism information of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the magnetism information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Material Magnetism Information\n\n"

        markdown += "### Basic Information\n"
        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Pretty Formula**: {material['formula_pretty']}\n"
        markdown += f"- **Anonymous Formula**: {material['formula_anonymous']}\n"
        markdown += f"- **Chemical System**: {material['chemsys']}\n"
        markdown += f"- **Number of Sites**: {material['nsites']}\n"
        markdown += f"- **Elements**: {', '.join(material['elements'])}\n"
        markdown += f"- **Number of Elements**: {material['nelements']}\n\n"

        markdown += "### Composition\n"
        markdown += "- **Full Composition**: " + ', '.join(
            [f"{elem}: {qty}" for elem, qty in material['composition'].items()]) + "\n"
        markdown += "- **Reduced Composition**: " + ', '.join(
            [f"{elem}: {qty}" for elem, qty in material['composition_reduced'].items()]) + "\n\n"

        markdown += "### Physical Properties\n"
        markdown += f"- **Volume**: {material['volume']:.3f} Å³\n"
        markdown += f"- **Density**: {material['density']:.3f} g/cm³\n"
        markdown += f"- **Atomic Density**: {material['density_atomic']:.3f} atoms/Å³\n\n"

        markdown += "### Symmetry\n"
        symmetry = material['symmetry']
        markdown += f"- **Crystal System**: {symmetry['crystal_system']}\n"
        markdown += f"- **Space Group Symbol**: {symmetry['symbol']}\n"
        markdown += f"- **Space Group Number**: {symmetry['number']}\n"
        markdown += f"- **Point Group**: {symmetry['point_group']}\n"
        markdown += f"- **Symmetry Precision**: {symmetry['symprec']}\n\n"

        markdown += "### Metadata\n"
        builder_meta = material['builder_meta']
        markdown += f"- **Builder Metadata**:\n"
        markdown += f"  - **Emmet Version**: {builder_meta['emmet_version']}\n"
        markdown += f"  - **Pymatgen Version**: {builder_meta['pymatgen_version']}\n"
        markdown += f"  - **Database Version**: {builder_meta['database_version']}\n"
        markdown += f"  - **Build Date**: {builder_meta['build_date']}\n"
        markdown += f"- **API Version**: {data['meta']['api_version']}\n"
        markdown += f"- **Timestamp**: {data['meta']['time_stamp']}\n\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_magnetism_info_by_material_id: {e}")


def get_composition_by_material_id(material_id: str):
    """
    Get the composition of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the composition of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Material Composition Information\n\n"

        markdown += "### Basic Information\n"
        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Pretty Formula**: {material['formula_pretty']}\n"
        markdown += f"- **Anonymous Formula**: {material['formula_anonymous']}\n"
        markdown += f"- **Chemical System**: {material['chemsys']}\n"
        markdown += f"- **Number of Sites**: {material['nsites']}\n"
        markdown += f"- **Elements**: {', '.join(material['elements'])}\n"
        markdown += f"- **Number of Elements**: {material['nelements']}\n\n"

        markdown += "### Composition\n"
        markdown += "- **Full Composition**: " + ', '.join(
            [f"{elem}: {qty}" for elem, qty in material['composition'].items()]) + "\n"
        markdown += "- **Reduced Composition**: " + ', '.join(
            [f"{elem}: {qty}" for elem, qty in material['composition_reduced'].items()]) + "\n\n"

        return markdown

    except Exception as e:
        logging.error(f"Error in get_composition_by_material_id: {e}")


def get_physical_properties_by_material_id(material_id: str):
    """
    Get the physical properties of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the physical properties of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Get Material Physical Properties\n\n"

        markdown += "### Basic Information\n"
        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Pretty Formula**: {material['formula_pretty']}\n"
        markdown += f"- **Anonymous Formula**: {material['formula_anonymous']}\n"
        markdown += f"- **Chemical System**: {material['chemsys']}\n"
        markdown += f"- **Number of Sites**: {material['nsites']}\n"
        markdown += f"- **Elements**: {', '.join(material['elements'])}\n"
        markdown += f"- **Number of Elements**: {material['nelements']}\n\n"

        markdown += "### Physical Properties\n"
        markdown += f"- **Volume**: {material['volume']:.3f} Å³\n"
        markdown += f"- **Density**: {material['density']:.3f} g/cm³\n"
        markdown += f"- **Atomic Density**: {material['density_atomic']:.3f} atoms/Å³"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_physical_properties_by_material_id: {e}")


def get_nsites_by_material_id(material_id: str):
    """
    Get the number of sites of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the number of sites of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Get  Number of Sites bv Material ID\n\n"

        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Number of Sites**: {material['nsites']}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_physical_properties_by_material_id: {e}")


def get_elements_by_material_id(material_id: str):
    """
    Get the elements of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the elements of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Get Elements by Material ID\n\n"

        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Elements**: {', '.join(material['elements'])}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_elements_by_material_id: {e}")


def get_number_of_elements_by_material_id(material_id: str):
    """
    Get the number of elements of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the number of elements of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Define the URL for the API endpoint
        url = 'https://api.materialsproject.org/materials/magnetism/'

        # Set up the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Configure the headers with the API key for authentication
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)

        # Load the JSON data from string
        data = response.json()

        # Access the first (and only) item in the data list
        material = data['data'][0]

        # Start constructing the Markdown text
        markdown = f"## Get Number of Elements by Material ID\n\n"

        markdown += f"- **Material ID**: {material['material_id']}\n"
        markdown += f"- **Number of Elements**: {material['nelements']}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_number_of_elements_by_material_id: {e}")


def get_dielectric_by_material_id(material_id: str):
    """
    Get the dielectric information of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the dielectric information of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = 'https://api.materialsproject.org/materials/dielectric/'

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        params = {
            'material_ids': cleaned_id,
            '_skip': 0,
            '_all_fields': 'true'
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()  # 将响应的JSON内容转换为Python字典

        # Extracting the data
        material_data = data['data'][0]
        meta_data = data['meta']

        # Markdown header
        markdown = "## Get Dielectric Properties\n\n"

        # Metadata
        markdown += "### Metadata\n"
        for key, value in meta_data.items():
            markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        # Material Data
        markdown += f"- **Material ID**: {material_data['material_id']}\n"

        # Dielectric Properties
        markdown += "\n### Dielectric Properties\n"
        markdown += f"- **Property Name**: {material_data['property_name']}\n"
        markdown += f"- **Total Dielectric Constant**: {material_data['e_total']:.3f}\n"
        markdown += f"- **Ionic Dielectric Constant**: {material_data['e_ionic']:e}\n"
        markdown += f"- **Electronic Dielectric Constant**: {material_data['e_electronic']:.3f}\n"

        # Print the full Markdown text
        return markdown
    except Exception as e:
        logging.error(f"Error in get_dielectric_by_material_id: {e}")


def get_crystal_system_by_material_id(material_id: str):
    """
    Get the crystal system of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the crystal system of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        # Set the endpoint URL
        url = 'https://api.materialsproject.org/materials/elasticity/'

        # Define the headers to be sent in the request
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Define the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Convert the response to JSON format
        data = response.json()

        # Convert JSON string to Python dictionary

        # Extract data from the JSON structure
        material_data = data['data'][0]
        meta_data = data['meta']

        # Start building the Markdown output
        markdown = "## Crystal System\n\n"

        markdown += f"- **Material ID**: {material_data['material_id']}\n"
        markdown += f"- **Crystal System**: {material_data['symmetry']['crystal_system']}\n"

        # Add metadata information
        markdown += "\n### Metadata\n"
        for key, value in meta_data.items():
            markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_crystal_system_by_material_id: {e}")


def get_chemical_system_by_material_id(material_id: str):
    """
    Get the chemical system of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the chemical system of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/elasticity/'

        # Define the headers to be sent in the request
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Define the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Convert the response to JSON format
        data = response.json()

        # Convert JSON string to Python dictionary

        # Extract data from the JSON structure
        material_data = data['data'][0]
        meta_data = data['meta']

        # Start building the Markdown output
        markdown = "## Chemical System\n\n"

        markdown += f"- **Material ID**: {cleaned_id}\n"
        markdown += f"- **Chemical System**: {material_data['chemsys']}\n"

        # Add metadata information
        markdown += "\n### Metadata\n"
        for key, value in meta_data.items():
            markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_chemical_system_by_material_id: {e}")


def get_space_group_symbol_by_material_id(material_id: str):
    """
    Get the space group symbol of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the space group symbol of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # Set the endpoint URL
        url = 'https://api.materialsproject.org/materials/elasticity/'

        # Define the headers to be sent in the request
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Define the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Convert the response to JSON format
        data = response.json()
        # Extract data from the JSON structure
        material_data = data['data'][0]
        meta_data = data['meta']

        # Start building the Markdown output
        markdown = "## Material Space Group Symbol\n\n"
        markdown += f"- **Material ID**: {material_data['material_id']}\n"
        markdown += f"- **Space Group Symbol**: {material_data['symmetry']['symbol']}\n"

        # Add metadata information
        markdown += "\n### Metadata\n"
        for key, value in meta_data.items():
            markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_space_group_symbol_by_material_id: {e}")


def get_formula_pretty_by_material_id(material_id: str):
    """
    Get the pretty formula of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the pretty formula of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # Set the endpoint URL
        url = 'https://api.materialsproject.org/materials/elasticity/'

        # Define the headers to be sent in the request
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # Define the query parameters
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_all_fields': 'true'
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)
        # Convert the response to JSON format
        data = response.json()
        # Extract data from the JSON structure
        material_data = data['data'][0]
        meta_data = data['meta']

        # Start building the Markdown output
        markdown = "## Material Pretty Formula\n\n"

        markdown += f"- **Material ID**: {material_data['material_id']}\n"
        markdown += f"- **Pretty Formula**: {material_data['formula_pretty']}\n"

        # Add metadata information
        markdown += "\n### Metadata\n"
        for key, value in meta_data.items():
            markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    except Exception as e:
        logging.error(f"Error in get_formula_pretty_by_material_id: {e}")


def get_surface_anisotropy_by_material_id(material_id: str):
    """
    Get the surface anisotropy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the surface anisotropy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/surface_properties/'
        params = {
            'material_ids': cleaned_id,
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'surface_anisotropy',
            '_all_fields': 'false'
        }

        # 设置请求头部
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)

        # 检查响应状态码并打印结果
        if response.status_code != 200:
            return f'Failed to connerct to the Materials Project API'

        data = response.json()

        # Convert the data into a markdown formatted string for easy reading
        markdown = """
## Get Surface Anisotropy

### Data
- **Input Material ID**: {cleaned_id}
- **Surface Anisotropy**: {surface_anisotropy}

### Metadata
- **API Version**: {api_version}
- **Timestamp**: {time_stamp}
- **Total Documents**: {total_doc}
- **Maximum Limit**: {max_limit}
- **Default Fields**: {default_fields}
        """.format(
            cleaned_id=cleaned_id,
            surface_anisotropy=data["data"][0]["surface_anisotropy"],
            api_version=data["meta"]["api_version"],
            time_stamp=data["meta"]["time_stamp"],
            total_doc=data["meta"]["total_doc"],
            max_limit=data["meta"]["max_limit"],
            default_fields=", ".join(data["meta"]["default_fields"])
        )

        return markdown
    except Exception as e:
        logging.error(f"Error in get_surface_anisotropy_by_material_id: {e}")


def get_structure_by_material_id(material_id: str):
    """
    Get the structure of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the structure of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = 'https://api.materialsproject.org/materials/surface_properties/'
        params = {
            'material_ids': cleaned_id,
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'structure',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return f'Failed to connerct to the Materials Project API'

        response_data = response.json()

        structure = response_data['data'][0]['structure']
        lattice = structure['lattice']
        sites = structure['sites']

        markdown = f"""
## Structure Information

- Lattice:
    - a: {lattice['a']}
    - b: {lattice['b']}
    - c: {lattice['c']}
    - alpha: {lattice['alpha']}
    - beta: {lattice['beta']}
    - gamma: {lattice['gamma']}
    - volume: {lattice['volume']}
    - matrix: {lattice['matrix']}

- Sites:
        """
        for site in sites:
            markdown += f"""
- Species: {site['species'][0]['element']}
    - abc: {site['abc']}
    - xyz: {site['xyz']}
    - label: {site['label']}
        """
        return markdown
    except Exception as e:
        logging.error(f"Error in get_structure_by_material_id: {e}")


def get_weighted_surface_energy_by_material_id(material_id: str):
    """
    Get the weighted surface energy of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the weighted surface energy of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/surface_properties/'
        params = {
            'material_ids': cleaned_id,
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'weighted_surface_energy',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return f'Failed to connerct to the Materials Project API'

        response_data = response.json()

        weighted_surface_energy = response_data['data'][0]['weighted_surface_energy']

        markdown = f"""## Weighted Surface Energy
**Input Material ID:** {cleaned_id}
**Weighted Surface Energy:** {weighted_surface_energy}
"""
        if not weighted_surface_energy:
            return "No data available for this material."

        return markdown
    except Exception as e:
        logging.error(f"Error in get_weighted_surface_energy_by_material_id: {e}")


def get_robocrystallographer_data(keywords: str):
    """
    Fetches material structure descriptions from the Materials Project Robocrystallographer API based on given keywords.

    Args:
    - keywords (str): Comma-separated keywords for searching material descriptions.

    Returns:
    - markdown: A markdown string containing 10 related materials from the API response or error information.

    """
    try:
        if "=" in keywords:
            keywords = keywords.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
            name, keywords = keywords.split("=")
        else:
            keywords = keywords.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")

        url = 'https://api.materialsproject.org/materials/robocrys/text_search/'
        params = {
            'keywords': keywords,
            '_skip': 0,
            '_limit': 10
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return f'Failed to connerct to the Materials Project API'

        data = response.json()
        markdown_content = "# Materials Description Extract\n\n## Material Information\n"

        for material in data['data']:
            markdown_content += f"### Material ID: {material['material_id']}\n"
            markdown_content += f"- **Formula**: {material['condensed_structure']['formula']}\n"
            markdown_content += f"- **Structure**: {material['description']}\n"
            markdown_content += f"- **Crystal System**: {material['condensed_structure']['crystal_system']}\n"
            markdown_content += f"- **Space Group**: {material['condensed_structure']['spg_symbol']}\n\n"

        markdown_content += "## Meta Information\n"
        markdown_content += f"- **API Version**: {data['meta']['api_version']}\n"
        markdown_content += f"- **Timestamp**: {data['meta']['time_stamp']}\n"
        markdown_content += f"- **Total Documents**: {data['meta']['total_doc']}\n"

        return markdown_content

    except Exception as e:
        logging.error(f"Error in get_robocrystallographer_data: {e}")

def get_description_by_material_id(material_id: str):
    """
    Get the description of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the description of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/robocrys/'

        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'description',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        descriptions = data['data']
        meta_info = data['meta']

        markdown = "# Description Information\n\n"
        markdown += "## Descriptions\n"
        for desc in descriptions:
            markdown += f"- **Material ID**: {cleaned_id}\n"
            markdown += f"- **Description**: {desc['description']}"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_description_by_material_id: {e}")


def get_synthesis_doc_by_keywords(keywords: str):
    """
    Fetches synthesis documents from the Materials Project Synthesis API based on given keywords.

    Args:
    - keywords (str): Comma-separated keywords for searching synthesis documents.

    Returns:
    - markdown: A markdown string containing 10 related synthesis documents from the API response or error information.

    """
    try:
        keywords = keywords.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        url = "https://api.materialsproject.org/materials/synthesis/"
        params = {
            "keywords": "graphene",
            "_skip": 0,
            "_limit": 10
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        response = response.json()
        data_entries = response['data']
        meta_info = response['meta']

        markdown = f"""
## Synthesis Information

- **API Version**: {meta_info['api_version']}
- **Timestamp**: {meta_info['time_stamp']}
- **Total Documents**: {meta_info['total_doc']}

        ### Data Entries
        """
        for entry in data_entries:
            markdown += f"""
- **DOI**: {entry['doi']}
- **Paragraph String**: {entry['paragraph_string']}
- **Synthesis Type**: {entry['synthesis_type']}
- **Reaction String**: {entry['reaction_string']}
- **Reaction**: {entry['reaction']}
- **Targets Formula**: {entry['targets_formula']}
- **Target**: {entry['target']}
- **Targets Formula_s**: {entry['targets_formula_s']}
- **Precursors Formula_s**: {entry['precursors_formula_s']}
- **Precursors**: {entry['precursors']}
- **Operations**: {entry['operations']}
- **Search Score**: {entry['search_score']}
- **Highlights**: {entry['highlights']}
- **Total Doc**: {entry['total_doc']}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_synthesis_doc_by_keywords: {e}")


def get_battery_formula_by_battery_id(battery_id: str):
    """
    Get the battery formula of a material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id directly without any other characters like'.
    Returns:
        A markdown string containing the battery formula of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "battery_formula",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        # Extract information
        battery_formula = data['data'][0]['battery_formula']
        api_version = data['meta']['api_version']
        time_stamp = data['meta']['time_stamp']

        # Markdown content initialization
        markdown_output = f"""
## Get Battery Formula
- **Input Battery ID**: {cleaned_id}
- **Battery Formula**: {battery_formula}

- **API Version**: {api_version}
- **Time Stamp**: {time_stamp}
"""
        return markdown_output
    except Exception as e:
        logging.error(f"Error in get_battery_formula_by_battery_id: {e}")


def get_working_ion_by_battery_id(battery_id: str):
    """
    Get the working ion of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the working ion of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "working_ion",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        # Extract information
        working_ion = data['data'][0]['working_ion']
        api_version = data['meta']['api_version']
        time_stamp = data['meta']['time_stamp']

        # Markdown content initialization
        markdown_output = f"""
## Get Battery Formula
- **Input Battery ID**: {cleaned_id}
- **Working ion**: {working_ion}

- **API Version**: {api_version}
- **Time Stamp**: {time_stamp}
"""
        return markdown_output
    except Exception as e:
        logging.error(f"Error in get_working_ion_by_battery_id: {e}")


def get_max_voltage_step_by_battery_id(battery_id: str):
    """
    Get the maximum voltage step of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the maximum voltage step of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")        
        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "max_voltage_step",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        # Extract information
        max_voltage_step = data['data'][0]['max_voltage_step']
        api_version = data['meta']['api_version']
        time_stamp = data['meta']['time_stamp']

        # Markdown content initialization
        markdown_output = f"""## Get maximum voltage step of a battery material
- **Input Battery ID**: {cleaned_id}
- **Max Voltage Step**: {max_voltage_step}

- **API Version**: {api_version}
- **Time Stamp**: {time_stamp}
"""
        return markdown_output
    except Exception as e:
        logging.error(f"Error in get_max_voltage_step_by_battery_id: {e}")


def get_framework_by_battery_id(battery_id: str):
    """
    Get the framework of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the framework of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "framework",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        framework = data['data'][0]['framework']

        markdown_output = f"""## Get Battery Framework
- **Input Battery ID**: {cleaned_id}
- **Framework**: {framework}
"""
        return markdown_output

    except Exception as e:
        logging.error(f"Error in get_framework_by_battery_id: {e}")


def get_framework_formula_by_battery_id(battery_id: str):
    """
    Get the framework formula of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the framework formula of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "framework_formula",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        framework_formula = data['data'][0]['framework_formula']
        markdown = f"""## Get Battery Framework Formula
- **Input Battery ID**: {cleaned_id}
- **Framework Formula**: {framework_formula}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_framework_formula_by_battery_id: {e}")


def get_elements_by_battery_id(battery_id: str):
    """
    Get the elements of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the elements of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "elements",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        elements = data['data'][0]['elements']
        markdown = f"""## Get Battery Elements
- **Input Battery ID**: {cleaned_id}
- **Elements**: {elements}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_elements_by_battery_id: {e}")


def get_nelements_by_battery_id(battery_id: str):
    """
    Get the number of elements of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the number of elements of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": "nelements",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        nelements = data['data'][0]['nelements']
        markdown = f"""## Get Number of Elements in a battery material
- **Input Battery ID**: {cleaned_id}
- **Number of Elements**: {nelements}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_nelements_by_battery_id: {e}")


def electrodes_by_battery_id(field: str, battery_id: str):
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        cleaned_field = field.replace(" ", "")

        url = "https://api.materialsproject.org/materials/insertion_electrodes/"
        params = {
            "battery_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 1,
            "_fields": cleaned_field,
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        result = data['data'][0][cleaned_field]
        markdown = f"""- **Input Battery ID**: {cleaned_id}
- **{field}**: {result}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in electrodes_by_battery_id: {e}")


def get_chemsys_by_battery_id(battery_id: str):
    """
    Get the chemical system of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the chemical system of the material
    """
    try:
        markdown = f"""## Get Chemical System of a battery material\n"""
        markdown += electrodes_by_battery_id("chemsys", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_chemsys_by_battery_id: {e}")


def get_formula_anonymous_by_battery_id(battery_id: str):
    """
    Get the anonymous formula of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the anonymous formula of the material
    """
    try:
        markdown = f"""## Get Anonymous Formula of a battery material\n"""
        markdown += electrodes_by_battery_id("formula_anonymous", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_anonymous_by_battery_id: {e}")


def get_warnings_by_battery_id(battery_id: str):
    """
    Get the warnings of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the warnings of the material
    """
    try:
        markdown = f"""## Get Warnings of a battery material\n"""
        markdown += electrodes_by_battery_id("warnings", battery_id)
        markdown += f"If there are no warnings in materials project, the field will be empty."
        return markdown
    except Exception as e:
        logging.error(f"Error in get_warnings_by_battery_id: {e}")


def get_formula_charge_by_battery_id(battery_id: str):
    """
    Get the charge formula of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the charge formula of the material
    """
    try:
        markdown = f"""## Get Charge Formula of a battery material\n"""
        markdown += electrodes_by_battery_id("formula_charge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_charge_by_battery_id: {e}")


def get_formula_discharge_by_battery_id(battery_id: str):
    """
    Get the discharge formula of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the discharge formula of the material
    """
    try:
        markdown = f"""## Get Discharge Formula of a battery material\n"""
        markdown += electrodes_by_battery_id("formula_discharge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_formula_discharge_by_battery_id: {e}")


def get_energy_volume_by_battery_id(battery_id: str):
    """
    Get the energy volume of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the energy volume of the material
    """
    try:
        markdown = f"""## Get Energy Volume of a battery material\n"""
        markdown += electrodes_by_battery_id("energy_vol", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_energy_volume_by_battery_id: {e}")


def get_max_delta_volume_battery_id(battery_id: str):
    """
    Get the maximum delta volume of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the maximum delta volume of the material
    """
    try:
        markdown = f"""## Get Maximum Delta Volume of a battery material\n"""
        markdown += electrodes_by_battery_id("max_delta_volume", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_max_delta_volume_battery_id: {e}")


def get_average_voltage_by_battery_id(battery_id: str):
    """
    Get the average voltage of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the average voltage of the material
    """
    try:
        markdown = f"""## Get Average Voltage of a battery material\n"""
        markdown += electrodes_by_battery_id("average_voltage", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_average_voltage_by_battery_id: {e}")


def get_capacity_grav_by_battery_id(battery_id: str):
    """
    Get the gravimetric capacity of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the gravimetric capacity of the material
    """
    try:
        markdown = f"""## Get Gravimetric Capacity of a battery material\n"""
        markdown += electrodes_by_battery_id("capacity_grav", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_capacity_grav_by_battery_id: {e}")


def get_capacity_vol_by_battery_id(battery_id: str):
    """
    Get the volumetric capacity of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the volumetric capacity of the material
    """
    try:
        markdown = f"""## Get Volumetric Capacity of a battery material\n"""
        markdown += electrodes_by_battery_id("capacity_vol", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_capacity_vol_by_battery_id: {e}")


def get_energy_grav_by_battery_id(battery_id: str):
    """
    Get the gravimetric energy of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the gravimetric energy of the material
    """
    try:
        markdown = f"""## Get Gravimetric Energy of a battery material\n"""
        markdown += electrodes_by_battery_id("energy_grav", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_energy_grav_by_battery_id: {e}")


def get_fracA_charge_by_battery_id(battery_id: str):
    """
    Get the charge fraction of A of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the charge fraction of A of the material
    """
    try:
        markdown = f"""## Get Charge Fraction of A of a battery material\n"""
        markdown += electrodes_by_battery_id("fracA_charge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_fracA_charge_by_battery_id: {e}")


def get_stability_charge_by_battery_id(battery_id: str):
    """
    Get the charge stability of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the charge stability of the material
    """
    try:
        markdown = f"""## Get Charge Stability of a battery material\n"""
        markdown += electrodes_by_battery_id("stability_charge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_stability_charge_by_battery_id: {e}")


def get_stability_discharge_by_battery_id(battery_id: str):
    """
    Get the discharge stability of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the discharge stability of the material
    """
    try:
        markdown = f"""## Get Discharge Stability of a battery material\n"""
        markdown += electrodes_by_battery_id("stability_discharge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_stability_discharge_by_battery_id: {e}")


def get_id_charge_by_battery_id(battery_id: str):
    """
    Get the charge id of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the charge id of the material
    """
    try:
        markdown = f"""## Get Charge ID of a battery material\n"""
        markdown += electrodes_by_battery_id("id_charge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_id_charge_by_battery_id: {e}")


def get_id_discharge_by_battery_id(battery_id: str):
    """
    Get the discharge id of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the discharge id of the material
    """
    try:
        markdown = f"""## Get Discharge ID of a battery material\n"""
        markdown += electrodes_by_battery_id("id_discharge", battery_id)
        return markdown
    except Exception as e:
        logging.error(f"Error in get_id_discharge_by_battery_id: {e}")


def get_host_structure_by_battery_id(battery_id: str):
    """
    Get the host structure of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the host structure of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/insertion_electrodes/'

        params = {
            'battery_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'host_structure',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        host_structure = data["data"][0]["host_structure"]
        lattice = host_structure["lattice"]
        sites = host_structure["sites"]

        markdown = f"# Get the host structure of a battery material\n"
        markdown += f"- **a**: {lattice['a']}\n"
        markdown += f"- **b**: {lattice['b']}\n"
        markdown += f"- **c**: {lattice['c']}\n"
        markdown += f"- **alpha**: {lattice['alpha']}\n"
        markdown += f"- **beta**: {lattice['beta']}\n"
        markdown += f"- **gamma**: {lattice['gamma']}\n"
        markdown += f"- **Volume**: {lattice['volume']} cu Å\n\n"
        markdown += "## Sites and Elements\n"

        for site in sites:
            element = site["species"][0]["element"]
            label = site["label"]
            magmom = site["properties"]["magmom"]
            xyz = site["xyz"]
            markdown += f"- **Element**: {element} ({label}), **Magnetic Moment**: {magmom}, **Coordinates (x, y, z)**: {xyz}\n"

        return markdown

    except Exception as e:
        logging.error(f"Error in get_host_structure_by_battery_id: {e}")


def get_adj_pairs_by_battery_id(battery_id: str):
    """
    Get the adj pairs of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the adj pairs of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/insertion_electrodes/'

        params = {
            'battery_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'adj_pairs',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        pairs = data["data"][0]["adj_pairs"]

        markdown = "# Battery Pairs Data\n\n"

        for i, pair in enumerate(pairs):
            markdown += f"## Pair {i + 1}\n"
            markdown += f"- **Max Delta Volume**: {pair['max_delta_volume']}\n"
            markdown += f"- **Average Voltage**: {pair['average_voltage']}\n"
            markdown += f"- **Gravimetric Capacity (mAh/g)**: {pair['capacity_grav']}\n"
            markdown += f"- **Volumetric Capacity (mAh/cm³)**: {pair['capacity_vol']}\n"
            markdown += f"- **Gravimetric Energy (Wh/kg)**: {pair['energy_grav']}\n"
            markdown += f"- **Volumetric Energy (Wh/l)**: {pair['energy_vol']}\n"
            markdown += f"- **Fraction A Charged**: {pair['fracA_charge']}\n"
            markdown += f"- **Fraction A Discharged**: {pair['fracA_discharge']}\n"
            markdown += f"- **Formula on Charging**: {pair['formula_charge']}\n"
            markdown += f"- **Formula on Discharging**: {pair['formula_discharge']}\n"
            markdown += f"- **Stability on Charging**: {pair['stability_charge']}\n"
            markdown += f"- **Stability on Discharging**: {pair['stability_discharge']}\n"
            markdown += f"- **ID on Charging**: {pair['id_charge']}\n"
            markdown += f"- **ID on Discharging**: {pair['id_discharge']}\n\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_adj_pairs_by_battery_id: {e}")


def get_material_id_by_battery_id(battery_id: str):
    """""""""
    Get the material id of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the material id of the material
    """""""""
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/insertion_electrodes/'

        params = {
            'battery_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'material_ids',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        material_id = data["data"][0]["material_ids"]

        markdown = f"""## Get Material ID of a battery material
- **Input Battery ID**: {cleaned_id}

- **Material ID**: {material_id}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_material_id_by_battery_id: {e}")


def get_entries_composition_summary_by_battery_id(battery_id: str):
    """
    Get the composition summary of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the composition summary of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/insertion_electrodes/'

        params = {
            'battery_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'entries_composition_summary',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # Extract the composition summary from the data
        composition_summary = data["data"][0]["entries_composition_summary"]

        # Start building the Markdown text
        markdown = "# Composition Summary\n\n"

        # Add formulas
        markdown += "## Formulas\n"
        for formula in composition_summary["all_formulas"]:
            markdown += f"- {formula}\n"

        # Add chemical systems
        markdown += "\n## Chemical Systems\n"
        for chemsys in composition_summary["all_chemsys"]:
            markdown += f"- {chemsys}\n"

        # Add anonymous formulas
        markdown += "\n## Anonymous Formulas\n"
        for anon_formula in composition_summary["all_formula_anonymous"]:
            markdown += f"- {anon_formula}\n"

        # Add elements
        markdown += "\n## Elements\n"
        for element in composition_summary["all_elements"]:
            markdown += f"- {element}\n"

        # Add reduced compositions
        markdown += "\n## Reduced Compositions\n"
        for element, amounts in composition_summary["all_composition_reduced"].items():
            markdown += f"- **{element}**: {', '.join(map(str, amounts))}\n"

        # Output or save the markdown text
        return markdown
    except Exception as e:
        logging.error(f"Error in get_entries_composition_summary_by_battery_id: {e}")


def get_electrode_object_by_battery_id(battery_id: str):
    """
    Get the electrode object of a battery material by its battery_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the electrode object of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/insertion_electrodes/'

        params = {
            'battery_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 100,
            '_fields': 'electrode_object',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        # Extract the electrode object data
        electrode_object = data["data"][0]["electrode_object"]
        voltage_pairs = electrode_object["voltage_pairs"]

        # Initialize the Markdown text
        markdown = "# Electrode Information\n\n"

        # Iterate through each voltage pair
        for i, pair in enumerate(voltage_pairs):
            markdown += f"## Voltage Pair {i + 1}\n"
            markdown += f"- **Voltage**: {pair['voltage']} V\n"
            markdown += f"- **Capacity (mAh)**: {pair['mAh']}\n"
            markdown += f"- **Mass on Charge (g)**: {pair['mass_charge']}\n"
            markdown += f"- **Mass on Discharge (g)**: {pair['mass_discharge']}\n"
            markdown += f"- **Volume on Charge (cm³)**: {pair['vol_charge']}\n"
            markdown += f"- **Volume on Discharge (cm³)**: {pair['vol_discharge']}\n"
            markdown += f"- **Fraction Charged**: {pair['frac_charge']}\n"
            markdown += f"- **Fraction Discharged**: {pair['frac_discharge']}\n"
            markdown += f"- **Framework Formula**: {pair['framework_formula']}\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_electrode_object_by_battery_id: {e}")


def is_deprecated(battery_id: str):
    """
    Check if a material is deprecated or not
    Args:
        battery_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the deprecation status of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "deprecated",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        deprecated = data["data"][0]["deprecated"]
        markdown = f"""## Deprecation Status of a Material
- **Input Material ID**: {cleaned_id}
- **Deprecation Status**: {deprecated}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in is_deprecated: {e}")


def get_deprecated_reasons_by_battery_id(battery_id: str):
    """
    Get the deprecation reasons of a battery material by its material_id
    Args:
        battery_id(str): The battery_id of the material. You should only provide one battery_id.
    Returns:
        A markdown string containing the deprecation reasons of the material
    """
    try:
        cleaned_id = battery_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "deprecated",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        deprecated_reasons = data["data"][0]["deprecated"]
        if not deprecated_reasons:
            markdown = f"""## Deprecation Reasons of a Material
- **Input Material ID**: {cleaned_id}
- **This material is not deprecated**
"""
        else:
            markdown = f"""## Deprecation Status of a Material
- **Input Material ID**: {cleaned_id}
- **Deprecation Status**: {deprecated_reasons}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_deprecated_reasons_by_material_id: {e}")


def get_possible_species_by_material_id(material_id: str):
    """
    Get the possible species of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the possible species of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "possible_species",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        possible_species = data["data"][0]["possible_species"]
        markdown = f"""## Possible Species of a Material
- **Input Material ID**: {cleaned_id}
- **Possible Species**: {possible_species}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_possible_species_by_material_id: {e}")


def get_possible_valences_by_material_id(material_id: str):
    """
    Get the possible valences of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the possible valences of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "possible_valences",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        possible_valences = data["data"][0]["possible_valences"]
        markdown = f"""## Possible Valences of a Material
- **Input Material ID**: {cleaned_id}
- **Possible Valences**: {possible_valences}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_possible_valences_by_material_id: {e}")


def get_average_oxidation_states_by_material_id(material_id: str):
    """
    Get the average oxidation states of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the average oxidation states of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "average_oxidation_states",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        average_oxidation_state = data["data"][0]["average_oxidation_states"]
        markdown = f"""## Average Oxidation States of a Material
- **Input Material ID**: {cleaned_id}
- **Average Oxidation States**: {average_oxidation_state}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_average_oxidation_states_by_material_id: {e}")


def get_property_name_by_material_id(material_id: str):
    """
    Get the property name of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the property name of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "property_name",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        property_name = data["data"][0]["property_name"]
        markdown = f"""## Property Name of a Material
- **Input Material ID**: {cleaned_id}
- **Property Name**: {property_name}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_property_name_by_material_id: {e}")


def get_oxidation_state_method_by_material_id(material_id: str):
    """
    Get the oxidation state method of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the method of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/oxidation_states/"
        params = {
            "material_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_fields": "method",
            "_all_fields": "false",
            "license": "BY-C"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return "Failed to retrieve data from Materials Project API"

        data = response.json()
        method = data["data"][0]["method"]
        markdown = f"""## Method of a Material
- **Input Material ID**: {cleaned_id}
- **Method**: {method}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_oxidation_state_method_by_material_id: {e}")


def get_symmetry_by_material_id(material_id: str):
    """
    Get the symmetry of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the symmetry of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/provenance/'
        params = {
            'material_ids': cleaned_id,
            'deprecated': 'false',
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'symmetry',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        # Now you can handle the response
        if response.status_code != 200:
            return 'Failed to retrieve data'

        data = response.json()

        markdown = "### Symmetry Data\n\n"
        for entry in data["data"]:
            symmetry = entry["symmetry"]
            markdown += "- **Number**: {}\n".format(symmetry.get("number", "N/A"))
            if "crystal_system" in symmetry:
                markdown += "  - **Crystal System**: {}\n".format(symmetry["crystal_system"])
                markdown += "  - **Symbol**: {}\n".format(symmetry["symbol"])
                markdown += "  - **Point Group**: {}\n".format(symmetry["point_group"])
                markdown += "  - **Symmetry Precision (symprec)**: {}\n".format(symmetry["symprec"])
                markdown += "  - **Version**: {}\n".format(symmetry["version"])
            markdown += "\n"

        return markdown
    except Exception as e:
        logging.error(f"Error in get_symmetry_by_material_id: {e}")



def get_created_time_by_material_id(material_id: str):
    """
    Get the created time of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the created time of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = 'https://api.materialsproject.org/materials/provenance/'
        params = {
            'material_ids': cleaned_id,
            'deprecated': 'false',
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'created_at',
            '_all_fields': 'false'
        }

        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_output = f"""##Created Time of a Material
- **Input Material ID**: {cleaned_id}
- **Created Time**: {data['data'][0]['created_at']}

- **Total Documents**: {data['meta']['total_doc']}
- **API Version**: {data['meta']['api_version']}
- **Timestamp**: {data['meta']['time_stamp']}
- **Maximum Limit**: {data['meta']['max_limit']}
"""
        return markdown_output

    except Exception as e:
        logging.error(f"Error in get_created_time_by_material_id: {e}")


def get_references_by_material_id(material_id: str):
    """
    Get the references of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the references of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/provenance/'
        params = {
            'material_ids': cleaned_id,
            'deprecated': 'false',
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'references',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        # Now you can handle the response
        if response.status_code != 200:
            return 'Failed to retrieve data'

        data = response.json()

        markdown = "### References Data\n\n"
        for entry in data["data"]:
            references = entry["references"]
            for reference in references:
                markdown += "- **Reference**:\n {}\n".format(reference)
            markdown += "\n"

        markdown = markdown.replace("{", "").replace("}", "").replace("\n\n", "\n")
        return markdown
    except Exception as e:
        logging.error(f"Error in get_references_by_material_id: {e}")


def get_authors_by_material_id(material_id: str):
    """
    Get the authors of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the authors of the material
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/provenance/'
        params = {
            'material_ids': cleaned_id,
            'deprecated': 'false',
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'authors',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        # Now you can handle the response
        if response.status_code != 200:
            return 'Failed to retrieve data'

        data = response.json()

        authors = data['data'][0]['authors']
        api_version = data['meta']['api_version']
        time_stamp = data['meta']['time_stamp']
        total_doc = data['meta']['total_doc']
        max_limit = data['meta']['max_limit']
        default_fields = data['meta']['default_fields']

        markdown = f"""# API Information
**Input Material ID**: {cleaned_id}
**Authors**：{', '.join([f"{author['name']} ({author['email']})" for author in authors])}

## Metadata
- API Version: {api_version}
- Timestamp: {time_stamp}
- Total Documents: {total_doc}
- Maximum Limit: {max_limit}
"""

        return markdown
    except Exception as e:
        logging.error(f"Error in get_authors_by_material_id: {e}")


def get_remarks_by_material_id(material_id):
    """""""""
    Get the remarks of a material by its material_id
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the remarks of the material
    """""""""
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = 'https://api.materialsproject.org/materials/provenance/'
        params = {
            'material_ids': cleaned_id,
            'deprecated': 'false',
            '_per_page': '100',
            '_skip': '0',
            '_limit': '100',
            '_fields': 'remarks',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)

        # Now you can handle the response
        if response.status_code != 200:
            return 'Failed to retrieve data'

        data = response.json()

        markdown = f"""## Remarks Data
**Input Material ID**: {cleaned_id}
**Remarks**: {data['data'][0]['remarks']}        
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_remarks_by_material_id: {e}")


def get_last_updated_time_by_task_id(task_id: str):
    """
    Get the last updated time of a task by its task_id
    Args:
        task_id(str): The task_id of the task. You should only provide one task_id.
    Returns:
        A markdown string containing the last updated time of the task
    """
    try:
        cleaned_id = task_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/charge_density/"
        params = {
            "task_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_all_fields": "false"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        time = data["data"][0]["last_updated"]

        markdown = f"""## Last Updated Time of a Task
- **Input Task ID**: {cleaned_id}
- **Last Updated Time**: {time}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_last_updated_time_by_task_id: {e}")


def get_fs_id_by_task_id(task_id: str):
    """""""""
    Get the fs_id of a task by its task_id
    Args:
        task_id(str): The task_id of the task. You should only provide one task_id.
    Returns:
        A markdown string containing the fs_id of the task
    """""""""
    try:
        cleaned_id = task_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = "https://api.materialsproject.org/materials/charge_density/"
        params = {
            "task_ids": cleaned_id,
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_all_fields": "true"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        fs_id = data["data"][0]["fs_id"]

        markdown = f"""## FS ID of a Task
- **Input Task ID**: {cleaned_id}
- **FS ID**: {fs_id}
"""
        return markdown
    except Exception as e:
        logging.error(f"Error in get_fs_id_by_task_id: {e}")


def get_task_id_by_fs_id(fs_id: str):
    """
    Get the task_id of a task by its fs_id
    Args:
        fs_id(str): The fs_id of the task. You should only provide one fs_id.
    Returns:
        A markdown string containing the task_id of the task
    """
    try:
        cleaned_id = fs_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = f"https://api.materialsproject.org/materials/charge_density/{cleaned_id}"

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        task_id = data["data"][0]["task_id"]

        markdown = f"""## Task ID of a Task
- **Input FS ID**: {cleaned_id}
- **Task ID**: {task_id}
"""

        return markdown
    except Exception as e:
        logging.error(f"Error in get_task_id_by_fs_id: {e}")


def get_url_by_fs_id(fs_id: str):
    """
    Get the URL of a task by its fs_id
    Args:
        fs_id(str): The fs_id of the task. You should only provide one fs_id.
    Returns:
        A markdown string containing the URL of the task
    """
    try:
        cleaned_id = fs_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        url = f"https://minio.materialsproject.org/phuck/atomate_chgcar_fs/{cleaned_id}"

        markdown = f"""## URL of a Task
- **Input FS ID**: {cleaned_id}
- **URL**: {url}
"""

        return markdown
    except Exception as e:
        logging.error(f"Error in getting URL of a fs id: {e}")


def get_alloy_pairs_by_material_id(material_id: str):
    """
    Get comprehensive information about specific alloy pairs by material id. Return up to 5 results.
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the comprehensive information about specific alloy pairs.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = 'https://api.materialsproject.org/materials/alloys/'
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 5,
            '_fields': 'alloy_pair',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        markdown_text = f"# Get Alloy Pairs Data\n**Input Material ID**:{cleaned_id}"
        for item in data['data']:
            alloy = item['alloy_pair']
            markdown_text += f"## **Alloy Pair**: {alloy['formula_a']} - {alloy['formula_b']}\n"
            markdown_text += f"- **ID A**: {alloy['id_a']}\n"
            markdown_text += f"- **ID B**: {alloy['id_b']}\n"
            markdown_text += f"- **Chemical System**: {alloy['chemsys']}\n"
            markdown_text += f"- **Pair Formula**: {alloy['pair_formula']}\n"
            markdown_text += f"- **Space Group Number A**: {alloy['spacegroup_intl_number_a']}\n"
            markdown_text += f"- **Space Group Number B**: {alloy['spacegroup_intl_number_b']}\n"
            markdown_text += "\n"
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_alloy_pairs_by_material_id: {e}")


def get_pair_id_by_material_id(material_id: str):
    """
    Get the pair_id of a pair by its material_id
    Args:
        material_id(str): The material_id of the pair. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the pair_id of the pair
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")

        url = 'https://api.materialsproject.org/materials/alloys/'
        params = {
            'material_ids': cleaned_id,
            '_per_page': 100,
            '_skip': 0,
            '_limit': 5,
            '_fields': 'pair_id',
            '_all_fields': 'false'
        }
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        markdown_text = "# Alloy Pairs List\n\n"
        for item in data['data']:
            markdown_text += f"- {item['pair_id']}\n"
        markdown_text += "\n## Metadata\n"
        markdown_text += f"- API Version: {data['meta']['api_version']}\n"
        markdown_text += f"- Timestamp: {data['meta']['time_stamp']}\n"
        markdown_text += f"- Total Documents: {data['meta']['total_doc']}\n"
        markdown_text += f"- Max Limit: {data['meta']['max_limit']}\n"
        markdown_text += f"- Default Fields: {', '.join(data['meta']['default_fields'])}\n"
        return markdown_text
    except Exception as e:
        return f"Error in get_pair_id_by_material_id: {e}"


def get_bond_info_by_material_id(material_id: str):
    """
    Get the chemical bonding information for a specified material by material id.
    Args:
        material_id(str): The material_id of the material. You should only provide one material_id directly without any other characters.
    Returns:
        A markdown string containing the bond information
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Bond Infomation\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        markdown_text += f"**Number of Sites**: {material['nsites']}\n"
        markdown_text += f"**Elements**: {', '.join(material['elements'])}\n"
        markdown_text += f"**Number of Elements**: {material['nelements']}\n"
        markdown_text += f"**Composition**: {material['composition']}\n"
        markdown_text += f"**Reduced Composition**: {material['composition_reduced']}\n"
        markdown_text += f"**Pretty Formula**: {material['formula_pretty']}\n"
        markdown_text += f"**Anonymous Formula**: {material['formula_anonymous']}\n"
        markdown_text += f"**Chemical System**: {material['chemsys']}\n"
        markdown_text += f"**Volume**: {material['volume']}\n"
        markdown_text += f"**Density**: {material['density']}\n"
        markdown_text += f"**Atomic Density**: {material['density_atomic']}\n"

        markdown_text += f"\n\n## **Crystallographic Information**:\n"
        symmetry = material['symmetry']
        markdown_text += f"- **Crystal System**: {symmetry['crystal_system']}\n"
        markdown_text += f"- **Space Group Symbol**: {symmetry['symbol']}\n"
        markdown_text += f"- **Space Group Number**: {symmetry['number']}\n"
        markdown_text += f"- **Point Group**: {symmetry['point_group']}\n"
        markdown_text += f"- **Symmetry Tolerance (symprec)**: {symmetry['symprec']} Å\n"
        markdown_text += f"- **Software Version**: {symmetry['version']}\n"

        markdown_text += f"\n\n**Property Name**: {material['property_name']}\n"
        markdown_text += f"**Deprecated**: {material['deprecated']}\n"
        markdown_text += f"**Deprecation Reasons**: {material['deprecation_reasons']}\n"
        markdown_text += f"**Origins**: {material['origins']}\n"
        markdown_text += f"**Warnings**: {material['warnings']}\n"

        structure = material['structure_graph']['structure']
        lattice = structure['lattice']
        markdown_text += f"\n\n## Structure Information\n"
        markdown_text += f"### Lattice Parameters\n"
        markdown_text += f"- a: {lattice['a']}, b: {lattice['b']}, c: {lattice['c']}\n"
        markdown_text += f"- Alpha: {lattice['alpha']}, Beta: {lattice['beta']}, Gamma: {lattice['gamma']}\n"
        markdown_text += f"- Volume: {lattice['volume']}\n"
        markdown_text += f"### Sites Information\n"
        for site in structure['sites']:
            markdown_text += f"- Element: {site['species'][0]['element']}, Position: {site['xyz']}, Label: {site['label']}\n"
        markdown_text += f"### Bonding Information\n"
        for adjacency_list in material['structure_graph']['graphs']['adjacency']:
            for bond in adjacency_list:
                markdown_text += f"- Bond from ID {bond['id']} to J-image {bond['to_jimage']} with weight {bond['weight']}\n"

        markdown_text += f"\n\n**Method**: {material['method']}\n"

        bond_data = material['bond_types']
        markdown_text += "\n\n## Bond Types\n"
        for bond_type, lengths in bond_data.items():
            average_bond_length = sum(lengths) / len(lengths)
            min_bond_length = min(lengths)
            max_bond_length = max(lengths)
            markdown_text += f"### Bond Type: {bond_type}\n"
            markdown_text += f"- Average Bond Length: {average_bond_length:.4f} Å\n"
            markdown_text += f"- Minimum Bond Length: {min_bond_length:.4f} Å\n"
            markdown_text += f"- Maximum Bond Length: {max_bond_length:.4f} Å\n"
            markdown_text += f"- All Bond Lengths: {', '.join(f'{x:.4f}' for x in lengths)} Å\n\n"

        stats = material['bond_length_stats']
        markdown_text += "\n\n## Bond Length Statistics\n"
        markdown_text += f"- Minimum Bond Length: {stats['min']:.4f} Å\n"
        markdown_text += f"- Maximum Bond Length: {stats['max']:.4f} Å\n"
        markdown_text += f"- Mean Bond Length: {stats['mean']:.4f} Å\n"
        markdown_text += f"- Variance of Bond Length: {stats['variance']:.10f}\n"
        markdown_text += f"- All Bond Lengths:{', '.join(f'{x:.4f}' for x in stats['all_weights'])} Å\n\n\n"

        markdown_text += f"**Coordination Environments**: "
        for item in material['coordination_envs']:
            markdown_text += item
            markdown_text += "  "
        markdown_text += "\n"

        markdown_text += f"**Anonymous Coordination Environments**: "
        for item in material['coordination_envs_anonymous']:
            markdown_text += item
            markdown_text += "  "
        markdown_text += "\n"

        return markdown_text
    except Exception as e:
        return f"Error in get_bond_info_by_material_id: {e}"


def get_bond_types_by_material_id(material_id: str):
    """
    Get the bond types for a given material ID.
    Args:
        material_id: The material ID to get the bond types for. You should only input one material ID.
    Returns:
        A markdown string containing the bond types for the given material ID.

    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Bond Types\n\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        bond_data = material['bond_types']
        markdown_text += "## Bond Types\n"
        for bond_type, lengths in bond_data.items():
            average_bond_length = sum(lengths) / len(lengths)
            min_bond_length = min(lengths)
            max_bond_length = max(lengths)
            markdown_text += f"### Bond Type: {bond_type}\n"
            markdown_text += f"- Average Bond Length: {average_bond_length:.4f} Å\n"
            markdown_text += f"- Minimum Bond Length: {min_bond_length:.4f} Å\n"
            markdown_text += f"- Maximum Bond Length: {max_bond_length:.4f} Å\n"
            markdown_text += f"- All Bond Lengths: {', '.join(f'{x:.4f}' for x in lengths)} Å\n\n"
        return markdown_text
    except Exception as e:
        return f"Error in get_bond_type_by_material_id: {e}"


def get_bond_length_stats_by_material_id(material_id: str):
    """
    Get the bond length statistics for a given material ID.
    Args:
        material_id: The material ID to get the bond length statistics for. You should only input one material ID.
    Returns:
        A markdown string containing the bond length statistics for the given material ID.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Bond Length Statistics\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        stats = material['bond_length_stats']
        markdown_text += "\n\n## Bond Length Statistics\n"
        markdown_text += f"- Minimum Bond Length: {stats['min']:.4f} Å\n"
        markdown_text += f"- Maximum Bond Length: {stats['max']:.4f} Å\n"
        markdown_text += f"- Mean Bond Length: {stats['mean']:.4f} Å\n"
        markdown_text += f"- Variance of Bond Length: {stats['variance']:.10f}\n"
        markdown_text += f"- All Bond Lengths:{', '.join(f'{x:.4f}' for x in stats['all_weights'])} Å\n\n\n"

        return markdown_text
    except Exception as e:
        return f"Error in get_bond_length_stats_by_material_id: {e}"


def get_coordination_envs_by_material_id(material_id: str):
    """
    Get the coordination environments for a given material ID.
    Args:
        material_id: The material ID to get the coordination environments for. You should only input one material ID.
    Returns:
        A markdown string containing the coordination environments for the given material ID.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Coordination Environments\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        markdown_text += f"**Coordination Environments**: "
        for item in material['coordination_envs']:
            markdown_text += item
            markdown_text += "  "
        markdown_text += "\n"
        return markdown_text
    except Exception as e:
        return f"Error in getting Coordination Environments: {e}"


def get_origins_by_material_id(material_id: str):
    """
    Get the coordination environments for a given material ID.
    Args:
        material_id: The material ID to get the coordination environments for. You should only input one material ID.
    Returns:
        A markdown string containing the coordination environments for the given material ID.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Origins\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        markdown_text += f"**Origins**: {material['origins']}\n"

        return markdown_text
    except Exception as e:
        return f"Error in getting bond origins: {e}"


def get_coordination_envs_anonymous_by_material_id(material_id: str):
    """
    Get the coordination environments for a given material ID.
    Args:
        material_id: The material ID to get the coordination environments for. You should only input one material ID.
    Returns:
        A markdown string containing the coordination environments for the given material ID.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Anonymous Coordination Environments\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n\n"

        markdown_text += f"**Anonymous Coordination Environments**: "
        for item in material['coordination_envs_anonymous']:
            markdown_text += item
            markdown_text += "  "
        markdown_text += "\n"

        return markdown_text
    except Exception as e:
        return f"Error in get Anonymous Coordination Environments : {e}"


def get_structure_graph_by_material_id(material_id: str):
    """
    Get the structure graph for a given material ID.
    Args:
        material_id: The material ID to get the structure graph for. You should only input one material ID.
    Returns:
        A markdown string containing the structure graph for the given material ID.
    """
    try:
        cleaned_id = material_id.replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "")
        if "=" in cleaned_id:
            name, cleaned_id = cleaned_id.split("=")
        # API URL
        url = "https://api.materialsproject.org/materials/bonds/"

        params = {
            "material_ids": cleaned_id,
            "_per_page": 100,
            "_skip": 0,
            "_limit": 100,
            "_all_fields": "true"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        markdown_text = "# Material Structure Graph\n"
        material = data['data'][0]

        markdown_text += f"**Material ID**: {material['material_id']}\n"
        markdown_text += f"**Last Updated**: {material['last_updated']}\n"

        structure = material['structure_graph']['structure']
        lattice = structure['lattice']
        markdown_text += f"\n\n## Structure Graph\n"
        markdown_text += f"### Lattice Parameters\n"
        markdown_text += f"- a: {lattice['a']}, b: {lattice['b']}, c: {lattice['c']}\n"
        markdown_text += f"- Alpha: {lattice['alpha']}, Beta: {lattice['beta']}, Gamma: {lattice['gamma']}\n"
        markdown_text += f"- Volume: {lattice['volume']}\n"
        markdown_text += f"### Sites Information\n"
        for site in structure['sites']:
            markdown_text += f"- Element: {site['species'][0]['element']}, Position: {site['xyz']}, Label: {site['label']}\n"
        markdown_text += f"### Bonding Information\n"
        for adjacency_list in material['structure_graph']['graphs']['adjacency']:
            for bond in adjacency_list:
                markdown_text += f"- Bond from ID {bond['id']} to J-image {bond['to_jimage']} with weight {bond['weight']}\n"

        return markdown_text
    except Exception as e:
        return f"Error in get structure graph: {e}"


def get_charge_by_molecule_id(molecule_id: str):
    """
    Get the charge of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the charge of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "charge",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Charge
**Input Molecule ID**: {cleaned_id}
**Charge**: {molecule['charge']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_charge_by_molecule_ids: {e}")


def get_spin_multiplicity_by_molecule_id(molecule_id: str):
    """
    Get the spin multiplicity of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the spin multiplicity of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "spin_multiplicity",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Spin Multiplicity
**Input Molecule ID**: {cleaned_id}
**Spin Multiplicity**: {molecule['spin_multiplicity']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_spin_multiplicity_by_molecule_ids: {e}")


def get_natoms_by_molecule_id(molecule_id: str):
    """
    Get the number of atoms of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the number of atoms of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "natoms",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Number of Atoms
**Input Molecule ID**: {cleaned_id}
**Number of Atoms**: {molecule['natoms']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_natoms_by_molecule_ids: {e}")


def get_elements_by_molecule_id(molecule_id: str):
    """
    Get the elements of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the elements of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "elements",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Elements
**Input Molecule ID**: {cleaned_id}
**Elements**: {', '.join(molecule['elements'])}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_elements_by_molecule_ids: {e}")


def get_nelements_by_molecule_id(molecule_id: str):
    """
    Get the number of elements of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the number of elements of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "nelements",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""##Number of Elements
**Input Molecule ID**: {cleaned_id}
**Number of Elements**: {molecule['nelements']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_nelements_by_molecule_ids: {e}")


def get_nelectrons_by_molecule_id(molecule_id: str):
    """
    Get the number of electrons of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the number of electrons of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "nelectrons",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Number of Electrons
**Input Molecule ID**: {cleaned_id}
**Number of Electrons**: {molecule['nelectrons']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_nelectrons_by_molecule_ids: {e}")


def get_composition_by_molecule_id(molecule_id: str):
    """
    Get the composition of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the composition of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "composition",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Composition
**Input Molecule ID**: {cleaned_id}
**Composition**: {molecule['composition']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_composition_by_molecule_ids: {e}")


def get_formula_alphabetical_by_molecule_id(molecule_id: str):
    """
    Get the alphabetical formula of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the alphabetical formula of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "formula_alphabetical",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": "4WOpnpLZ06KhHRFTVkoyRYKI06DGRi2K"
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Alphabetical Formula
**Input Molecule ID**: {cleaned_id}
**Alphabetical Formula**: {molecule['formula_alphabetical']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_formula_alphabetical_by_molecule_ids: {e}")


def get_formula_pretty_by_molecule_id(molecule_id: str):
    """
    Get the pretty formula of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the pretty formula of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "formula_pretty",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Pretty Formula
**Input Molecule ID**: {cleaned_id}
**Pretty Formula**: {molecule['formula_pretty']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_formula_pretty_by_molecule_ids: {e}")


def get_formula_anonymous_by_molecule_id(molecule_id: str):
    """
    Get the anonymous formula of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the anonymous formula of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "formula_anonymous",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Anonymous Formula
**Input Molecule ID**: {cleaned_id}
**Anonymous Formula**: {molecule['formula_anonymous']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_formula_anonymous_by_molecule_ids: {e}")


def get_chemsys_by_molecule_id(molecule_id: str):
    """
    Get the chemical system of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the chemical system of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "chemsys",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Chemical System
**Input Molecule ID**: {cleaned_id}
**Chemical System**: {molecule['chemsys']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_chemsys_by_molecule_ids: {e}")



def get_symmetry_by_molecule_id(molecule_id: str):
    """
    Get the symmetry of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the symmetry of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "symmetry",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Symmetry
**Input Molecule ID**: {cleaned_id}

## Symmetry Information
"""
        for key, value in molecule['symmetry'].items():
            markdown_text += f" - **{key}**: {value}"
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_symmetry_by_molecule_ids: {e}")


def get_property_name_by_molecule_id(molecule_id: str):
    """
    Get the property name of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the property name of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "property_name",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Property Name
**Input Molecule ID**: {cleaned_id}
**Property Name**: {molecule['property_name']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_property_name_by_molecule_ids: {e}")


def get_property_id_by_molecule_id(molecule_id: str):
    """
    Get the property id of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the property id of the molecule
    """
    try:
        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"","").replace("\'","")


        url = "https://api.materialsproject.org/molecules/summary/"

        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "property_id",
            "_all_fields": "false"
        }

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.get(url, params=params, headers=headers)

        data = response.json()
        molecule = data['data'][0]
        markdown_text = f"""## Molecule Property ID
**Input Molecule ID**: {cleaned_id}
**Property ID**: {molecule['property_id']}
"""
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_property_id_by_molecule_ids: {e}")


def get_molecule_summary_by_id(molecule_id: str, property_name: str):
    try:


        if "=" in molecule_id:
            ids = molecule_id.split("=")
            cleaned_id = ids[1].replace("\"", "").replace("\'", "").replace(" ", "")
        else:
            cleaned_id = molecule_id.replace(" ", "").replace("\"", "").replace("\'", "")

        url = "https://api.materialsproject.org/molecules/summary/"
        params = {
            "molecule_ids": cleaned_id,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": property_name,
            "_all_fields": "false"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        molecule = data['data'][0]
        return molecule[property_name]
    except Exception as e:
        return f"Error in get_molecule_property_by_id: {e}"


def get_deprecated_by_molecule_id(molecule_id: str):
    """
    Get the deprecated status of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the deprecated status of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "deprecated")
    markdown = f"""## Molecule Deprecated Status
**Input Molecule ID**: {molecule_id}
**Deprecated Status**: {result}
"""
    return markdown


def get_deprecation_reasons_by_molecule_id(molecule_id: str):
    """
    Get the deprecation reasons of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the deprecation reasons of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "deprecation_reasons")
    markdown = f"""## Molecule Deprecation Reasons
**Input Molecule ID**: {molecule_id}
**Deprecation Reasons**: {result}
"""
    return markdown


def get_level_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the level of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the level of theory of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "level_of_theory")
    markdown = f"""## Molecule Level of Theory
**Input Molecule ID**: {molecule_id}
**Level of Theory**: {result}
"""
    return markdown


def get_solvent_by_molecule_id(molecule_id: str):
    """
    Get the solvent of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the solvent of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "solvent")
    markdown = f"""## Molecule Solvent
**Input Molecule ID**: {molecule_id}
**Solvent**: {result}
"""
    return markdown


def get_lot_solvent_by_molecule_id(molecule_id: str):
    """
    Get the solvent lot of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the solvent lot of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "lot_solvent")
    markdown = f"""## Molecule Lot Solvent
**Input Molecule ID**: {molecule_id}
**Lot Solvent**: {result}
"""
    return markdown


def get_last_updated_time_by_molecule_id(molecule_id: str):
    """
    Get the last updated time of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the last updated time of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "last_updated")
    markdown = f"""## Molecule Last Updated Time
**Input Molecule ID**: {molecule_id}
**Last Updated Time**: {result}
"""
    return markdown


def get_warnings_by_molecule_id(molecule_id: str):
    """
    Get the warnings of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the warnings of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "warnings")
    markdown = f"""## Molecule Warnings
**Input Molecule ID**: {molecule_id}
**Warnings**: {result}
"""
    return markdown


def get_origins_by_molecule_id(molecule_id: str):
    """
    Get the origins of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the origins of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "origins")
    markdown = f"""## Molecule Origins
**Input Molecule ID**: {molecule_id}
**Origins**: {result}
"""
    return markdown


def get_molecule_id_by_formula(formula: str):
    """
    Get the molecule ID of a molecule by its formula
    Args:
        formula(str): The alphabetical formula of the molecule. You should only provide one formula. Like 'C1 Mg1 N2 O1 S1'
    Returns:
        A markdown string containing the molecule ID of the molecule
    """
    try:
        import re
        formula = formula.replace(" ", "").replace("\"", "").replace("\'", "").replace("=\n", "")
        if "=" in formula:
            name, formula = formula.split("=")

        elements = re.findall(r'([A-Z][a-z]*)(\d*)', formula)

        elements = [(element[0], int(element[1]) if element[1] else 1) for element in elements]

        elements.sort(key=lambda x: x[0])

        alphabetical_formula = ' '.join([f"{element[0]}{element[1]}" for element in elements])

        url = "https://api.materialsproject.org/molecules/summary/"
        params = {
            "formula": alphabetical_formula,
            "deprecated": "false",
            "_per_page": "100",
            "_skip": "0",
            "_limit": "100",
            "_fields": "molecule_id",
            "_all_fields": "false"
        }
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        molecule = data['data']
        markdown_text = f"""## Molecule ID of Formula
**Input Formula**: {formula}

## Molecule ID
"""
        for item in molecule:
            markdown_text += f"**Molecule ID**: {item['molecule_id']}\n"
        return markdown_text
    except Exception as e:
        logging.error(f"Error in get_molecule_id_by_formula: {e}")

def get_molecule_levels_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the molecule levels of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the molecule levels of theory of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "molecule_levels_of_theory")
    markdown = f"""## Molecule Levels of Theory
**Input Molecule ID**: {molecule_id}

##Molecule Levels of Theory
"""
    for key, value in result.items():
        markdown += f"**{key}**: {value}\n"

    return markdown


def get_species_hash_by_molecule_id(molecule_id: str):
    """
    Get the species hash of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the species hash of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "species_hash")
    markdown = f"""## Molecule Species Hash
**Input Molecule ID**: {molecule_id}
**Species Hash**: {result}
"""
    return markdown


def get_coord_hash_by_molecule_id(molecule_id: str):
    """
    Get the coord hash of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the coord hash of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "coord_hash")
    markdown = f"""## Molecule Coord Hash
**Input Molecule ID**: {molecule_id}
**Coord Hash**: {result}
"""


def get_inchi_by_molecule_id(molecule_id: str):
    """
    Get the InChI of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the InChI of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "inchi")
    markdown = f"""## Molecule InChI
**Input Molecule ID**: {molecule_id}
**InChI**: {result}
"""
    return markdown


def get_inchikey_by_molecule_id(molecule_id: str):
    """
    Get the InChIKey of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the InChIKey of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "inchi_key")
    markdown = f"""## Molecule InChIKey
**Input Molecule ID**: {molecule_id}
**InChIKey**: {result}
"""
    return markdown


def get_similar_molecules_by_molecule_id(molecule_id: str):
    """
    Get the similar molecules of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the similar molecules of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "similar_molecules")
    markdown = f"""## Similar Molecules
**Input Molecule ID**: {molecule_id}

## Similar Molecules
{result}

If the molecule has no similar molecules, the result will be empty [].
"""
    return markdown



def get_constituent_molecules_by_molecule_id(molecule_id: str):
    """
    Get the constituent molecules of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the constituent molecules of the molecule
    """
    result = get_molecule_summary_by_id(molecule_id, "constituent_molecules")
    markdown = f"""## Constituent Molecules
**Input Molecule ID**: {molecule_id}
**Constituent Molecules**: {result}
"""
    return markdown


def get_unique_calc_types_by_molecule_id(molecule_id: str):
    """
    Get the unique calculation types of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the unique calculation types of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "unique_calc_types")
        markdown = f"""## Unique Calculation Types
**Input Molecule ID**: {molecule_id}

###Unique Calculation Types
"""
        for item in result:
            markdown += item
            markdown += "\n"
        return markdown
    except Exception as e:
        return f"Error in get_unique_calc_types_by_molecule_id: {e}"


def get_unique_task_types_by_molecule_id(molecule_id: str):
    """
    Get the unique task types of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the unique task types of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "unique_task_types")
        markdown = f"""## Unique Task Types
**Input Molecule ID**: {molecule_id}

###Unique Task Types
"""
        for item in result:
            markdown += item
            markdown += "\n"
        return markdown
    except Exception as e:
        return f"Error in get_unique_task_types_by_molecule_id: {e}"


def get_unique_levels_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the unique levels of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the unique levels of theory of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "unique_levels_of_theory")
        markdown = f"""## Unique Levels of Theory
**Input Molecule ID**: {molecule_id}

###Unique Levels of Theory
"""
        for item in result:
            markdown += item
            markdown += "\n"
        return markdown
    except Exception as e:
        return f"Error in get_unique_levels_of_theory_by_molecule_id: {e}"


def get_unique_solvents_by_molecule_id(molecule_id: str):
    """
    Get the unique solvents of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the unique solvents of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "unique_solvents")
        markdown = f"""## Unique Solvents
**Input Molecule ID**: {molecule_id}

###Unique Solvents
"""
        for item in result:
            markdown += item
            markdown += "\n"
        return markdown
    except Exception as e:
        return f"Error in get_unique_solvents_by_molecule_id: {e}"


def get_unique_lot_solvents_by_molecule_id(molecule_id: str):
    """
    Get the unique lot solvents of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the unique lot solvents of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "unique_lot_solvents")
        markdown = f"""## Unique Lot Solvents
**Input Molecule ID**: {molecule_id}

###Unique Lot Solvents
"""
        for item in result:
            markdown += item
            markdown += "\n"
        return markdown
    except Exception as e:
        return f"Error in get_unique_lot_solvents_by_molecule_id: {e}"


def get_thermo_property_ids_by_moelcule_id(molecule_id: str):
    """
    Get the thermo property ids of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the thermo property ids of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "thermo_property_ids")
        markdown = f"""## Thermo Property IDs
**Input Molecule ID**: {molecule_id}

###Thermo Property IDs
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"

        return markdown
    except Exception as e:
        return f"Error in get_thermo_property_ids_by_molecule_id: {e}"


def get_thermo_levels_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the thermo levels of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the thermo levels of theory of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "thermo_levels_of_theory")
        markdown = f"""## Thermo Levels of Theory
**Input Molecule ID**: {molecule_id}

###Thermo Levels of Theory
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"

        return markdown
    except Exception as e:
        return f"Error in get_thermo_levels_of_theory_by_molecule_id: {e}"


def get_electronic_energy_by_moelcule_id(molecule_id: str):
    """
    Get the electronic energy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the electronic energy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "electronic_energy")
        markdown = f"""## Electronic Energy
**Input Molecule ID**: {molecule_id}

###Electronic Energy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_electronic_energy_by_molecule_id: {e}"


def get_zero_point_energy_by_molecule_id(molecule_id: str):
    """
    Get the zero point energy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the zero point energy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "zero_point_energy")
        markdown = f"""## Zero Point Energy
**Input Molecule ID**: {molecule_id}

###Zero Point Energy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_zero_point_energy_by_molecule_id: {e}"


def get_total_enthalpy_by_molecule_id(molecule_id: str):
    """
    Get the total enthalpy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the total enthalpy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "total_enthalpy")
        markdown = f"""## Total Enthalpy
**Input Molecule ID**: {molecule_id}

###Total Enthalpy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_total_enthalpy_by_molecule_id: {e}"


def get_total_entropy_by_molecule_id(molecule_id: str):
    """
    Get the total entropy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the total entropy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "total_entropy")
        markdown = f"""## Total Entropy
**Input Molecule ID**: {molecule_id}

###Total Entropy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_total_entropy_by_molecule_id: {e}"


def get_translational_enthalpy_by_molecule_id(molecule_id: str):
    """
    Get the translational enthalpy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the translational enthalpy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "translational_enthalpy")
        markdown = f"""## Translational Enthalpy
**Input Molecule ID**: {molecule_id}

###Translational Enthalpy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_translational_enthalpy_by_molecule_id: {e}"


def get_translational_entropy_by_molecule_id(molecule_id: str):
    """
    Get the translational entropy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the translational entropy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "translational_entropy")
        markdown = f"""## Translational Entropy
**Input Molecule ID**: {molecule_id}

###Translational Entropy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_translational_entropy_by_molecule_id: {e}"


def get_rotational_enthalpy_by_molecule_id(molecule_id: str):
    """
    Get the rotational enthalpy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the rotational enthalpy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "rotational_enthalpy")
        markdown = f"""## Rotational Enthalpy
**Input Molecule ID**: {molecule_id}

###Rotational Enthalpy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_rotational_enthalpy_by_molecule_id: {e}"


def get_rotational_entropy_by_molecule_id(molecule_id: str):
    """
    Get the rotational entropy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the rotational entropy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "rotational_entropy")
        markdown = f"""## Rotational Entropy
**Input Molecule ID**: {molecule_id}

###Rotational Entropy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_rotational_entropy_by_molecule_id: {e}"


def get_vibrational_enthalpy_by_molecule_id(molecule_id: str):
    """
    Get the vibrational enthalpy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the vibrational enthalpy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "vibrational_enthalpy")
        markdown = f"""## Vibrational Enthalpy
**Input Molecule ID**: {molecule_id}

###Vibrational Enthalpy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_vibrational_enthalpy_by_molecule_id: {e}"

def get_vibrational_entropy_by_molecule_id(molecule_id: str):
    """
    Get the vibrational entropy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the vibrational entropy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "vibrational_entropy")
        markdown = f"""## Vibrational Entropy
**Input Molecule ID**: {molecule_id}

###Vibrational Entropy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_vibrational_entropy_by_molecule_id: {e}"

def get_free_energy_by_molecule_id(molecule_id: str):
    """
    Get the free energy of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the free energy of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "free_energy")
        markdown = f"""## Free Energy
**Input Molecule ID**: {molecule_id}

###Free Energy
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_free_energy_by_molecule_id: {e}"


def get_vibration_property_ids_by_molecule_id(molecule_id: str):
    """
    Get the vibration property ids of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the vibration property ids of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "vibration_property_ids")
        markdown = f"""## Vibration Property IDs
**Input Molecule ID**: {molecule_id}

###Vibration Property IDs
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_vibration_property_ids_by_molecule_id: {e}"

def get_vibration_levels_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the vibration levels of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the vibration levels of theory of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "vibration_levels_of_theory")
        markdown = f"""## Vibration Levels of Theory
**Input Molecule ID**: {molecule_id}

###Vibration Levels of Theory
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_vibration_levels_of_theory_by_molecule_id: {e}"


def get_frequencies_by_molecule_id(molecule_id: str):
    """
    Get the frequencies of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the frequencies of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "frequencies")
        markdown = f"""## Frequencies
**Input Molecule ID**: {molecule_id}

###Frequencies
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_frequencies_by_molecule_id: {e}"


def get_frequency_modes_by_molecule_id(molecule_id: str):
    """
    Get the frequency modes of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the frequency modes of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "frequency_modes")
        markdown = f"""## Frequency Modes
**Input Molecule ID**: {molecule_id}

###Frequency Modes
"""
        for key, value in result.items():
            markdown += f"**{key}**:"
            for item in value:
                markdown += f"{item}\n"
        return markdown
    except Exception as e:
        return f"Error in get_frequency_modes_by_molecule_id: {e}"

def get_ir_intensities_by_molecule_id(molecule_id: str):
    """
    Get the ir intensities of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the ir intensities of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "ir_intensities")
        markdown = f"""## IR Intensities
**Input Molecule ID**: {molecule_id}

###IR Intensities
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_ir_intensities_by_molecule_id: {e}"



def get_ir_activities_by_molecule_id(molecule_id: str):
    """
    Get the ir activities of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the ir activities of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "ir_activities")
        markdown = f"""## IR Activities
**Input Molecule ID**: {molecule_id}

###IR Activities
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_ir_activities_by_molecule_id: {e}"


def get_orbitals_property_ids_by_molecule_id(molecule_id: str):
    """
    Get the orbitals property ids of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the orbitals property ids of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "orbitals_property_ids")
        markdown = f"""## Orbitals Property IDs
**Input Molecule ID**: {molecule_id}

###Orbitals Property IDs
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_orbitals_property_ids_by_molecule_id: {e}"

def get_orbitals_levels_of_theory_by_molecule_id(molecule_id: str):
    """
    Get the orbitals levels of theory of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the orbitals levels of theory of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "orbitals_levels_of_theory")
        markdown = f"""## Orbitals Levels of Theory
**Input Molecule ID**: {molecule_id}

###Orbitals Levels of Theory
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_orbitals_levels_of_theory_by_molecule_id: {e}"


def get_open_shell_by_molecule_id(molecule_id: str):
    """
    Get the open shell of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the open shell of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "open_shell")
        markdown = f"""## Open Shell
**Input Molecule ID**: {molecule_id}

###Open Shell Result
"""
        for key, value in result.items():
            markdown += f"**{key}**: {value}\n"
        return markdown
    except Exception as e:
        return f"Error in get_open_shell_by_molecule_id: {e}"


def get_nbo_population_by_molecule_id(molecule_id: str):
    """
    Get the Natural Bond Orbital(nbo) population of a molecule by its molecule_id
    Args:
        molecule_id(str): The molecule_id of the molecule. You should only provide one molecule_id directly.
    Returns:
        A markdown string containing the nbo population of the molecule
    """
    try:
        result = get_molecule_summary_by_id(molecule_id, "nbo_population")
        markdown_text = f"""## NBO Population
"""
        for key, value in result.items():
            markdown_text += f"##{key}\n| Atom Index | Core Electrons | Valence Electrons | Rydberg Electrons | Total Electrons |\n|---|-----------|------------|------------|-----------|\n"

            max_length = max(len(str(atom['total_electrons'])) for atom in value)
            for atom in value:
                core_electrons = f"{atom['core_electrons']:.5f}".ljust(10, ' ')
                valence_electrons = f"{atom['valence_electrons']:.5f}".ljust(10, ' ')
                rydberg_electrons = f"{atom['rydberg_electrons']:.5f}".ljust(10, ' ')
                total_electrons = f"{atom['total_electrons']:.5f}".ljust(max_length, ' ')
                markdown_text += f"| {atom['atom_index']} | {core_electrons} | {valence_electrons} | {rydberg_electrons} | {total_electrons} |\n"

        return markdown_text
    except Exception as e:
        return f"Error in get_nbo_population_by_molecule_id: {e}"

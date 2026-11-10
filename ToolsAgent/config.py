import os
from dotenv import load_dotenv
load_dotenv('example.env', override=True)

class Config:
    def __init__(self):
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        self.BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")
        self.BING_SEARCH_URL = os.getenv("BING_SEARCH_URL") 
        self.WOLFRAM_ALPHA_APPID = os.getenv("WOLFRAM_ALPHA_APPID")

        self.MP_KEY = os.getenv("MP_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.FORCEGPT_MODEL_PATH = os.getenv("FORCEGPT_MODEL_PATH")
        self.QizhiPei_MODEL_PATH = os.getenv("QizhiPei_MODEL_PATH")

        self.BASE_URL_EXPASY = "https://web.expasy.org"
        self.BASE_URL_PRABI = "https://npsa-prabi.ibcp.fr"
        self.BASE_URL_NOVOPRO = "https://www.novopro.cn/plus/tmp/"

        self.PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov"
        self.RXN4CHEM_API_KEY = os.getenv("RXN4CHEM_API_KEY")
        self.RXN4CHEM_BASE_URL = "https://rxn.res.ibm.com"
        self.RXN4CHEM_PROJECT_ID = os.getenv("RXN4CHEM_PROJECT_ID")

        self.AEOPP_EXECUTABLE = os.getenv("AEOPP_EXECUTABLE")
        self.SOLVENT_THERMAL_MODEL_PATH = os.getenv("SOLVENT_THERMAL_MODELS")

        self.CHROMA_KEY = os.getenv("CHROMA_KEY")
        
        self.UPLOAD_FILES_TYPE = ''
        self.UPLOAD_FILES_BASE_PATH = ''
        self.UPLOAD_FILES_NAMES = []


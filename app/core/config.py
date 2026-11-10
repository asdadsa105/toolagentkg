import os
from dotenv import load_dotenv
load_dotenv('example.env', override=False)
class Config:
    """
    Initialize Config object with environment variables.

    The Config object is used to store environment variables.
    """

    def __init__(self):
        """
        Initialize Config object with environment variables.

        Attributes:
            OPENAI_API_BASE (str): the base URL for the OpenAI API
            OPENAI_API_KEY (str): the API key for the OpenAI API
            DASHSCOPE_API_BASE (str): the base URL for the Dashscope API
            DASHSCOPE_API_KEY (str): the API key for the Dashscope API
            MODEL_NAME (str): the name of the model to use
            EMBEDDING_MODEL_NAME (str): the name of the embedding model to use
            DATA_FILE_PATH (str): the path to the data file
            PERSIST_DIR (str): the directory where the agent will store its knowledge graph
            TOXIN_COMPOUND (str): the name of the toxin compound
            TOXIN_PROTEIN (str): the name of the toxin protein
        """
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        self.DASHSCOPE_API_BASE = os.getenv("DASHSCOPE_API_BASE")
        self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

        self.DATA_FILE_PATH = os.getenv("DATA_FILE_PATH")
        self.PERSIST_DIR = os.getenv("PERSIST_DIR")
        self.TOXIN_COMPOUND = os.getenv("TOXIN_COMPOUND")
        self.TOXIN_PROTEIN = os.getenv("TOXIN_PROTEIN")



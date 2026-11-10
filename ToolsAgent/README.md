# ToolsAgent 

## 1. Tool Service Overview

ToolsAgent is a versatile Python project that provides a series of functional modules for biology, chemistry, materials science, and general tools. The project has a clear structure, supports extensions, and is suitable for research and development.


ToolsAgent provides tool services for SciToolAgent. It integrates over 500 tools from the fields of biology, chemistry, and materials science, including AI models, online APIs, Python packages, and other formats. These tools are packaged together and made available through a unified HTTP access interface. You can use the tools we have prepared or add custom tools of your own.

## 2. Framework

```plaintext
/ToolsAgent
├── DataFiles        # Directory for data files (e.g., cif, csv, md, pdb, pdf, sdf formats)
├── LogFiles         # Directory for log files
├── TempFiles        # Temporary files directory
├── TestCode         # Directory for test codes
├── ToolsFuns        # Core functional modules directory
├── utils            # Common utility functions directory
├── README.md        # Project overview
├── requirements.txt # Python dependencies
├── run.sh           # One-click run script
├── struct.md        # Project structure documentation
├── config.py        # Configuration file
├── example.env      # Environment variable file
└── tool_runner.py   # Tool entry point
```

## 3. Quick Start

1.  Clone the project to your local machine
    ```bash
    cd ToolsAgent
2.  Create and activate a virtual environment
    ```bash
    conda create -n ToolsAgent python=3.10
    conda activate ToolsAgent
    ```
3.  Install the project dependencies
    ```bash
    pip install -r requirements.txt
4.  Run the project
    ```bash
    bash run.sh
    ```
> For some AI model-driven tools, you also need to configure model files, paths, and environment information. You can find the corresponding tool code in `ToolsAgent/ToolsFuns` for specific modifications.

## 4. Example Usage

To access the tool services via HTTP requests, you can use the FastAPI-based service exposed by the run-func endpoint. Here’s a step-by-step guide on how to make an HTTP request to invoke a function:

### Example HTTP Request:

The `run-func` endpoint accepts POST requests and requires the following parameters:

`func_name`: The name of the function you want to run.

`func_args`: The arguments required by the function, passed as a string.

`file_path_list`: A list of file paths (optional) for files that need to be uploaded for the function.

### Request Details
```json
{
    "func_name": "function_name_here",
    "func_args": "arguments_for_function",
    "file_path_list": ["path/to/file1", "path/to/file2"]
}
```

 The default port is 60002, which can be modified in `main.py`.


### Response
```json
{
    "status_code": 200,
    "result": "function_execution_result_here"
}
```

> This project uses the FastAPI framework. You can view the API documentation at http://127.0.0.1:60002/docs

## 5. Custom Tool
You can add custom tools by following these steps:

1. Create a new tool in Python under `ToolsAgent/ToolsFuns`. You can follow the existing tools as examples. Format:
    ```python
    def custom_tool(parameter: str):
        # Your code here
        return result
    ```
2. Add the tool name to `tool_name_dict.py` and `tools_dict.py`.
3. Restart the tool service to apply the changes.


## 6. Acknowledgement

Special thanks to the developers of [FastAPI](https://github.com/fastapi/fastapi) and all the open-source scientific tools that we have integrated into this project:
### Biological Tools
- **[SynBioTools](https://synbiotools.lifesynther.com)**
- **[Neurosnap](https://neurosnap.ai/services)**
- **[IDT](https://www.idtdna.com/scitools)**
- **[CNCB](https://www.cncb.ac.cn/tools)**
- **[ESM Atlas](https://esmatlas.com)**
- **[BioPython](https://biopython.org)**
- **[HIPPIE](http://cbdm.uni-mainz.de/hippie)**
- **[PPI3D](https://bioinformatics.lt/ppi3d/start)**
- **[INGA](https://inga.bio.unipd.it)**
- **[MusiteDeep](https://www.musite.net)**
- **[ProteinForceGPT](https://huggingface.co/lamm-mit/ProteinForceGPT)**
- **[NeEMO](http://old.protein.bio.unipd.it/neemo)**

### Chemical Tools
- **[RDKit](https://www.rdkit.org)**
- **[RXN4Chemistry](https://github.com/rxn4chemistry)**
- **[ChemCrow](https://github.com/ur-whitelab/chemcrow-public)**
- **[MDAnalysis](https://github.com/MDAnalysis/mdanalysis)**

### Material Tools
- **[Materials Project](https://next-gen.materialsproject.org)**
- **[MOFDscribe](https://github.com/kjappelbaum/mofdscribe)**
- **[MOFFragmentor](https://github.com/kjappelbaum/moffragmentor)**
- **[Pymatgen](https://pymatgen.org)**
- **[ChatMOF](https://github.com/Yeonghun1675/ChatMOF)**
- **[ASE](https://wiki.fysik.dtu.dk/ase)**
- **[RASPA](https://github.com/spenser-lu/RASPA_tools)**
- **[MOFSimplify](https://github.com/hjkgrp/MOFSimplify)**

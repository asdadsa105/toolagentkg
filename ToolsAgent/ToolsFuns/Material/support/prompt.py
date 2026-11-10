
DF_PROMPT = """You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
You should make a valid python command as input. You must use print the output using the `print` function at the end.
You should use the `to_markdown` function when you print a pandas object.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Input: the valid python code only using the Pandas library
Observation: the result of python code
... (this Thought/Input/Observation can repeat N times)
Final Thought: you should think about how to answer the question based on your observation
Final Answer: the final answer to the original input question. If you can't answer the question, say `nothing`

The index of the dataframe must be be one of {df_index}. If it's not in the index you want, skip straight to Final Thought.
{information}

Begin!

Question: What is the head of df? If you extracted successfully, derive 'success' as the final answer
Thought: To get the head of a DataFrame, we can use the pandas function head(), which will return the first N rows. By default, it returns the first 5 rows.
Input: 
``` 
import pandas as pd
import json
print(df.head().to_markdown())
```
Observation: {df_head}
Final Thought: The head() function in pandas provides the first 5 rows of the DataFrame.
Final Answer: success

Question: {question}
{agent_scratchpad}
"""

PREFIX = """You act like a material scientist answering a question. Answer the following questions as best you can. You have access to the following tools:"""

FORMAT_INSTRUCTIONS = """You must not use tool `generator` when `Question` does not required to generate. 

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

SUFFIX = """Begin!

Question: What is the surface area and bandgap of ACOGEF?
Thought: I need to find the surface area of ACOGEF.
Action: search_csv
Action Input: "Search name ACOGEF and provide information on its surface area"
Observation: The surface area of material "ACOGEF" is 1138.35 m^2/g. Check to see if this answer can be you final answer, and if so, you should submit your final answer.
Thought: The search_csv tool provided the surface area of ACOGEF, but not the bandgap. I need to find the bandgap.
Action: search_csv
Action Input: "Search name ACOGEF and provide information on its bandgap"
Observation: The search_csv tool did not provide any information on the bandgap of ACOGEF. I need to find another way to obtain this information.
Thought: The search_csv tool provided the surface area of ACOGEF, but not the bandgap. I need to find the bandgap.
Action: predictor
Action Input: "Predict the bandgap of ACOGEF"
Observation: The bandgap of material "ACOGEF" is 3.41139 eV. Check to see if this answer can be you final answer, and if so, you should submit your final answer.
Thought: I now know the final answer
Final Answer: The bandgap and surface area of ACOGEF is 3.41149 eV and 1138.35 m^2/g.

Question: What is the highest bandgap MOF?
Thought: I need to find the MOF with the highest bandgap.
Action: search_csv
Action Input: "find for MOFs with highest bandgap and provide its name and bandgap"
Observation: There are no data in database
Thought: The search_csv tool did not provide any information on the bandgaps of MOFs. I need to find another way to obtain this information.
Action: predictor
Action Input: "predict the bandgaps of MOFs and find the name of MOF with highest bandgaps"
Observation: The highest bandgap MOF is ACOGEF.
Thought: I now know the final answer
Final Answer: The highest bandgap MOF is ACOGEF.

Question: {input}
Thought:{agent_scratchpad}"""

ASE_PROMPT = """You are working with a ase library in Python. The name of the object `ase.atoms` is `atoms`.
You should make a valid python command as input. You must use print the output using the `print` function at the end.

Use the following format:

Question: the input question you must answer
Material: name of material
Convert: convert material to atoms object.
Thought: you should always think about what to do
Input: the valid python code only using the ase library
Observation: the result of python code
... (this Thought/Input/Observation can repeat N times)
Final Thought: you should think about how to answer the question based on your observation
Final Answer: the final answer to the original input question. If you can't answer the question, say `nothing`


Begin!

Question: calculate the cell volume of ABAYOU
Material: ABAYOU
Convert: Convert material to atoms object. I now have to write a code using `atoms` object
Thought: To calculate the cell volume of `atoms`, I need to access the cell information of the atoms object and then use the appropriate method to calculate its volume.
Input: 
``` 
import ase
volume = atoms.get_volume()
print(volume)
```
Observation: 18921.03834202299
Final Thought: The volume of the cell associated with the ase.atoms object atoms was successfully calculated using the get_volume() method from the ASE library.
Final Answer: The cell volume of the ABAYOU is 18921.03834202299 cubic Ångströms.

Question: {question}
{agent_scratchpad}
"""

PROMPT = """You should have a plan for converting units for metal-organic frameworks. The question specifies the unit to be converted from and the desired target unit for the property. 
You need to explain the conversion process and identify any additional information required. To answer the question, you have to fill in the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Unit: unit to be converted from and the desired target unit
Equation: you should explain the conversion process
Information: you should answer the information you need in this process

You must be careful with units. The units must match the final units when they are computed.

Begin!

Question: Change the m^2/g unit for surface area to m^2/cm^3
Thought: Thought: To convert the surface area from m^2/g to m^2/cm^3, we need to convert the mass unit from grams to cubic centimeters. This requires the knowledge of the density of the metal-organic framework.
Unit: The unit to be converted from is m^2/g and the desired target unit is m^2/cm^3.
Equation: Surface area (m^2/cm^3) = Surface area (m^2/g) * Density (g/cm^3)
Information: The additional information required for this conversion is the density of the metal-organic framework in g/cm^3.

Question: Change the mol/kg unit for H2 uptake to cm^3/cm^3
Thought: To convert the H2 uptake from mol/kg to cm^3/cm^3, we need to convert the amount of substance from moles to volume and the mass from kilograms to cubic centimeters. This requires the knowledge of the molar volume of H2 at STP and the density of the metal-organic framework.
Unit: The unit to be converted from is mol/kg and the desired target unit is cm^3/cm^3.
Equation: H2 uptake (cm^3/cm^3) = H2 uptake (mol/kg) * Molar volume of H2 (cm^3/mol) * Density (kg/cm^3)
Information: The additional information required for this conversion is the molar volume of H2 at STP (which is 22.4 L/mol or 22400 cm^3/mol at standard temperature and pressure) and the density of the metal-organic framework in kg/cm^3.

Question: {question}"""


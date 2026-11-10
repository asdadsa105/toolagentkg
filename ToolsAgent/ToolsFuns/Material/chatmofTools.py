import os
import re
import copy
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import ase
import ase.io
import ase.visualize

from langchain.chains.base import Chain
from langchain.base_language import BaseLanguageModel
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_experimental.tools.python.tool import PythonAstREPLTool
# from langchain.tools.python.tool import PythonAstREPLTool

from langchain.base_language import BaseLanguageModel

from chatmof.config import config as config_default
from chatmof.llm import get_llm
from chatmof import __root_dir__ 


from .support import DF_PROMPT, ASE_PROMPT, PROMPT
from langchain_community.chat_models import ChatOpenAI
from config import Config
config_chatmof = {
    'lookup_dir': os.path.join(__root_dir__, 'database/tables/coremof.xlsx'),
    'handle_errors': True,
    'structure_dir': os.path.join(__root_dir__, 'database/structures/'),
    'max_iteration': 3,
}

def get_deepseek_llm():
    return ChatOpenAI(
        model_name=Config().MODEL_NAME,
        openai_api_base=Config().OPENAI_API_BASE,
        openai_api_key=Config().OPENAI_API_KEY,
        temperature=0
    )

def search_file(name: str, direc: Path) -> List[Path]:
    if '*' in name:
        files = list(direc.glob(name))
        if files:
            return files
    else:
        f_name = direc/name
        if f_name.exists():
            return [f_name]
        
    iterdir = sorted([i for i in direc.iterdir() if i.is_dir()])
    for direc in iterdir:
        files = search_file(name, direc)
        if files:
            return files
            
    return []


class ASETool(Chain):
    """Tools that search csv using ASE agent"""
    llm_chain: LLMChain
    data_dir: Path = Path(config_chatmof['structure_dir'])
    input_key: str = 'question'
    output_key: str = 'answer'
    # print(f"data_dir:{data_dir}")
    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _parse_output(self, text:str) -> Dict[str, Any]:
        thought = re.search(
            r"(?<!Final )Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        material = re.search(
            r"Material:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        convert = re.search(
            r"Convert:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        input_ = re.search(
            r"Input:\s*(?:```|`)?(.+?)(?:```|`)?\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        final_thought = re.search(
            r"Final Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        final_answer = re.search(
            r"Final Answer:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|Material|Convert|$)", text, re.DOTALL)
        
        if (not input_) and (not final_answer):
            raise ValueError(f'unknown format from LLM: {text}')
        
        return {
            'Thought': (thought.group(1) if thought else None),
            'Material': (material.group(1) if material else None),
            'Convert': (convert.group(1) if convert else None),
            'Input': (input_.group(1).strip() if input_ else None),
            'Final Thought' : (final_thought.group(1) if final_thought else None),
            'Final Answer': (final_answer.group(1) if final_answer else None),
        }
    
    def _clear_name(self, text:str) -> str:
        remove_list = ['_clean_h', '_clean', '_charged', '_manual', '_ion_b', '_auto', '_SL', ]
        str_remove_list = r"|".join(remove_list)
        return re.sub(rf"({str_remove_list})", "", text)
    
    # @staticmethod
    def _get_atoms(self, material: str):
        ls_st: str[Path] = search_file(f'{material}*.cif', self.data_dir)
        if not ls_st:
            raise ValueError(f'{material} does not exists.')

        path: Path = ls_st[0]
        atoms = ase.io.read(path)
        return atoms
    
    def _write_log(self, action, text, run_manager):
        run_manager.on_text(f"\n[ASE repl] {action}: ", verbose=self.verbose)
        run_manager.on_text(text, verbose=self.verbose, color='yellow')
    
    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        return_observation = inputs.get('return_observation', False)
        
        agent_scratchpad = ''
        max_iteration = config_chatmof['max_iteration']

        input_ = self._clear_name(inputs[self.input_key])

        for i in range(max_iteration + 1):
            llm_output = self.llm_chain.run(
                question=input_,
                agent_scratchpad = agent_scratchpad,
                callbacks=callbacks,
                stop=['Observation:', 'Question:',]
            )

            if not llm_output.strip():
                agent_scratchpad += 'Thought: '
                llm_output = self.llm_chain.run(
                    question=input_,
                    agent_scratchpad = agent_scratchpad,
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:',]
                )
            
            #if llm_output.endswith('Final Answer: success'):
            if re.search(r'Final Answer: (success|.* above|.* DataFrames?).?$', llm_output):
                thought = f'Final Thought: we have to answer the question `{input_}` using observation\n'
                agent_scratchpad += thought
                llm_output = self.llm_chain.run(
                    question=input_,
                    agent_scratchpad = agent_scratchpad,
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:',]
                )
                llm_output = thought + llm_output

            output = self._parse_output(llm_output)

            if output['Final Answer']:
                if output['Thought']:
                    raise ValueError(llm_output)
                
                self._write_log('Final Thought', output['Final Thought'], run_manager)

                final_answer: str = output['Final Answer']
                check_sentence = ''
                if re.search(r'nothing', final_answer):
                    # please use tool `predictor` to get answer.'
                    final_answer = 'There are no data in ASE repl.'
                elif final_answer.endswith('.'):    
                    final_answer += check_sentence
                else:
                    final_answer = f'The answer for question "{input_}" is {final_answer}.{check_sentence}'
                return {self.output_key: final_answer}
            
            elif i >= max_iteration:
                final_answer = 'There are no data in ASE repl'
                self._write_log('Final Thought', final_answer, run_manager)
                return {self.output_key: final_answer}

            else:
                self._write_log('Material', output['Material'], run_manager)
                self._write_log('Convert', output['Convert'], run_manager)
                self._write_log('Thought', output['Thought'], run_manager)
                self._write_log('Input', output['Input'], run_manager)
                
            if output['Material']:
                atoms = self._get_atoms(output['Material'])

            pytool = PythonAstREPLTool(locals={'atoms': atoms})
            # pytool = PythonREPL(locals={'atoms': atoms})
            observation = str(pytool.run(output['Input'])).strip()
            
            if return_observation:
                if "\n" in observation:
                    self._write_log('Observation', "\n"+observation, run_manager)
                else:
                    self._write_log('Observation', observation, run_manager)
                return {self.output_key: observation}

            if "\n" in observation:
                self._write_log('Observation', "\n"+observation, run_manager)
            else:
                self._write_log('Observation', observation, run_manager)

            if output['Material'] and output['Convert']:
                agent_scratchpad += 'Material: {}\nConvert: {}\n'\
                    .format(output['Material'], output['Convert'])

            agent_scratchpad += 'Thought: {}\nInput: {} \nObservation: {}\n'\
                .format(output['Thought'], output['Input'], observation)

        raise AssertionError('Code Error! please report to author!')

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = ASE_PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['question', 'agent_scratchpad'],
        )
        llm_chain = LLMChain(llm=llm, prompt=template)
        return cls(llm_chain=llm_chain, **kwargs)

class TableSearcher(Chain):
    """Tools that search csv using Pandas agent"""
    llm_chain: LLMChain
    df: pd.DataFrame
    encode_function: Callable
    num_max_data: int = 200
    input_key: str = 'question'
    output_key: str = 'answer'

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _parse_output(self, text:str) -> Dict[str, Any]:
        thought = re.search(r"(?<!Final )Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        input_ = re.search(r"Input:\s*(?:```|`)?(.+?)(?:```|`)?\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        final_thought = re.search(r"Final Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        final_answer = re.search(r"Final Answer:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        observation = re.search(r"Observation:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        
        if (not input_) and (not final_answer):
            raise ValueError(f'unknown format from LLM: {text}')
        
        return {
            'Thought': (thought.group(1) if thought else None),
            'Input': (input_.group(1).strip() if input_ else None),
            'Final Thought' : (final_thought.group(1) if final_thought else None),
            'Final Answer': (final_answer.group(1) if final_answer else None),
            'Observation': (observation.group(1) if observation else None),
        }
    
    def _clear_name(self, text:str) -> str:
        remove_list = ['_clean_h', '_clean', '_charged', '_manual', '_ion_b', '_auto', '_SL', ]
        str_remove_list = r"|".join(remove_list)
        return re.sub(rf"({str_remove_list})", "", text)
    
    @staticmethod
    def _get_df(file_path: str):
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.xlsx':
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f'table must be .csv, .xlsx, or .json, not {file_path.suffix}')

        return df
    
    def _write_log(self, action, text, run_manager):
        run_manager.on_text(f"\n[Table Searcher] {action}: ", verbose=self.verbose)
        run_manager.on_text(text, verbose=self.verbose, color='yellow')
    
    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        
        return_observation = inputs.get('return_observation', False)
        information = inputs.get('information', "If unit exists, you must include it in the final output. The name of the material exists in the column \"name\".")

        agent_scratchpad = ''
        max_iteration = config_chatmof['max_iteration']

        input_ = self._clear_name(inputs[self.input_key])

        for i in range(max_iteration + 1):
            llm_output = self.llm_chain.run(
                df_index = str(list(self.df)),
                information = information,
                df_head = self.df.head().to_markdown(),
                question=input_,
                agent_scratchpad = agent_scratchpad,
                callbacks=callbacks,
                stop=['Observation:', 'Question:',]
            )

            if not llm_output.strip():
                agent_scratchpad += 'Thought: '
                llm_output = self.llm_chain.run(
                    df_index = str(list(self.df)),
                    information = information,
                    df_head = self.df.head().to_markdown(),
                    question=input_,
                    agent_scratchpad = agent_scratchpad,
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:',]
                )
            
            #if llm_output.endswith('Final Answer: success'):
            if re.search(r'Final Answer: (success|.* above|.* success|.* succeed|.* DataFrames?).?$', llm_output):
                thought = f'Final Thought: we have to answer the question `{input_}` using observation\n'
                agent_scratchpad += thought
                llm_output = self.llm_chain.run(
                    df_index = str(list(self.df)),
                    df_head = self.df.head().to_markdown(),
                    question=input_,
                    information = information,
                    agent_scratchpad = agent_scratchpad,
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:',]
                )
                llm_output = thought + llm_output

            output = self._parse_output(llm_output)

            if output['Final Answer']:
                if output['Observation']:
                    raise ValueError(llm_output)
                
                self._write_log('Final Thought', output['Final Thought'], run_manager)

                final_answer: str = output['Final Answer']
                #if final_answer == 'success':
                #    agent_scratchpad += 'Thought: {}\nInput: {} \nObservation: {}\n'\
                #            .format(output['Thought'], output['Input'], observation)

                #check_sentence = ' Check to see if this answer can be your final answer, and if so, you should submit your final answer. You should not do any additional verification on the answer.'
                check_sentence = ''
                if re.search(r'nothing', final_answer):
                    final_answer = 'There are no data in database.' # please use tool `predictor` to get answer.'
                elif final_answer.endswith('.'):    
                    final_answer += check_sentence
                else:
                    final_answer = f'The answer for question "{input_}" is {final_answer}.{check_sentence}'

                self._write_log('Final Answer', final_answer, run_manager)
                return {self.output_key: final_answer}
            
            elif i >= max_iteration:
                final_answer = 'There are no data in database'
                self._write_log('Final Thought',
                                output['Final Thought'], run_manager)
                self._write_log('Final Answer', final_answer, run_manager)

                return {self.output_key: final_answer}

            else:
                self._write_log('Thought', output['Thought'], run_manager)
                self._write_log('Input', output['Input'], run_manager)
                
            # pytool = PythonREPL(locals={'df':self.df})
            pytool = PythonAstREPLTool(locals={'df':self.df})
            observation = str(pytool.run(output['Input'])).strip()

            num_tokens = self.encode_function(observation)
            
            if return_observation:
                if "\n" in observation:
                    self._write_log('Observation', "\n"+observation, run_manager)
                else:
                    self._write_log('Observation', observation, run_manager)
                return {self.output_key: observation}
            
            #if num_tokens > 3400:
                #raise ValueError('The number of tokens has been exceeded.')
                # observation = f"The number of tokens has been exceeded. To reduce the length of the message, please modify code to only pull up to {self.num_max_data} data."
                # self.num_max_data = self.num_max_data // 2

            if "\n" in observation:
                self._write_log('Observation', "\n"+observation, run_manager)
            else:
                self._write_log('Observation', observation, run_manager)

            agent_scratchpad += 'Thought: {}\nInput: {} \nObservation: {}'\
                .format(output['Thought'], output['Input'], observation)

        raise AssertionError('Code Error! please report to author!')

    @classmethod
    def from_filepath(
        cls,
        llm: BaseLanguageModel,
        file_path: Path = Path(config_chatmof['lookup_dir']),
        prompt: str = DF_PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['df_index', 'information', 'df_head', 'question', 'agent_scratchpad']
        )
        # print(f"lookup_dir_file_path:{file_path}")
        llm_chain = LLMChain(llm=llm, prompt=template)
        df = cls._get_df(file_path)
        encode_function = llm.get_num_tokens
        return cls(llm_chain=llm_chain, df=df, encode_function=encode_function, **kwargs)
    
    @classmethod
    def from_dataframe(
        cls,
        llm: BaseLanguageModel,
        dataframe: pd.DataFrame,
        prompt: str = DF_PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['df_index', 'information', 'df_head', 'question', 'agent_scratchpad']
        )
        llm_chain = LLMChain(llm=llm, prompt=template)
        encode_function = llm.get_num_tokens
        return cls(llm_chain=llm_chain, df=dataframe, encode_function=encode_function, **kwargs)

class UnitConverter(Chain):
    """Tools that search csv using Pandas agent"""
    llm_chain: LLMChain
    data_dir: Path = Path(config_chatmof['structure_dir'])
    input_key: str = 'question'
    output_key: str = 'answer'

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _write_log(self, action, text, run_manager):
        run_manager.on_text(f"\n[Visualizer] {action}: ", verbose=self.verbose)
        run_manager.on_text(text, verbose=self.verbose, color='yellow')

    def _parse_output(self, text: str) -> Dict[str, Any]:
        thought = re.search(
            r"(?<!Final )Thought:\s*(.+?)\s*(Unit|Equation|Information|Thought|Question|$)", text, re.DOTALL)
        unit = re.search(
            r"Unit:\s*(.+?)\s*(Unit|Equation|Information|Thought|Question|$)", text, re.DOTALL)
        equation = re.search(
            r"Equation:\s*(.+?)\s*(Unit|Equation|Information|Thought|Question|$)", text, re.DOTALL)
        info = re.search(
            r"Information:\s*(.+?)\s*(Unit|Equation|Information|Thought|Question|$)", text, re.DOTALL)

        if not equation and not info:
            raise ValueError(f'unknown format for LLM: {text}')

        return {
            'Thought': (thought.group(1) if thought else None),
            'Unit': (unit.group(1) if unit else None),
            'Equation': (equation.group(1) if equation else None),
            'Information': (info.group(1) if info else None),
        }

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()

        llm_output = self.llm_chain.run(
            question=inputs[self.input_key],
            callbacks=callbacks,
            stop=['Question:'],
        )

        output = self._parse_output(llm_output)
        self._write_log('Thought', output['Thought'], run_manager)
        self._write_log('Unit', output['Unit'], run_manager)
        self._write_log('Equation', output['Equation'], run_manager)
        self._write_log('Information', output['Information'], run_manager)

        output = f"Equation: {output['Equation']}, Information: {output['Information']}"
        return {self.output_key: output}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['question'],
        )
        llm_chain = LLMChain(llm=llm, prompt=template)
        return cls(llm_chain=llm_chain, **kwargs)

# @timer_decorator
def search_csv_fun(question: str) -> str:
    """
    Query the relevant information of the MOF material according to the MOF data table, such as Largest cavity diameter, Pore limiting diameter, Largest free pore diameter, Density, Accessible Surface Area, Nonaccessible surface area, Accessible volume volume fraction, void fraction, Accessible pore volume, Accessible volume, Nonaccessible Volume, Metal type, Has open metal site and Type of open metal. 
    The input must be a detailed full sentence to answer the question.
    """
    config = copy.deepcopy(config_default)
    # config.update(kwargs)
    # search_internet = config['search_internet']
    verbose = config['verbose']
    llm = get_deepseek_llm()
    llm = get_llm(model, temperature=0)
    callback_manager = [StdOutCallbackHandler()]
    # run_manager = CallbackManagerForChainRun.get_noop_manager()

    table_searcher = TableSearcher.from_filepath(
        llm=llm,
        file_path=Path(config['lookup_dir']),  
        verbose=verbose
    )

    try:
        output = table_searcher.run(question, callbacks=callback_manager)
    except Exception as e:
        output = f"Error occurred: {e}"
    markdown_result = f"{output}"
    return markdown_result

# @timer_decorator
def ase_tool_fun(question: str) -> str:
    """
    A tool that uses ASE to handle questions related to atomic simulations or properties.
    The input should be a detailed full sentence describing the query.
    """
    config = copy.deepcopy(config_default)
    verbose = config['verbose']
    llm = get_deepseek_llm()
    llm = get_llm(model, temperature=0)
    callback_manager = [StdOutCallbackHandler()]

    ase_tool = ASETool.from_llm(
        llm=llm,
        verbose=verbose
    )

    try:
        output = ase_tool.run(question, callbacks=callback_manager)
    except Exception as e:
        output = f"Error occurred: {e}"
    markdown_result = f"{output}"
    return markdown_result

def unit_converter_fun(question: str) -> str:
    """
    A tool that helps with unit conversions. 
    The input should be a detailed full sentence describing the unit conversion query.
    """
    config = copy.deepcopy(config_default)
    verbose = config['verbose']
    llm = get_deepseek_llm()
    llm = get_llm(model, temperature=0)
    callback_manager = [StdOutCallbackHandler()]

    unit_converter = UnitConverter.from_llm(
        llm=llm,
        verbose=verbose
    )

    try:
        output = unit_converter.run(question, callbacks=callback_manager)
    except Exception as e:
        output = f"Error occurred: {e}"
    markdown_result = f"{output}"
    return markdown_result




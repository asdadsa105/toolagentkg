import importlib
from ToolsFuns.tools_dict import TOOLS_MAPPING

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import asyncio

# app = FastAPI()
# executor = ProcessPoolExecutor()
executor = ThreadPoolExecutor()

tool_categories = {}
for category, names in TOOLS_MAPPING.items():
    for name in names:
        tool_categories[name] = category
tool_categories = tool_categories


def get_tool_fun(name):
    category_base = tool_categories[name].replace("Tools", "")
    module_path = f'ToolsFuns.{category_base}.tool_name_dict'
    dict_name = f"{category_base.upper()}_TOOLS_DICT"

    try:
        # Dynamic import module
        tools_dict_module = importlib.import_module(module_path)
        tools_dict = getattr(tools_dict_module, dict_name, {})
    except ImportError:
        print(
            f"Warning: Module for {category_base} not found at {module_path}.")
        raise ValueError(
            f"Module for {category_base} not found at {module_path}.")
    except Exception:
        print(
            f"Warning: Module for {category_base} not found at {module_path}.")
        raise ValueError(
            f"Module for {category_base} not found at {module_path}.")

    func = tools_dict[name]
    if not func:
        print(f"Warning: Tool {name} not found in {module_path}.")
        raise ValueError("Tool {name} not found in {module_path}.")
    return func


def run_tool(name, input_str):
    func = get_tool_fun(name)
    return func(input_str)

async def run_task_in_process(func_name, func_args):
    loop = asyncio.get_running_loop()
    # Use thread pools to execute tasks
    result = await loop.run_in_executor(executor, run_tool, func_name, func_args)
    return result


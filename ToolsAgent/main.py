from typing import List 
import os
from uvicorn import run
from fastapi import Body, FastAPI, HTTPException
from tool_runner import run_task_in_process
from config import Config

def set_upload_file_info(config, file_path_list: list):
    if file_path_list:
        last_file_path = file_path_list[-1]
        last_file_ext = os.path.splitext(last_file_path)[1][1:]  
        last_file_dir = os.path.dirname(last_file_path)

        upload_file_names = [
            os.path.basename(file_path)
            for file_path in file_path_list
            if file_path.endswith(f".{last_file_ext}")
        ]

        Config().UPLOAD_FILES_TYPE = last_file_ext
        Config().UPLOAD_FILES_BASE_PATH = last_file_dir
        Config().UPLOAD_FILES_NAMES = upload_file_names
    else:
        Config().UPLOAD_FILES_TYPE = None
        Config().UPLOAD_FILES_BASE_PATH = None
        Config().UPLOAD_FILES_NAMES = []

app = FastAPI()

@app.post("/run-func")
async def run_func(func_name: str, func_args: str, file_path_list: List[str] = Body(..., embed=True)):
    try:  
        set_upload_file_info(Config(), file_path_list)
        print(f"base_path:{Config().UPLOAD_FILES_BASE_PATH}")
        result = await run_task_in_process(func_name, func_args)
        return {"status_code": 200, "result": result}

    except (ImportError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    run(app=app, host='0.0.0.0', port=60002)

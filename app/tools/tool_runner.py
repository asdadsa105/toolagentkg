import aiohttp

async def run_tool(tool_name, tool_args, file_path_list):
    url = "http://127.0.0.1:60002/run-func"

    params = {
        "func_name": tool_name,
        "func_args": tool_args
    }

    json_data = {
        "file_path_list": file_path_list
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params, json=json_data) as response:
            res = await response.json()
            return res["result"]
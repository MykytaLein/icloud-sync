import json

def load_last_run_info() -> dict:
    with open('./last_run.json') as info:
        return json.load(info)
    
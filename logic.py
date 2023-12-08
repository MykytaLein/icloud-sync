import logging as log
import json
from pyicloud import PyiCloudService

def load_last_run_info() -> dict:
    with open('./last_run.json') as info:
        return json.load(info)

def load_photos(appleId: str, pwd: str, 
    fromDate: str, toDate: str, mainWindow):
    api = PyiCloudService(appleId, pwd, cookie_directory='./log')
    if api.requires_2fa:
        code = mainWindow.pop_up_2fa()
        if not code: 
            log.error('No 2fa code provided')
            return
        
        result = api.validate_2fa_code(code)
        if not result: 
            log.error('False 2fa code provided')
            return
        
    elif api.requires_2sa:
        pass
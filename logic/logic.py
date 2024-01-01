import logging as log
import json
import shutil
import zipfile
from io import BytesIO
from datetime import datetime

from pyicloud import PyiCloudService
from pyicloud.services.photos import PhotoAsset
from os.path import isfile
import pandas as pd

class Logic:
    device: str
    processedPhotos: pd.DataFrame
    
    def __init__(self) -> None:
        self.processedPhotos = self.get_processed_photos()

    def load_last_run_info(self) -> dict:
        with open('./log/last_run.json') as info:
            return json.load(info)

    def load_photos(self, appleId: str, pwd: str, 
            fromDate: str, toDate: str, mainWindow):
        # Establish connection to iCloud
        api = PyiCloudService(appleId, pwd, cookie_directory='./log')
        
        # Handle authentication request
        authenticated = self.handle_authentication(api=api, mainWindow=mainWindow)
        if not authenticated: return 

        # for loop

        for index, photo in enumerate(api.photos.all):
            # 499 <PhotoAsset: id=AcCjs8CfnS/WwBWehUF1GZOSh2AI> 2023-11-25 16:03:51.798000+00:00 IMG_2272.JPG
            print(index, photo, photo.asset_date, photo.filename)
            # check for zip

    def process_photo(self, photo: PhotoAsset, index: int, fromDate: str, toDate: str):
        if photo.created < datetime.date(fromDate): return
        if photo.created < datetime.date(toDate): return
        if photo.id in self.processedPhotos.index: return



    def save_photo(self, photo: PhotoAsset):
        photoCopy = BytesIO()
        shutil.copyfileobj(photo.download(), photoCopy)
        with open(f'./{photo.filename}', 'wb') as photoFile:
            photoFile.write(photoCopy.raw.read())

    def handle_authentication(self, api: PyiCloudService, mainWindow):
        # Two-factor authentication
        if api.requires_2fa:
            # Request authentication code
            code = mainWindow.pop_up_2fa() # the code stops here until popup is closed
            
            # If popup was closed without input
            if not code: 
                log.error('No 2fa code provided')
                return False
            
            # Validate authentication code
            result = api.validate_2fa_code(code)
            if not result:
                log.error('False 2fa code provided')
                return False
            
        # Two step authentication
        elif api.requires_2sa:
            # Load list of trusted devices 
            devices = [
                device.get('phoneNumber') for device in api.trusted_devices
            ]
            # Ask user to choose which device to use for authentication
            mainWindow.pop_up_2sa(devices=devices)

            if not self.device: return False

            # Send verification code to the chosen trusted device
            sent = api.send_verification_code(self.device)
            if not sent:  
                log.error('Failed to send two step authentication code')
                return False
            
            # Request authentication code
            code = mainWindow.pop_up_2fa() # the code stops here until popup is closed

            # If popup was closed without input
            if not code: 
                log.error('No verification code provided')
                return False
            
            # Validate verification code
            result = api.validate_verification_code(code)
            if not result:
                log.error('False verification code provided')
                return False
        
        # If none of the negative conditions are met return true to proceed
        return True 

    def get_processed_photos(self) -> pd.DataFrame:
        path = './log/processed_photos.csv'
        if isfile(path):
            result = pd.read_csv(path)
        else:
            result = pd.DataFrame(columns=['photo_id', 'date_taken', 'date_imported'])
        
        result.set_index('photo_id')
        return result
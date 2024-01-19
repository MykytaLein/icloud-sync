import logging as log
import shutil
import json
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime, date

from pyicloud import PyiCloudService
from pyicloud.services.photos import PhotoAsset, PhotoAlbum
from os.path import isfile
import pandas as pd
from dateutil import tz

class Logic:
    device: str
    processedPhotos: pd.DataFrame
    
    def __init__(self) -> None:
        self.processedPhotos = self.get_processed_photos()
        self.fromZone = tz.tzutc()
        self.toZone = tz.tzlocal()

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

        # Create a zip file to store all zip archives
        today = datetime.now().date().strftime('%d.%m.%Y')
        outputZipFilename = f'./photos/{fromDate}-{toDate}_imported_at_{today}.zip'

        with ZipFile(outputZipFilename, "w") as zip:
            self.process_photos(
                zip=zip, 
                photos=api.photos.all, 
                fromDate=fromDate, 
                toDate=toDate)
            
    def process_photos(self, zip: ZipFile, photos: PhotoAlbum, fromDate: str, toDate: str):
        # Initialize zip directory name
        zipDirectory = ''
        for index, photo in enumerate(photos):
            print(f'processing photo {photo}')
            zipDirectory= self.get_zip_directory(index, zipDirectory, photo.created.date())
            savePhoto = self.photo_is_to_be_saved(photo, fromDate, toDate)
            if savePhoto: self.save_photo(index, photo, zipDirectory, zip)

    def get_zip_directory(self, index: int, zipDirectory: str, photoCreated: date):
        if index % 100 != 0: return zipDirectory
        return f'from_{photoCreated.strftime("%d.%m.%Y")}'

    def photo_is_to_be_saved(self, photo: PhotoAsset, fromDate: str, toDate: str):
        print('before', photo.created)
        created = photo.created.replace(tzinfo=self.fromZone).astimezone(self.toZone)
        print('after', created)
        if created < datetime.strptime(fromDate, '%d.%m.%Y').replace(tzinfo=self.toZone): return False
        if created > datetime.strptime(toDate, '%d.%m.%Y').replace(tzinfo=self.toZone): return False
        if photo.id in self.processedPhotos.index: return False
        return True

    def save_photo(self, index: int, photo: PhotoAsset, zipDirectory: str, outputZip: ZipFile):
        # Copy the photo as BytesIO object
        photoCopy = BytesIO(photo.download().content)

        # Save the photo with a unique name based on timestamp together with directory index (out of 100)
        photo_name = f"{zipDirectory}/{photo.created}{(index+1)%101}.jpeg"
        outputZip.writestr(photo_name, photoCopy.getvalue())

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
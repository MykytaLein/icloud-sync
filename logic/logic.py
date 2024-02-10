import logging as log
import json
import os
from io         import BytesIO
from zipfile    import ZipFile
from datetime   import datetime
from os.path    import isfile
from threading  import Thread, Event

import pandas as pd
from pyicloud   import PyiCloudService
from pyicloud.services.photos import PhotoAsset, PhotoAlbum
from pyicloud.exceptions import PyiCloudFailedLoginException
from dateutil   import tz

# import concurrent.futures
# import shutil

class Logic(Thread):
    device: str
    processedPhotos: pd.DataFrame
    
    def __init__(self) -> None:
        super(Logic, self).__init__(target=self.load_photos, daemon=True)
        self.stopEvent = Event()
        self.processedPhotos = self.get_processed_photos()
        self.fromZone = tz.tzutc()
        self.toZone = tz.tzlocal()
        self.today = datetime.now().date().strftime('%d.%m.%Y')

        
    def set_variables(
            self, appleId: str, pwd: str, 
            fromDate: str, toDate: str, mainWindow):
        self.appleId, self.pwd, self.fromDate, self.toDate, self.mainWindow = (
            appleId, pwd, fromDate, toDate, mainWindow)

    def load_photos(self):
        # Establish connection to iCloud
        try:
            api = PyiCloudService(self.appleId, self.pwd, cookie_directory='./log')
        except PyiCloudFailedLoginException as e:
            log.error(f'Authentication failed: {str(e)}') 
            return False

        # Handle authentication request
        authenticated = self.handle_authentication(api=api)
        if not authenticated: return False

        # Create a zip file to store all zip archives
        # today = datetime.now().date().strftime('%d.%m.%Y')
        outputZipFilename = f'./photos/{self.fromDate}-{self.toDate}_imported_at_{self.today}.zip'

        try:
            with ZipFile(outputZipFilename, "w") as zip:
                self.process_photos(
                    zip=zip, 
                    photos=api.photos.all)
        
        # except ValueError: pass
        finally:
            self.post_import()
            log.info('Process finished')

    def post_import(self):
        self.processedPhotos.to_csv('./log/processed_photos.csv') # Overwrites with new numbers
        
        # Delete session files
        logDir = './log'
        for filename in os.listdir(logDir):
            if filename in ['last_run.json', 'log.log']: continue
            os.remove(os.path.join(logDir, filename))
            
    def process_photos(self, zip: ZipFile, photos: PhotoAlbum):
        # Initialize zip directory name
        zipDirectory = ''

        for index, photo in enumerate(photos):
            print(f'Processing photo {photo.filename}')
            if self.stopped: return
            created = photo.created.replace(tzinfo=self.fromZone).astimezone(self.toZone)
            zipDirectory= self.get_zip_directory(index, zipDirectory, created)
            savePhoto = self.photo_is_to_be_saved(photo, created)
            if savePhoto: self.save_photo(index, photo, created, zipDirectory, zip)

    def get_zip_directory(self, index: int, zipDirectory: str, created: datetime):
        if index % 100 != 0: return zipDirectory
        return f'from_{created.date().strftime("%d.%m.%Y")}'

    def photo_is_to_be_saved(self, photoId: str, created: datetime):
        if created < datetime.strptime(self.fromDate, '%d.%m.%Y').replace(tzinfo=self.toZone): return False
        if created > datetime.strptime(self.toDate, '%d.%m.%Y').replace(tzinfo=self.toZone): return False
        if photoId in self.processedPhotos.index: return False
        return True

    def save_photo(self, index: int, photo: PhotoAsset, created: datetime, zipDirectory: str, zip: ZipFile):
        # Copy the photo as BytesIO object
        photoCopy = BytesIO(photo.download().content)

        # Diffirentiate between photos and videos
        format = photo.filename[-3:]

        # Save the photo with a unique name based on timestamp together with directory index (out of 100)
        photo_name = f"{zipDirectory}/{created.strftime('%d.%m.%Y-%H.%M.%S')}-{(index+1)%101}.{format}"
        zip.writestr(photo_name, photoCopy.getvalue())
        
        # Add photo to a processed photos dataset
        self.add_processed_photo(photo, created)
    
    def add_processed_photo(self, photo: PhotoAsset, created: datetime):
        newRow = [photo.id, created.date, self.today]
        # print(newRow)
        self.processedPhotos.loc[photo.id] = newRow
        # print(self.processedPhotos)

    def handle_authentication(self, api: PyiCloudService):
        # Two-factor authentication
        if api.requires_2fa:
            # Request authentication code
            code = self.mainWindow.pop_up_2fa() # the code stops here until popup is closed
            
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
            self.mainWindow.pop_up_2sa(devices=devices)

            if not self.device: return False

            # Send verification code to the chosen trusted device
            sent = api.send_verification_code(self.device)
            if not sent:  
                log.error('Failed to send two step authentication code')
                return False
            
            # Request authentication code
            code = self.mainWindow.pop_up_2fa() # the code stops here until popup is closed

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
        
        result.set_index('photo_id', drop=False)
        return result
    
    def stop(self):
        self.stopEvent.set()

    @property
    def stopped(self):
        return self.stopEvent.is_set()
    
def load_last_run_info() -> dict:
    with open('./log/last_run.json') as info:
        return json.load(info)
from typing import List

import gdown
from loguru import logger
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def download_folder_from_drive(url: str):
    gdown.download_folder(url, quiet=True, use_cookies=False)
    logger.info("Folder successfully downloaded from GDrive!")


def gdrive_auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)
    logger.info("Google drive successfully authenticated!")

    return drive


def upload_file_to_drive(
    drive: GoogleDrive, url_list: List[str], parent_folder_id: str
):
    for upload_file in url_list:
        gfile = drive.CreateFile({"parents": [{"id": parent_folder_id}]})
        gfile.SetContentFile(upload_file)
        gfile.Upload()
    logger.info("Files successfully uploaded to GDrive!")

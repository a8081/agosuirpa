import os
import zipfile
import shutil
from agosuirpa.settings import sep, UI_LOGS_FOLDERNAME

def split_name_system(root_path):
    if "/" in root_path:
        splitted = root_path.split("/")
    elif "\\" in root_path:
        splitted = root_path.split("\\")
    if "/" in root_path or "\\" in root_path:
        folder_path = sep.join(splitted)
    else:
        folder_path = root_path   
    return folder_path

def upload_mockups(zip_path):
    zip_path = split_name_system(zip_path)
    path_without_fileextension = zip_path.split('.')[0] 
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(path_without_fileextension)
    return path_without_fileextension

def compress_experiment(path, file_name):
    folder_path = split_name_system(path)
    zip_file = folder_path + sep + file_name 
    abs_path = os.path.abspath(folder_path + sep + ui_logs_foldername)
    zip_path = zip_file + ".zip"
    if not os.path.exists(zip_path):
        zip_path = shutil.make_archive(zip_file, 'zip', abs_path)
    return zip_path
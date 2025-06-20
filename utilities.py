#! /usr/bin/env python3

"""
Function to handle file utilites for the main script.
"""

import os
import shutil
from zipfile import ZipFile
import glob
import py7zr

def is_within_directory(directory, target):
    """" Check if absolute path for two directories are the same. """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)

    return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

def secure_extract(zip_file, extract_path):
    """ Function that ensure files in zip are not malicious. """
    with ZipFile(zip_file) as z:
        for member in z.namelist():
            member_path = os.path.join(extract_path, member)
            if not is_within_directory(extract_path, member_path):
                raise Exception("Attempted Path Traversal.")
        z.extractall(extract_path)

def secure_extract_7z(zip_file, extract_path):
    with py7zr.SevenZipFile(zip_file, mode='r') as z:
        for member in z.getnames():
            member_path = os.path.join(extract_path, member)
            if not is_within_directory(extract_path, member_path):
                raise Exception("Attempted Path Traversal.")
        z.extractall(path=extract_path)

def delete_uploads(folder):
    """ Funtion that deletes the upload folder. """
    if os.path.exists(folder):
        shutil.rmtree(folder)

    return None

def delete_zip(folder="."):
    """ Function that cleans up the zip files in the current directory. """
    if os.path.exists(folder):
        patterns = ["*.zip", "*.7z"]

        for pattern in patterns:
            print(glob.glob(os.path.join(folder, pattern)))
            for file_path in glob.glob(os.path.join(folder, pattern)):
                try:
                    print(file_path)
                    os.remove(file_path)
                except Exception as e:
                    print(e)

    return None

def unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    new_path = file_path    

    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter +=1

    return new_path
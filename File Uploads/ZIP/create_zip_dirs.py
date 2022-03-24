#!/usr/bin/python3
import os
from io import BytesIO
import zipfile

# Variables
filen = 'malicious_file.zip'
dirname = "zip"

def build_zip():
    f = BytesIO()
    with zipfile.ZipFile(filen,mode='w',compression=zipfile.ZIP_DEFLATED) as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(dirname):
            for filename in filenames:
                # Create complete filepath of file in directory
                # filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filename)

build_zip()

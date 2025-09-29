import os
from logging import info
import subprocess
import requests
import zipfile


def download_and_extract_zip(url, extract_to='resource_hacker'):
    os.makedirs(extract_to, exist_ok=True)
    extract_to= os.path.join(extract_to, 'resource_hacker')
    os.makedirs(extract_to, exist_ok=True)

    zip_filename = os.path.join(extract_to, 'resource_hacker.zip')
    response = requests.get(url, headers={"User-Agent": "XY"})
    response.raise_for_status()  # Ensure the request was successful

    with open(zip_filename, 'wb') as file:
        file.write(response.content)

    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    os.remove(zip_filename)

def add_icon_to_executable(name, icon_path, folder):
    name = os.path.abspath(os.path.splitext(os.path.basename(name))[0])
    cache_path = os.path.expandvars('%LOCALAPPDATA%\\Cythontoexe.cache')
    os.makedirs(cache_path, exist_ok=True)
    info(f'Cache path: {cache_path}')

    if not os.path.exists(os.path.join(cache_path, 'resource_hacker')):
        info('Downloading ResourceHacker...')
        download_and_extract_zip('https://www.angusj.com/resourcehacker/resource_hacker.zip', cache_path)

    r_hacker_path = os.path.join(cache_path, 'resource_hacker', 'ResourceHacker.exe')
    if folder: command = f'"{r_hacker_path}" -open "{name}.exe" -save "{name}.exe" -action add -res "{icon_path}" -mask ICONGROUP,MAINICON'
    else: command = f'"{r_hacker_path}" -open "{name}.exe" -save "{name}.exe" -action add -res "{icon_path}" -mask ICONGROUP,MAINICON'
    subprocess.run(command, shell=True)

def add_uac_to_executable(name, folder=False):
    """
    Adds a UAC manifest requesting admin privileges to an executable.
    """
    name = os.path.abspath(os.path.splitext(os.path.basename(name))[0])
    cache_path = os.path.expandvars(r'%LOCALAPPDATA%\Cythontoexe.cache')
    os.makedirs(cache_path, exist_ok=True)
    info(f"Cache path: {cache_path}")

    # Ensure Resource Hacker is available
    rh_path = os.path.join(cache_path, 'resource_hacker')
    if not os.path.exists(rh_path):
        info("Downloading ResourceHacker...")
        download_and_extract_zip('https://www.angusj.com/resourcehacker/resource_hacker.zip', cache_path)

    r_hacker_path = os.path.join(rh_path, 'ResourceHacker.exe')

    # Create a temporary manifest file
    manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>"""
    manifest_path = os.path.join(cache_path, 'uac_manifest.manifest')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

    # Construct Resource Hacker command
    if folder:
        command = f'"{r_hacker_path}" -open "{name}.exe" -save "{name}.exe" -action add -res "{manifest_path}" -mask MANIFEST,1'
    else:
        command = f'"{r_hacker_path}" -open "{name}.exe" -save "{name}.exe" -action add -res "{manifest_path}" -mask MANIFEST,1'

    info(f"Running Resource Hacker to add UAC manifest to {name}.exe")
    subprocess.run(command, shell=True)
    info("Done!")    
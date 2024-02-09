#this main 
import os
from datetime import datetime, timedelta
from mega import Mega
from io import BytesIO
import zipfile
import schedule
import time
from tqdm import tqdm

def create_zip(source_folder, subfolder):
    buffer = BytesIO()
    date_str = os.path.basename(source_folder)
    zip_filename = f"{date_str}_{subfolder}.zip"

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Use the relative path of the file from the source_folder as arcname
                arcname = os.path.relpath(file_path, source_folder)
                zip_file.write(file_path, arcname=arcname)

    buffer.seek(0)
    return zip_filename, buffer

def upload_to_mega(zip_filename, zip_buffer, mega_folder):
    temp_filename = f'/tmp/{zip_filename}'
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(zip_buffer.read())

    mega = Mega()
    m = mega.login('agathicountai@gmail.com', '@Aga$12ca#')  # Replace with your Mega email and password

    try:
        mega_space_info = m.get_storage_space()

        # Check if the available space is less than 90%
        if mega_space_info['used'] / mega_space_info['total'] * 100 < 90:
            # If the folder already exists in Mega, delete it
            mega_files = m.get_files()
            folder_exists = any(file['name'] == mega_folder and file['type'] == 'd' for file in mega_files if 'type' in file)

            if folder_exists:
                m.delete(m.find(mega_folder)[0]['h'])

            # Create the Mega folder
            m.create_folder(mega_folder)

            # Upload the zip file to Mega
            print(f"Uploading {zip_filename} to Mega...")
            m.upload(temp_filename, m.find(mega_folder)[0])

            # Indicate the end of the upload
            print("=" * 30)
            print(f"Finished uploading {zip_filename}\n")
            print("=" * 30)

        else:
            # If available space is greater than or equal to 90%, proceed with upload and delete old folders
            # Check if the folder already exists in Mega, if not, create it
            mega_files = m.get_files()
            folder_exists = any(file['name'] == mega_folder and file['type'] == 'd' for file in mega_files if 'type' in file)

            if not folder_exists:
                m.create_folder(mega_folder)

            # Upload the zip file to Mega
            print(f"Uploading {zip_filename} to Mega...")
            m.upload(temp_filename, m.find(mega_folder)[0])

            # Delete old date_subfolder.zip folders
            for old_folder in [file for file in mega_files if 'name' in file and file['name'].startswith(date_str) and file['type'] == 'f']:
                m.delete(old_folder['h'])

            # Indicate the end of the upload
            print("=" * 30)
            print(f"Finished uploading {zip_filename}\n")
            print("=" * 30)

    except Exception as e:
        # Handle the exception and print an error message
        print("=" * 30)
        print(f"Upload failed for {zip_filename}: {str(e)}\n")
        print("=" * 30)

    finally:
        # Delete the temporary file
        os.remove(temp_filename)

def job():
    main_folder = '/home/alan/projects/coneinespection-ui/'
    mega_folder = 'new'

    today = datetime.today()
    previous_date = today - timedelta(days=1)
    previous_date_str = previous_date.strftime("%d-%m-%Y")
    #previous_date_str = previous_date.strftime("%Y-%m-%d") #2023-01-10 date formate

    for subfolder in ['classLive', 'uvclassLive']:
        subfolder_path = os.path.join(main_folder, subfolder)
        date_folder = os.path.join(subfolder_path, previous_date_str)

        if os.path.exists(date_folder):
            zip_filename, zip_buffer = create_zip(date_folder, subfolder)
            upload_to_mega(zip_filename, zip_buffer, mega_folder)

#schedule.every().day.at("01:00").do(job)
schedule.every(2).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
 

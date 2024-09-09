import os
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from src.chunker import chunk_structured_document
from src.utils import save_chunks_as_txt, save_chunks_as_json, save_chunks_as_csv
from PyPDF2 import PdfReader

# Set up logging
logging.basicConfig(
    filename='logs/chunking.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def authenticate_with_google():
    """
    Authenticate with Google Drive using PyDrive.
    """
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
    return GoogleDrive(gauth)

def download_files_from_drive_folder(drive, folder_id, download_dir):
    """
    Download all files from a Google Drive folder.
    Args:
    - drive: Authenticated PyDrive instance.
    - folder_id: Google Drive folder ID.
    - download_dir: Directory where the files will be saved.
    """
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and mimeType='application/pdf'"}).GetList()
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for file in file_list:
        file_name = file['title']
        file_path = os.path.join(download_dir, file_name)
        logging.info(f"Downloading {file_name} from Google Drive.")
        file.GetContentFile(file_path)
        logging.info(f"Downloaded {file_name} to {file_path}.")
    
    return [f['title'] for f in file_list]

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using PyPDF2.
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text
    except Exception as e:
        logging.error(f"Failed to extract text from {file_path}: {e}")
        return None

def process_google_drive_folder(folder_id, download_dir, output_dir):
    """
    Download and process all PDFs from a Google Drive folder.
    Args:
    - folder_id: Google Drive folder ID.
    - download_dir: Directory to save downloaded PDFs.
    - output_dir: Directory to save chunked outputs.
    """
    drive = authenticate_with_google()

    # Step 1: Download all files from the Google Drive folder
    file_names = download_files_from_drive_folder(drive, folder_id, download_dir)

    # Step 2: Process each downloaded PDF
    for filename in file_names:
        if filename.endswith(".pdf"):
            file_path = os.path.join(download_dir, filename)

            # Extract text from PDF
            pdf_content = extract_text_from_pdf(file_path)
            if not pdf_content:
                logging.error(f"Skipping {filename} due to extraction failure.")
                continue

            # Chunk the text using semantic similarity
            chunks = chunk_structured_document(pdf_content)
            if not chunks:
                logging.error(f"No chunks created for {filename}. Skipping.")
                continue

            # Save the chunks in different formats
            base_filename = os.path.splitext(filename)[0]
            txt_output_path = os.path.join(output_dir, f"{base_filename}_chunked.txt")
            json_output_path = os.path.join(output_dir, f"{base_filename}_chunked.json")
            csv_output_path = os.path.join(output_dir, f"{base_filename}_chunked.csv")

            save_chunks_as_txt(chunks, txt_output_path)
            save_chunks_as_json(chunks, json_output_path)
            save_chunks_as_csv(chunks, csv_output_path)

            logging.info(f"Successfully processed and saved chunks for {filename}.")

if __name__ == "__main__":
    # Google Drive folder ID (the part after 'folders/' in the shared link)
    folder_id = '1DUjejnNijWOkh45trc3ahBvfDvL6Lxxy'

    # Directory to save the downloaded PDFs
    download_dir = 'data'

    # Directory to store the chunked output files
    output_dir = 'output'

    # Start the process
    logging.info("Starting the PDF chunking process from Google Drive folder.")
    process_google_drive_folder(folder_id, download_dir, output_dir)
    logging.info("PDF chunking process completed.")

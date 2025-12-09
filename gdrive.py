"""
Google Drive Integration Module

This module handles all interactions with Google Drive:
- Authenticating with Google's API
- Creating folders in Drive
- Uploading files to Drive

Key Concepts:
- OAuth 2.0: Authentication system that requires user to grant permission once
- Token: Saved credentials so you don't have to authenticate every time
- Service Account: The API client that can interact with Drive
"""

import os
from pathlib import Path

# Third-party imports for Google Drive API
import pickle  # For saving/loading authentication tokens
from googleapiclient.discovery import build  # Builds the Drive API service object
from googleapiclient.http import MediaFileUpload  # For uploading files to Drive
from google_auth_oauthlib.flow import InstalledAppFlow  # OAuth flow for desktop apps
from google.auth.transport.requests import Request  # For refreshing tokens

# Path to store authentication token
# pickle format is a Python-specific binary format for saving objects
pickel_path = Path("token.pickle")  # Note: "pickel" appears to be a typo for "pickle"

def authenticate_drive():
    """
    Authenticate with Google Drive API and return a service object.

    WHAT THIS DOES:
    Handles the authentication process with Google Drive. If you've authenticated before,
    it loads the saved token. Otherwise, it opens a browser for you to sign in.

    HOW IT WORKS:
    1. Checks if we have a saved token (token.pickle)
    2. If token exists and is valid → use it
    3. If token expired → refresh it
    4. If no token → open browser for new authentication
    5. Save token for next time
    6. Return a service object that can interact with Drive

    Returns:
        Service object: A Google Drive API service that can create folders, upload files, etc.
    
    EXAMPLE:
        service = authenticate_drive()
        # First time: Browser opens, you sign in, grant permissions
        # Next time: Uses saved token, no browser needed
    
    IMPORTANT CONCEPTS:
        - OAuth 2.0: Secure authentication that doesn't require storing passwords
        - Scopes: Define what permissions we're asking for (full Drive access)
        - Token: Encrypted credentials that prove we have permission
        - Refresh: Tokens expire; refresh gets a new one without re-authenticating
    """
    # Define what permissions we need from Google Drive
    # This scope gives full read/write access to Drive
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    
    creds = None  # Will store credentials object
    
    # Check if we have a saved token from a previous authentication
    if pickel_path.exists():
        # Load the saved credentials from the pickle file
        # read_bytes() reads the file as binary data
        # pickle.loads() converts binary data back into Python object
        creds = pickle.loads(pickel_path.read_bytes())
    
    # Check if credentials are valid
    if not creds or not creds.valid:
        # Credentials are missing or invalid
        
        # If credentials exist but are expired, try to refresh them
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token - gets new access token without user interaction
            creds.refresh(Request())
        else:
            # No valid credentials - need to authenticate from scratch
            # This will open a browser window for user to sign in
            
            # Create OAuth flow from credentials file
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            
            # Run the authentication flow
            # port=0 means "pick any available port"
            # Opens browser, user signs in, grants permissions
            creds = flow.run_local_server(port=0)
        
        # Save the credentials (or refreshed credentials) for next time
        # pickle.dumps() converts Python object to binary data
        # write_bytes() writes binary data to file
        pickel_path.write_bytes(pickle.dumps(creds))
    
    # Build and return the Drive API service object
    # "drive" = service name
    # "v3" = API version
    # credentials = our authenticated credentials
    # This service object is what we use to make API calls
    return build("drive", "v3", credentials=creds)


def create_drive_directory(service, name, parent_id=None):
    """
    Create a folder in Google Drive.

    WHAT THIS DOES:
    Creates a new folder in Google Drive with the specified name.
    Optionally, can create it inside another folder (parent folder).

    HOW IT WORKS:
    1. Sets up folder metadata (name and type)
    2. If parent_id provided, sets it as the parent (nested folder)
    3. Calls Google Drive API to create the folder
    4. Returns the folder's ID (needed for uploading files into it)

    Args:
        service: Google Drive API service object (from authenticate_drive())
        name (str): Name of the folder to create (e.g., "My Notebook")
        parent_id (str, optional): ID of parent folder if creating nested folder
                                   None = create in Drive root

    Returns:
        str: The ID of the newly created folder
        This ID is needed to upload files into this folder later.

    EXAMPLE:
        folder_id = create_drive_directory(service, "Work Notes")
        # Creates "Work Notes" folder in Drive root
        # Returns something like "1a2b3c4d5e6f7g8h9i0j"
        
        subfolder_id = create_drive_directory(service, "2024", parent_id=folder_id)
        # Creates "2024" folder inside "Work Notes"
    
    IMPORTANT:
        - Google Drive uses IDs, not paths, to identify folders
        - Every folder/file gets a unique ID when created
        - We need this ID to reference the folder later
    """
    print("Creating folder:", name)
    
    # Set up metadata for the folder
    # In Google Drive API, folders are just files with a special MIME type
    file_metadata = {
        "name": name,  # The folder name
        "mimeType": "application/vnd.google-apps.folder"  # Tells Drive this is a folder
    }
    
    # If parent_id is provided, set it as the parent folder
    # This makes the new folder a subfolder of the parent
    if parent_id:
        file_metadata["parents"] = [parent_id]  # Must be a list
    
    # Create the folder using Google Drive API
    # service.files() = files and folders API
    # .create() = create new item
    # body = metadata (name, type, parent)
    # fields="id" = only return the ID (more efficient than returning all metadata)
    # .execute() = actually make the API call
    folder = service.files().create(body=file_metadata, fields="id").execute()
    
    # Return the folder ID (we'll need this to upload files into the folder)
    return folder["id"]


def upload_file(service, file_path: Path, parent_id: str):
    """
    Upload a single file to Google Drive.

    WHAT THIS DOES:
    Uploads a file from your computer to Google Drive, placing it in the
    specified folder (identified by parent_id).

    HOW IT WORKS:
    1. Sets up file metadata (name and parent folder)
    2. Creates a media upload object (handles the file transfer)
    3. Calls Google Drive API to upload the file
    4. File appears in Drive inside the specified folder

    Args:
        service: Google Drive API service object (from authenticate_drive())
        file_path (Path): Path to the file on your computer to upload
        parent_id (str): ID of the Drive folder where file should be uploaded

    EXAMPLE:
        service = authenticate_drive()
        folder_id = create_drive_directory(service, "My Notes")
        upload_file(service, Path("./My Notes/note.pdf"), folder_id)
        # Uploads note.pdf into "My Notes" folder in Drive
    
    IMPORTANT CONCEPTS:
        - resumable=True: Allows upload to resume if interrupted (good for large files)
        - parent_id: Must be a valid folder ID from create_drive_directory()
        - This only uploads ONE file - use upload_directory() for multiple files
    """
    print("Uploading file:", file_path.name, "from the directory:", file_path.parent)
    
    # Get just the filename (without path)
    # Example: Path("./Notes/note.pdf") → file_name = "note.pdf"
    file_name = file_path.name
    
    # Set up metadata for the file
    file_metadata = {
        "name": file_name,        # Name in Drive (usually same as filename)
        "parents": [parent_id]    # Which folder to upload into
    }
    
    # Create media upload object
    # MediaFileUpload handles the actual file transfer
    # resumable=True means if upload fails, it can resume from where it stopped
    # This is important for large files
    media = MediaFileUpload(file_path, resumable=True)
    
    # Upload the file to Google Drive
    # service.files() = files API
    # .create() = create new file
    # body = file metadata (name, parent)
    # media_body = the actual file to upload
    # fields="id" = only return ID (more efficient)
    # .execute() = make the API call
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()


def upload_directory(service, local_path: Path, parent_id: str | None = None):
    """
    Upload an entire directory (folder) and its contents to Google Drive recursively.

    WHAT THIS DOES:
    Takes a folder on your computer and recreates its entire structure in Google Drive,
    uploading all files and subfolders. This is a recursive function that processes
    nested folders.

    HOW IT WORKS:
    1. Creates a folder in Drive matching the local folder name
    2. Loops through all items in the local folder
    3. For each subfolder: recursively call upload_directory() (processes nested folders)
    4. For each file: upload it to the Drive folder
    5. Result: Complete folder structure replicated in Drive

    Args:
        service: Google Drive API service object (from authenticate_drive())
        local_path (Path): Path to the local folder to upload (e.g., Path("./EverNote Notes"))
        parent_id (str | None): ID of parent folder in Drive (None = upload to Drive root)

    EXAMPLE:
        service = authenticate_drive()
        upload_directory(service, Path("./EverNote Notes"))
        # Recreates entire "EverNote Notes" folder structure in Drive
        
        Structure on computer:
        EverNote Notes/
          Notebook1/
            note1.pdf
            note2.pdf
          Notebook2/
            note3.pdf
        
        Result in Drive: Same structure exactly!
    
    IMPORTANT CONCEPTS:
        - Recursive function: Calls itself to handle nested folders
        - iterdir(): Gets all items (files and folders) in a directory
        - is_dir(): Checks if an item is a folder (vs a file)
        - This maintains the exact folder structure from your computer
    
    RECURSION EXPLANATION:
        When it finds a subfolder, it calls itself (upload_directory) with that subfolder.
        This continues until all nested folders are processed.
        Example:
        - Upload "EverNote Notes" → creates folder
        - Finds "Notebook1" subfolder → calls upload_directory("Notebook1")
          - Creates "Notebook1" in Drive
          - Finds "note1.pdf" → uploads it
          - Done with "Notebook1"
        - Continues with next item...
    """
    # Get the name of the folder we're uploading
    # Example: Path("./EverNote Notes") → folder_name = "EverNote Notes"
    folder_name = local_path.name
    
    # Create a folder in Drive with this name
    # parent_id determines where it goes (None = Drive root)
    # Returns the new folder's ID (needed to upload files into it)
    folder_id = create_drive_directory(service, folder_name, parent_id)
    
    # Loop through all items in the local folder
    # iterdir() returns both files and subfolders
    for item in local_path.iterdir():
        # Check if this item is a directory (folder)
        if item.is_dir():
            # It's a subfolder - process it recursively
            # This calls upload_directory() again with:
            # - The subfolder path
            # - The parent folder ID (the folder we just created)
            # This will create the subfolder in Drive and process its contents
            upload_directory(service, item, folder_id)
        else:
            # It's a file - upload it to the Drive folder we created
            upload_file(service, item, folder_id)
    
    # After this function completes, the entire folder structure is uploaded!

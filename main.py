"""
Evernote to Google Drive Migrator - Main Entry Point

This script processes Evernote ENEX export files and converts them to PDFs,
then optionally uploads them to Google Drive while preserving notebook structure.

Key Concepts:
- ENEX files are XML files containing notes from Evernote
- Each notebook is exported as a separate .enex file
- Notes can contain text, images, PDFs, and other attachments
- The script organizes output by notebook name and adds unique IDs to each note
"""

# Standard library imports - these come with Python
import argparse  # For parsing command-line arguments (like --dry-run)
import base64  # For decoding base64-encoded file data from ENEX files
import json  # For reading/writing JSON log files
import mimetypes  # For guessing file extensions from MIME types
import os  # For checking if files exist
import xml.etree.ElementTree as ET  # For parsing XML content in ENEX files
from pathlib import Path  # Modern way to handle file paths (better than os.path)

# Local imports - these are files in the same project
from gdrive import authenticate_drive, upload_directory  # Functions for Google Drive integration
from pdf_utils import (
    create_multi_item_pdf,  # Merges text + images/PDFs into one PDF
    create_text_pdf,  # Converts plain text to PDF
    generate_unique_id,  # Creates unique 6-character IDs for notes
    should_create_multi_item_pdf,  # Decides if we need a multi-item PDF
)


def load_extraction_log(log_file: Path) -> dict:
    """
    Load the extraction log from a JSON file.
    If the log file doesn't exist, create an empty one.

    WHAT THIS DOES:
    This function loads a JSON file that tracks which notes have been processed.
    Think of it like a diary that remembers what we've already done.

    HOW IT WORKS:
    1. Checks if the log file exists
    2. If not, creates an empty JSON file with just "{}" (empty dictionary)
    3. If it exists, reads and parses the JSON
    4. Returns the data as a Python dictionary

    Args:
        log_file (Path): Path to the log file (e.g., "./extraction_log.json")

    Returns:
        dict: A dictionary containing the log data. Empty dict {} if file doesn't exist
              or if there's an error reading it.

    EXAMPLE:
        log_file = Path("./extraction_log.json")
        logs = load_extraction_log(log_file)
        # logs might be: {"Notebook1": [{"note": "My Note", "success": True}]}
    """
    # Check if the log file exists on the filesystem
    if not log_file.exists():
        # File doesn't exist - create an empty JSON file
        # "{}" represents an empty dictionary in JSON format
        log_file.write_text("{}")
        return {}  # Return empty dictionary

    # Try to read and parse the JSON file
    try:
        # json.loads() converts a JSON string into a Python dictionary
        # read_text() reads the entire file as a string
        return json.loads(log_file.read_text())
    except Exception:
        # If anything goes wrong (corrupted file, invalid JSON, etc.),
        # return an empty dictionary instead of crashing
        return {}


def list_enex_files(input_dir: Path) -> list[Path]:
    """
    List all .enex files in the input directory.

    WHAT THIS DOES:
    Scans a directory and finds all files ending in .enex (Evernote export files).

    HOW IT WORKS:
    1. Uses iterdir() to get all files/folders in the directory
    2. Checks each item's suffix (file extension)
    3. Converts to lowercase for case-insensitive matching (.ENEX = .enex)
    4. Returns only files that match ".enex"

    Args:
        input_dir (Path): The directory to search in (e.g., Path("./input_data"))

    Returns:
        list[Path]: A list of Path objects pointing to .enex files

    EXAMPLE:
        input_dir = Path("./input_data")
        files = list_enex_files(input_dir)
        # files might be: [Path("./input_data/Notebook1.enex"), Path("./input_data/Notebook2.enex")]

    NOTE:
        This uses a "list comprehension" - a concise Python way to filter items.
        Equivalent longer code:
            files = []
            for f in input_dir.iterdir():
                if f.suffix.lower() == ".enex":
                    files.append(f)
            return files
    """
    # List comprehension: create a list by iterating and filtering
    # f.suffix gets the file extension (e.g., ".enex", ".txt")
    # .lower() makes it case-insensitive (".ENEX" becomes ".enex")
    return [f for f in input_dir.iterdir() if f.suffix.lower() == ".enex"]


def get_unique_filepath(base_path: Path, logs: dict) -> Path:
    """
    Ensure a unique file path by adding a counter suffix if the file already exists.

    This prevents silent data loss when --no-serial is used and multiple notes
    have the same title in a notebook.

    Args:
        base_path: The initial desired file path (e.g., "My Note.pdf")
        logs: Logging dictionary to record collision warnings

    Returns:
        Path: A unique file path (e.g., "My Note.pdf" or "My Note_1.pdf" or "My Note_2.pdf")

    Example:
        If "Vacation.pdf" exists:
        - First call: Returns "Vacation.pdf"
        - Second call: Returns "Vacation_1.pdf" (logs warning)
        - Third call: Returns "Vacation_2.pdf" (logs warning)
    """
    if not base_path.exists():
        return base_path

    # File exists - need to find a unique name
    stem = base_path.stem  # Filename without extension (e.g., "My Note")
    suffix = base_path.suffix  # Extension (e.g., ".pdf")
    parent = base_path.parent  # Directory

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            # Log collision warning
            warning_msg = f"File collision: '{base_path.name}' already exists, using '{new_path.name}'"
            print(f"⚠️  WARNING: {warning_msg}")
            logs.setdefault("warnings", []).append({
                "type": "filename-collision",
                "original": base_path.name,
                "deduped": new_path.name,
                "message": warning_msg
            })
            return new_path
        counter += 1


def process_enex_file(file: Path, output_dir: Path, logs: dict, preserve_filenames: bool = False):
    """
    Process a single ENEX file and extract its notes.

    WHAT THIS DOES:
    Opens an ENEX file (which is XML format), parses it, finds all notes inside,
    and processes each note one by one. Think of it as opening a notebook and
    going through each page.

    HOW IT WORKS:
    1. Gets the notebook name from the filename (without .enex extension)
    2. Creates an empty list in logs for this notebook
    3. Parses the XML file to extract all <note> elements
    4. Loops through each note and processes it
    5. If anything goes wrong, logs the error and stops

    Args:
        file (Path): Path to the ENEX file to process (e.g., Path("./input_data/MyNotebook.enex"))
        output_dir (Path): Where to save the extracted notes (e.g., Path("./EverNote Notes"))
        logs (dict): Dictionary that accumulates processing results for logging
        preserve_filenames (bool): If True, skip serial number prefix on filenames (default: False)

    EXAMPLE:
        file = Path("./input_data/WorkNotes.enex")
        output_dir = Path("./EverNote Notes")
        logs = {}
        process_enex_file(file, output_dir, logs, preserve_filenames=False)
        # This will create "./EverNote Notes/WorkNotes/" and process all notes in the file

    NOTE:
        file.stem gives the filename without extension
        "MyNotebook.enex" → stem = "MyNotebook"
    """
    # Get notebook name from filename (remove .enex extension)
    # Example: "MyNotebook.enex" → notebook_name = "MyNotebook"
    notebook_name = file.stem

    # Initialize an empty list in logs dictionary for this notebook
    # This will store information about each processed note
    logs[notebook_name] = []

    # Try to parse the XML file - ENEX files are XML format
    try:
        # ET.parse() reads and parses the XML file into a tree structure
        tree = ET.parse(file)

        # getroot() gets the root element, findall("note") finds all <note> tags
        # Each <note> tag represents one note from Evernote
        notes = tree.getroot().findall("note")
    except Exception as e:
        # If parsing fails (corrupted file, invalid XML, etc.), log the error
        logs[notebook_name].append({
            "file": file.name,        # Just the filename, not full path
            "error": str(e),          # Convert exception to string
            "notebook": notebook_name
        })
        return  # Stop processing this file

    # Process each note in the ENEX file
    # This loops through all the <note> elements we found
    for note in notes:
        process_note(note, notebook_name, file, output_dir, logs, preserve_filenames)


def process_note(note, notebook_name, file, output_dir, logs, preserve_filenames=False):
    """
    Process a single note: extract text and resources, create PDFs with unique IDs.

    WHAT THIS DOES:
    Takes one note from the ENEX file, extracts its title, text content, and attachments,
    then decides how to save it based on what it contains. This is the "brain" function
    that routes notes to the right handler based on their content.

    HOW IT WORKS:
    1. Extracts the note's title (required - skip note if missing)
    2. Generates a unique ID for the note
    3. Extracts text content (if any)
    4. Finds all resources/attachments (images, PDFs, etc.)
    5. Creates the output directory for this notebook
    6. Decides which handler function to call based on content:
       - Multi-item: text + multiple resources OR text + 1+ resources
       - Single resource: just one attachment, no text
       - Text-only: just text, no attachments

    Args:
        note (Element): XML element representing one note from the ENEX file
        notebook_name (str): Name of the notebook this note belongs to
        file (Path): Path to the source ENEX file (for logging)
        output_dir (Path): Base directory where all notebooks will be saved
        logs (dict): Dictionary to log processing results

    EXAMPLE:
        A note might contain:
        - Title: "Meeting Notes"
        - Text: "Discussed project timeline..."
        - Resources: [image1.jpg, document.pdf]
        → This becomes a multi-item PDF

    IMPORTANT CONCEPTS:
        - safe_title: Removes characters that can't be in filenames (like "/")
        - note_id: Unique identifier to prevent filename conflicts
        - resources: Attachments like images, PDFs, videos, etc.
    """
    # Extract the note's title from the XML
    # findtext() searches for a tag and returns its text content
    title = note.findtext("title")

    # If there's no title, skip this note (can't create a file without a name)
    if not title:
        return  # Exit early - nothing to process

    # Generate a unique 6-character ID for this note (unless preserve_filenames is True)
    # Example: "A3B9K2" - helps prevent filename conflicts
    # If preserve_filenames is True, use empty string (no prefix)
    note_id = "" if preserve_filenames else generate_unique_id()

    # Make the title safe for filesystem use
    # "/" is not allowed in filenames on most systems, so replace with "-"
    # Replace "--" with "-" to avoid double dashes
    safe_title = title.replace("/", "-").replace("--", "-")

    # Find all resource elements in the note
    # Resources are attachments like images, PDFs, videos, etc.
    resources = note.findall("resource")

    # Find the content element which contains the note's text
    content_element = note.find("content")
    text_content = None  # Will store extracted text if available

    # Try to extract text from the content element
    # The content is stored as XML/HTML-like text, so we need to parse it
    if content_element is not None and content_element.text is not None:
        try:
            # Parse the content XML to extract plain text
            # strip() removes leading/trailing whitespace
            content_root = ET.fromstring(content_element.text.strip())

            # itertext() gets all text from all XML elements
            # join with "\n" puts each text block on a new line
            text_content = "\n".join(content_root.itertext()).strip()
        except ET.ParseError:
            # If the content isn't valid XML, just skip text extraction
            # The note might still have resources to process
            pass

    # Create the output directory for this notebook
    # Example: output_dir / "MyNotebook" → "./EverNote Notes/MyNotebook"
    # mkdir(parents=True) creates parent directories if they don't exist
    # exist_ok=True means don't error if directory already exists
    note_dir = output_dir / notebook_name
    note_dir.mkdir(parents=True, exist_ok=True)

    # Decide how to handle this note based on its content
    # should_create_multi_item_pdf() checks if we have multiple items to combine
    if should_create_multi_item_pdf(text_content, len(resources)):
        # This note has multiple resources OR both text and resources
        # Create a single PDF with everything merged together
        handle_multi_item_note(
            note_id, safe_title, text_content, resources,
            note_dir, file, notebook_name, logs
        )
    else:
        # This note is simpler - either one resource or just text
        if resources:
            # Note has one attachment (image, PDF, etc.) - save it as-is
            handle_single_resource(
                note_id, safe_title, resources[0],  # Only process first resource
                note_dir, file, notebook_name, logs
            )
        elif text_content:
            # Note has only text, no attachments - convert to PDF
            handle_text_only_note(
                note_id, safe_title, text_content,
                note_dir, file, notebook_name, logs
            )
        # Note: If note has neither text nor resources, nothing happens


def handle_multi_item_note(
    note_id, safe_title, text_content, resources,
    note_dir, file, notebook_name, logs
):
    """
    Handle notes with multiple items - merge supported files into PDF, save others separately.

    WHAT THIS DOES:
    Processes notes that have multiple attachments or both text and attachments.
    Creates a single PDF combining text and supported file types (images, PDFs).
    Unsupported files (videos, ZIP files, etc.) are saved separately.

    HOW IT WORKS:
    1. Extracts all resources from the note and saves them as temporary files
    2. Decodes base64-encoded data from the ENEX file
    3. Creates a multi-item PDF with text + supported resources
    4. Saves unsupported files separately
    5. Cleans up temporary files

    Args:
        note_id (str): Unique identifier like "A3B9K2"
        safe_title (str): Note title safe for filesystem
        text_content (str): Plain text content from the note (can be None)
        resources (list): List of XML resource elements (attachments)
        note_dir (Path): Where to save the final files
        file (Path): Source ENEX file path
        notebook_name (str): Name of the notebook
        logs (dict): Dictionary for logging results

    EXAMPLE:
        Note with:
        - Text: "Meeting notes"
        - Image1.jpg
        - Image2.png
        - Video.mp4 (unsupported)

        Result:
        - "A3B9K2 - Meeting notes-MultiItem.pdf" (contains text + images)
        - "A3B9K2 - Meeting notes-Video.mp4" (saved separately)

    IMPORTANT:
        - Resources in ENEX files are base64-encoded (text representation of binary data)
        - We decode them to get the actual files
        - Temporary files are cleaned up in the "finally" block (always runs)
    """
    # List to store paths of temporary resource files we create
    temp_resource_paths = []

    # Create a temporary directory to store extracted resources
    # The ".temp_resources" prefix with dot makes it a hidden folder (optional)
    temp_dir = note_dir / ".temp_resources"
    temp_dir.mkdir(exist_ok=True)  # Create directory, don't error if exists

    # Use try/finally to ensure cleanup happens even if errors occur
    try:
        # Loop through each resource (attachment) in the note
        # enumerate() gives us both the index (idx) and the resource element
        for idx, res in enumerate(resources):
            # Find the "data" element - contains the actual file data (base64-encoded)
            data_element = res.find("data")

            # Find the "mime" element - tells us the file type (e.g., "image/jpeg")
            mime_element = res.find("mime")

            # Skip this resource if it's missing required data
            if data_element is None or mime_element is None:
                continue  # Go to next resource

            # Get the MIME type (e.g., "image/jpeg", "application/pdf")
            mime_type = mime_element.text

            # Skip if MIME type or data is missing
            if not mime_type or not data_element.text:
                continue

            # Convert MIME type to file extension
            # Example: "image/jpeg" → ".jpg"
            # strict=True means only return extensions if we're confident
            # or "" means return empty string if we can't guess
            extension = mimetypes.guess_extension(mime_type, strict=True) or ""

            # Create a temporary filename for this resource
            # Example: "resource_0.jpg", "resource_1.png"
            temp_file_name = f"resource_{idx}{extension}"
            temp_file_path = temp_dir / temp_file_name

            # Try to decode and save the resource
            try:
                # Decode base64-encoded data to get binary file data
                # ENEX files store binary data as text using base64 encoding
                binary_data = base64.b64decode(data_element.text)

                # Write the binary data to a temporary file
                temp_file_path.write_bytes(binary_data)

                # Remember this file path for later processing
                temp_resource_paths.append(temp_file_path)
            except Exception as e:
                # If decoding fails, print error and continue with next resource
                print(f"Error decoding resource: {e}")
                continue  # Skip this resource, try next one

        # Create the final PDF filename
        # With serial: "A3B9K2 - Meeting Notes-MultiItem.pdf"
        # Without serial: "Meeting Notes-MultiItem.pdf"
        if note_id:
            output_pdf_path = note_dir / f"{note_id} - {safe_title}-MultiItem.pdf"
        else:
            output_pdf_path = note_dir / f"{safe_title}-MultiItem.pdf"

        # Ensure unique filepath (adds _1, _2 suffix if collision occurs)
        output_pdf_path = get_unique_filepath(output_pdf_path, logs)

        # Try to create the multi-item PDF
        try:
            # This function combines text + supported resources into one PDF
            # Returns: (success_boolean, list_of_unsupported_files)
            success, unsupported_files = create_multi_item_pdf(
                text_content,           # Text to include (can be None)
                temp_resource_paths,    # List of temporary resource files
                output_pdf_path         # Where to save the final PDF
            )

            # If PDF was created successfully, log it
            if success:
                logs[notebook_name].append({
                    "file": file.name,           # Source ENEX filename
                    "note": safe_title,          # Note title
                    "note_id": note_id,          # Unique ID
                    "success": True,             # Processing succeeded
                    "file_path": str(output_pdf_path),  # Full path to created PDF
                    "notebook": notebook_name,   # Which notebook
                    "type": "multi-item-pdf",    # Type of output
                })
                print(f"✓ Created multi-item PDF: {output_pdf_path.name}")

            # Handle unsupported files (videos, ZIP files, etc.)
            # These can't be merged into PDF, so save them separately
            if unsupported_files:
                print(f"⚠️  Note '{safe_title}' has {len(unsupported_files)} unsupported file(s) - saving separately")

                # Move each unsupported file from temp directory to final location
                for unsupported_file in unsupported_files:
                    # Create new filename with note ID prefix (if enabled)
                    # With serial: "A3B9K2 - Meeting Notes-Video.mp4"
                    # Without serial: "Meeting Notes-Video.mp4"
                    if note_id:
                        separate_file_path = note_dir / f"{note_id} - {safe_title}-{unsupported_file.name}"
                    else:
                        separate_file_path = note_dir / f"{safe_title}-{unsupported_file.name}"

                    # Ensure unique filepath (adds _1, _2 suffix if collision occurs)
                    separate_file_path = get_unique_filepath(separate_file_path, logs)

                    # rename() moves the file to new location
                    unsupported_file.rename(separate_file_path)

                    # Log this separately saved file
                    logs[notebook_name].append({
                        "file": file.name,
                        "note": safe_title,
                        "note_id": note_id,
                        "success": True,
                        "file_path": str(separate_file_path),
                        "notebook": notebook_name,
                        "type": "unsupported-separate-file",
                        "warning": "File type not supported in PDF merge - saved separately"
                    })
                    print(f"  → Saved separately: {separate_file_path.name}")

        except Exception as e:
            # If PDF creation fails, log the error
            logs[notebook_name].append({
                "file": file.name,
                "note": safe_title,
                "note_id": note_id,
                "success": False,  # Mark as failed
                "notebook": notebook_name,
                "error": f"PDF creation failed: {str(e)}"  # Save error message
            })
            print(f"✗ Error creating multi-item PDF for {safe_title}: {e}")

    finally:
        # CLEANUP: This block always runs, even if errors occurred above
        # This ensures we don't leave temporary files lying around

        # Delete temporary resource files
        for temp_file in temp_resource_paths:
            try:
                # Only delete if file exists and is still in temp directory
                # (it might have been moved if it was unsupported)
                if temp_file.exists() and temp_file.parent == temp_dir:
                    temp_file.unlink()  # Delete the file
            except Exception:
                # If deletion fails (permissions, etc.), just continue
                pass

        # Remove the temporary directory if it's empty
        try:
            # Check if directory exists and has no files
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()  # Remove empty directory
        except Exception:
            # If removal fails, continue anyway
            pass


def handle_single_resource(
    note_id, safe_title, resource,
    note_dir, file, notebook_name, logs
):
    """
    Handle notes with a single resource (no text or only one attachment).

    WHAT THIS DOES:
    Processes notes that have exactly one attachment (like a single image or PDF)
    and no text content. Saves the file as-is with the note's ID and title.

    HOW IT WORKS:
    1. Extracts the resource data and MIME type from XML
    2. Determines the file extension from MIME type
    3. Decodes base64 data to binary
    4. Saves the file with ID prefix

    Args:
        note_id (str): Unique identifier for the note
        safe_title (str): Note title safe for filesystem
        resource (Element): XML element containing one resource/attachment
        note_dir (Path): Directory where the file should be saved
        file (Path): Source ENEX file path
        notebook_name (str): Name of the notebook
        logs (dict): Dictionary for logging results

    EXAMPLE:
        Note: "Vacation Photo" with one image.jpg
        Result: "A3B9K2 - Vacation Photo.jpg" saved in notebook directory

    NOTE:
        This function doesn't convert to PDF - it saves the original file format.
        The file is saved as-is (image stays as image, PDF stays as PDF, etc.)
    """
    # Extract data and MIME type from the resource XML element
    data_element = resource.find("data")  # Contains base64-encoded file data
    mime_element = resource.find("mime")  # Contains MIME type like "image/jpeg"

    # Validate that we have both required elements
    if data_element is None or mime_element is None:
        # Log error and exit - can't process without data and type info
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": "Missing mime type or resource data"
        })
        return  # Can't continue without this information

    # Get the actual MIME type string and check it's not empty
    mime_type = mime_element.text
    if not mime_type or not data_element.text:
        # MIME type or data is missing - log error and exit
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": "Missing mime type or resource data"
        })
        return

    # Convert MIME type to file extension
    # Example: "image/jpeg" → ".jpg", "application/pdf" → ".pdf"
    extension = mimetypes.guess_extension(mime_type, strict=True) or ""

    # Create filename: "ID - Title.extension" or just "Title.extension" if preserving
    # With serial: "A3B9K2 - Vacation Photo.jpg"
    # Without serial: "Vacation Photo.jpg"
    if note_id:
        file_name = f"{note_id} - {safe_title}{extension}"
    else:
        file_name = f"{safe_title}{extension}"
    file_path = note_dir / file_name

    # Ensure unique filepath (adds _1, _2 suffix if collision occurs)
    file_path = get_unique_filepath(file_path, logs)

    # Try to decode and save the file
    try:
        # Decode base64-encoded data to get binary file content
        binary_data = base64.b64decode(data_element.text)
        file_path.write_bytes(binary_data)

        # Log successful save
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": True,
            "file_path": str(file_path),
            "notebook": notebook_name,
            "type": "single-resource",  # Mark as single resource type
        })
        print(f"Saved single resource: {file_path.name}")

    except Exception as e:
        # If anything goes wrong (decoding error, write permission, etc.)
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": f"Base64 decoding or file write failed: {str(e)}"
        })


def handle_text_only_note(
    note_id, safe_title, text_content,
    note_dir, file, notebook_name, logs
):
    """
    Handle notes with only text content (no attachments).

    WHAT THIS DOES:
    Processes notes that contain only text (like a written note or memo)
    with no images or other attachments. Converts the text to a PDF file.

    HOW IT WORKS:
    1. Creates a PDF filename with the note ID and title
    2. Calls create_text_pdf() to convert text to PDF format
    3. Logs the result (success or failure)

    Args:
        note_id (str): Unique identifier for the note
        safe_title (str): Note title safe for filesystem use
        text_content (str): The plain text content of the note
        note_dir (Path): Directory where the PDF should be saved
        file (Path): Source ENEX file path (for logging)
        notebook_name (str): Name of the notebook
        logs (dict): Dictionary for logging results

    EXAMPLE:
        Note: "Shopping List" with text "Milk, Eggs, Bread..."
        Result: "A3B9K2-Shopping List.pdf" created in notebook directory

    NOTE:
        All text-only notes are converted to PDF format for consistency.
        The PDF uses standard formatting (11pt font, letter-sized pages).
    """
    # Create the PDF filename
    # With serial: "ID-Title.pdf" (note: no space after ID, different from other handlers)
    # Example: "A3B9K2-Shopping List.pdf"
    # Without serial: "Title.pdf"
    # Example: "Shopping List.pdf"
    if note_id:
        file_path = note_dir / f"{note_id}-{safe_title}.pdf"
    else:
        file_path = note_dir / f"{safe_title}.pdf"

    # Ensure unique filepath (adds _1, _2 suffix if collision occurs)
    file_path = get_unique_filepath(file_path, logs)

    # Try to create the PDF
    try:
        # Convert the text content to a PDF file
        # This function handles all the PDF formatting (fonts, margins, pages, etc.)
        create_text_pdf(text_content, file_path)

        # Log successful PDF creation
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": True,
            "file_path": str(file_path),
            "notebook": notebook_name,
            "type": "text-only-pdf",  # Mark as text-only type
        })
        print(f"Created text-only PDF: {file_path.name}")

    except Exception as e:
        # If PDF creation fails, log the error
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": f"PDF creation failed: {str(e)}"
        })
        print(f"Error creating text-only PDF for {safe_title}: {e}")


def process_files(output_directory: Path, dry_run: bool, preserve_filenames: bool = False) -> None:
    """
    Main driver function: Processes ENEX files and optionally uploads to Google Drive.

    WHAT THIS DOES:
    This is the main orchestrator function that:
    1. Finds all ENEX files in the input directory
    2. Processes each ENEX file (which processes each note)
    3. Saves logs of all processing
    4. Optionally uploads everything to Google Drive

    HOW IT WORKS:
    - Sets up input/output directories
    - Loads or creates extraction log
    - Processes all ENEX files sequentially
    - Saves logs to JSON file
    - Uploads to Google Drive (unless dry_run is True)

    Args:
        output_directory (Path): Where to save extracted notes (e.g., Path("./EverNote Notes"))
        dry_run (bool): If True, process files but skip Google Drive upload
                       Useful for testing without actually uploading

    EXAMPLE:
        process_files(Path("./My Notes"), dry_run=False)
        # Processes all ENEX files and uploads to Google Drive

    FLOW:
        1. Check input directory exists
        2. Create output directory
        3. Find all .enex files
        4. Process each file → extracts notes → creates PDFs/files
        5. Save logs
        6. Upload to Google Drive (if not dry run)
    """
    # Inform user where files will be saved
    print(f"[INFO] Processing notes into: {output_directory}")

    # Inform user if we're in test mode (dry run)
    if dry_run:
        print("[INFO] Dry run mode enabled — Google Drive syncing will be skipped.")

    # Define paths - these are relative to where you run the script from
    input_directory = Path("./input_data")  # Where ENEX files are stored
    extraction_log_file = Path("./extraction_log.json")  # Log file for tracking progress

    # Load existing log file (or create empty one if it doesn't exist)
    logs_json = load_extraction_log(extraction_log_file)

    # Validate that input directory exists
    if not input_directory.exists():
        # Raise an exception (crash) with helpful error message
        raise FileNotFoundError("Input directory does not exist")

    # Create output directory if it doesn't exist
    # parents=True creates parent directories too
    # exist_ok=True means don't error if it already exists
    output_directory.mkdir(parents=True, exist_ok=True)

    # Find all ENEX files in the input directory
    files = list_enex_files(input_directory)

    # Check if we found any files to process
    if not files:
        print("No ENEX files found.")
        return  # Exit early - nothing to do

    # Process each ENEX file
    # Each file represents one notebook from Evernote
    for file in files:
        # This processes the entire ENEX file and all notes within it
        process_enex_file(file, output_directory, logs_json, preserve_filenames)

    # Save all the logs we've accumulated to the JSON file
    finalize_logs(logs_json, extraction_log_file)

    # Handle Google Drive upload (if not in dry-run mode)
    if dry_run:
        # Dry run - just tell user we're done, no upload
        print("Dry run complete. No files were uploaded.")
    elif os.path.exists("credentials.json"):
        # Credentials file exists - proceed with upload
        # First, authenticate with Google Drive
        service_account = authenticate_drive()

        # Upload the entire output directory to Google Drive
        # This recreates the folder structure in Drive
        upload_directory(service_account, output_directory)
    elif not os.path.exists("credentials.json"):
        # Credentials file missing - raise helpful error
        raise FileNotFoundError("""credentials.json not found!.
Please create a credentials.json file in the root directory of the project.
Google Drive API documentation: https://developers.google.com/drive/api/v3/quickstart/python
""")

def finalize_logs(logs_json: dict, log_file: Path):
    """
    Save the logs dictionary to a JSON file.

    WHAT THIS DOES:
    Takes all the log data we've collected and writes it to a JSON file.
    This creates a permanent record of what was processed.

    HOW IT WORKS:
    - Converts the Python dictionary to JSON string
    - Formats it nicely with indentation (indent=4)
    - Writes it to the log file

    Args:
        logs_json (dict): Dictionary containing all processing logs
        log_file (Path): Path to the JSON log file to create/overwrite

    EXAMPLE:
        logs = {"Notebook1": [{"note": "My Note", "success": True}]}
        finalize_logs(logs, Path("./extraction_log.json"))
        # Creates extraction_log.json with formatted JSON
    """
    # json.dumps() converts Python dict to JSON string
    # indent=4 makes it readable (4 spaces per indentation level)
    # write_text() overwrites the file with new content
    log_file.write_text(json.dumps(logs_json, indent=4))


# This block only runs when the script is executed directly (not when imported)
# If someone imports this file as a module, this code won't run
if __name__ == "__main__":
    """
    COMMAND-LINE INTERFACE SETUP

    This section sets up the command-line interface using argparse.
    Users can run: python main.py --dry-run --output-directory "./My Notes"

    Key concepts:
    - argparse: Python library for parsing command-line arguments
    - --dry-run: Flag that skips Google Drive upload
    - --output-directory: Option to specify where files are saved
    """

    # Create argument parser with program name and description
    parser = argparse.ArgumentParser(
        prog="Evernote-to-Drive Migrator",
        description=(
            "Exports and processes Evernote ENEX files, replicating notebook structure "
            "into Google Drive. Supports dry-run mode to skip actual upload."
        )
    )

    # Add --output-directory option (also available as -o)
    parser.add_argument(
        "-o", "--output-directory",  # Both -o and --output-directory work
        type=Path,                   # Automatically converts string to Path object
        default=Path("./EverNote Notes"),  # Default value if not specified
        help="Directory where the converted notes will be saved (default: ./EverNote Notes)"
    )

    # Add --dry-run flag (also available as -d)
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",  # If flag is present, set to True; if absent, False
        help="Run without uploading to Google Drive (for testing output structure only)"
    )

    # Add --no-serial or -ns
    parser.add_argument(
        "-ns", "--no-serial",
        action="store_true",  # If flag is present, set to True; if absent, False
        dest="preserve_filenames",  # All flags set the same variable
        help="Preserve original filenames without adding serial number prefix (default: False)"
    )

    # Parse the command-line arguments
    # This reads what the user typed and converts it to Python variables
    args = parser.parse_args()

    # Extract the values from parsed arguments
    output_directory: Path = args.output_directory  # Get output directory path
    dry_run: bool = args.dry_run                    # Get dry-run flag (True or False)
    preserve_filenames: bool = args.preserve_filenames  # Get preserve-filenames flag (True or False)

    # Ensure output directory exists (create if needed)
    output_directory.mkdir(parents=True, exist_ok=True)

    # Run the main processing function with user's arguments
    process_files(output_directory, dry_run, preserve_filenames)

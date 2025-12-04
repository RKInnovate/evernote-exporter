import json
import base64
import argparse
import mimetypes
import urllib.parse
from pathlib import Path
import xml.etree.ElementTree as ET

from gdrive import upload_directory, authenticate_drive
from pdf_utils import (
    generate_unique_id,
    create_multi_item_pdf,
    should_create_multi_item_pdf,
    create_text_pdf
)


def load_extraction_log(log_file: Path) -> dict:
    """
    Load the extraction log from a JSON file.
    If the log file doesn't exist, create an empty one.

    Args:
        log_file (Path): Path to the log file.

    Returns:
        dict: Parsed log content.
    """
    if not log_file.exists():
        log_file.write_text("{}")
        return {}

    try:
        return json.loads(log_file.read_text())
    except Exception:
        return {}


def list_enex_files(input_dir: Path) -> list[Path]:
    """
    List all .enex files in the input directory.

    Args:
        input_dir (Path): Directory to search for .enex files.

    Returns:
        list[Path]: List of .enex files.
    """
    return [f for f in input_dir.iterdir() if f.suffix.lower() == ".enex"]


def process_enex_file(file: Path, output_dir: Path, logs: dict):
    """
    Process a single ENEX file and extract its notes.

    Args:
        file (Path): Path to the ENEX file.
        output_dir (Path): Directory to store extracted notes.
        logs (dict): Log dictionary to store processing metadata.
    """
    notebook_name = file.stem
    logs[notebook_name] = []

    try:
        tree = ET.parse(file)
        notes = tree.getroot().findall("note")
    except Exception as e:
        logs[notebook_name].append({
            "file": file.name, "error": str(e), "notebook": notebook_name
        })
        return

    for note in notes:
        process_note(note, notebook_name, file, output_dir, logs)


def process_note(note, notebook_name, file, output_dir, logs):
    """
    Process a single note: extract text and resources, create PDFs with unique IDs.

    Args:
        note (Element): XML note element.
        notebook_name (str): Name of the notebook.
        file (Path): Source ENEX file.
        output_dir (Path): Target output directory.
        logs (dict): Log dictionary.
    """
    title = note.findtext("title")
    if not title:
        return

    # Generate unique ID for this note
    note_id = generate_unique_id()

    # Make title safe for filesystem
    safe_title = title.replace("/", "-").replace("--", "-")

    resources = note.findall("resource")
    content_element = note.find("content")
    text_content = None

    if content_element is not None and content_element.text is not None:
        try:
            content_root = ET.fromstring(content_element.text.strip())
            text_content = "\n".join(content_root.itertext()).strip()
        except ET.ParseError:
            pass

    # Always place files directly in notebook directory (no nested folders)
    note_dir = output_dir / notebook_name
    note_dir.mkdir(parents=True, exist_ok=True)

    # Determine if we should create a multi-item PDF
    if should_create_multi_item_pdf(text_content, len(resources)):
        handle_multi_item_note(
            note_id, safe_title, text_content, resources,
            note_dir, file, notebook_name, logs
        )
    else:
        # Handle single item or text-only notes
        if resources:
            handle_single_resource(
                note_id, safe_title, resources[0],
                note_dir, file, notebook_name, logs
            )
        elif text_content:
            handle_text_only_note(
                note_id, safe_title, text_content,
                note_dir, file, notebook_name, logs
            )


def handle_multi_item_note(
    note_id, safe_title, text_content, resources,
    note_dir, file, notebook_name, logs
):
    """
    Handle notes with multiple items - merge supported files into PDF, save others separately.

    TODO: Enhanced handling for unsupported file types requires discussion:
    - Should unsupported files be listed in the PDF with links?
    - Generate thumbnails/previews for videos?
    - Convert HTML to PDF with proper rendering?

    Args:
        note_id (str): Unique identifier for the note.
        safe_title (str): Filesystem-safe note title.
        text_content (str): Text content of the note.
        resources (list): List of resource elements.
        note_dir (Path): Directory to save the PDF.
        file (Path): ENEX source file.
        notebook_name (str): Name of the notebook.
        logs (dict): Log dictionary.
    """
    # Extract resources to temporary files
    temp_resource_paths = []
    temp_dir = note_dir / ".temp_resources"
    temp_dir.mkdir(exist_ok=True)

    try:
        for idx, res in enumerate(resources):
            data_element = res.find("data")
            mime_element = res.find("mime")

            if data_element is None or mime_element is None:
                continue

            mime_type = mime_element.text
            if not mime_type or not data_element.text:
                continue

            # Guess file extension from MIME type
            extension = mimetypes.guess_extension(mime_type, strict=True) or ""
            temp_file_name = f"resource_{idx}{extension}"
            temp_file_path = temp_dir / temp_file_name

            try:
                binary_data = base64.b64decode(data_element.text)
                temp_file_path.write_bytes(binary_data)
                temp_resource_paths.append(temp_file_path)
            except Exception as e:
                print(f"Error decoding resource: {e}")
                continue

        # Create multi-item PDF with "MultiItem" keyword (only supported files)
        output_pdf_path = note_dir / f"{note_id} - {safe_title}-MultiItem.pdf"

        try:
            success, unsupported_files = create_multi_item_pdf(
                text_content, temp_resource_paths, output_pdf_path
            )

            if success:
                logs[notebook_name].append({
                    "file": file.name,
                    "note": safe_title,
                    "note_id": note_id,
                    "success": True,
                    "file_path": str(output_pdf_path),
                    "notebook": notebook_name,
                    "type": "multi-item-pdf",
                })
                print(f"✓ Created multi-item PDF: {output_pdf_path.name}")

            # Save unsupported files separately with ID prefix
            if unsupported_files:
                print(f"⚠️  Note '{safe_title}' has {len(unsupported_files)} unsupported file(s) - saving separately")
                for unsupported_file in unsupported_files:
                    separate_file_path = note_dir / f"{note_id} - {safe_title}-{unsupported_file.name}"
                    unsupported_file.rename(separate_file_path)
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
            logs[notebook_name].append({
                "file": file.name,
                "note": safe_title,
                "note_id": note_id,
                "success": False,
                "notebook": notebook_name,
                "error": f"PDF creation failed: {str(e)}"
            })
            print(f"✗ Error creating multi-item PDF for {safe_title}: {e}")

    finally:
        # Clean up temporary files (only ones still in temp directory)
        for temp_file in temp_resource_paths:
            try:
                if temp_file.exists() and temp_file.parent == temp_dir:
                    temp_file.unlink()
            except Exception:
                pass

        # Remove temp directory if empty
        try:
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
        except Exception:
            pass


def handle_single_resource(
    note_id, safe_title, resource,
    note_dir, file, notebook_name, logs
):
    """
    Handle notes with a single resource (no text or only one attachment).

    Args:
        note_id (str): Unique identifier for the note.
        safe_title (str): Filesystem-safe note title.
        resource (Element): Resource element.
        note_dir (Path): Directory to save the file.
        file (Path): ENEX source file.
        notebook_name (str): Name of the notebook.
        logs (dict): Log dictionary.
    """
    data_element = resource.find("data")
    mime_element = resource.find("mime")

    if data_element is None or mime_element is None:
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": "Missing mime type or resource data"
        })
        return

    mime_type = mime_element.text
    if not mime_type or not data_element.text:
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": "Missing mime type or resource data"
        })
        return

    # Guess file extension from MIME type
    extension = mimetypes.guess_extension(mime_type, strict=True) or ""
    file_name = f"{note_id} - {safe_title}{extension}"
    file_path = note_dir / file_name

    try:
        binary_data = base64.b64decode(data_element.text)
        if not file_path.exists():
            file_path.write_bytes(binary_data)

        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": True,
            "file_path": str(file_path),
            "notebook": notebook_name,
            "type": "single-resource",
        })
        print(f"Saved single resource: {file_path.name}")
    except Exception as e:
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

    Args:
        note_id (str): Unique identifier for the note.
        safe_title (str): Filesystem-safe note title.
        text_content (str): Text content of the note.
        note_dir (Path): Directory to save the PDF.
        file (Path): ENEX source file.
        notebook_name (str): Name of the notebook.
        logs (dict): Log dictionary.
    """
    file_path = note_dir / f"{note_id}-{safe_title}.pdf"

    try:
        create_text_pdf(text_content, file_path)
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": True,
            "file_path": str(file_path),
            "notebook": notebook_name,
            "type": "text-only-pdf",
        })
        print(f"Created text-only PDF: {file_path.name}")
    except Exception as e:
        logs[notebook_name].append({
            "file": file.name,
            "note": safe_title,
            "note_id": note_id,
            "success": False,
            "notebook": notebook_name,
            "error": f"PDF creation failed: {str(e)}"
        })
        print(f"Error creating text-only PDF for {safe_title}: {e}")


def process_files(output_directory: Path, dry_run: bool) -> None:
    """
    Main driver function: Processes ENEX files and optionally uploads to Google Drive.

    Args:
        output_directory (Path): Directory where files will be extracted.
        dry_run (bool): If True, skip uploading to Drive.
    """
    print(f"[INFO] Processing notes into: {output_directory}")
    if dry_run:
        print("[INFO] Dry run mode enabled — Google Drive syncing will be skipped.")

    input_directory = Path("./input_data")
    extraction_log_file = Path("./extraction_log.json")
    logs_json = load_extraction_log(extraction_log_file)

    if not input_directory.exists():
        raise FileNotFoundError("Input directory does not exist")

    output_directory.mkdir(parents=True, exist_ok=True)
    files = list_enex_files(input_directory)

    if not files:
        print("No ENEX files found.")
        return

    for file in files:
        process_enex_file(file, output_directory, logs_json)

    finalize_logs(logs_json, extraction_log_file)

    if dry_run:
        print("Dry run complete. No files were uploaded.")
    else:
        service_account = authenticate_drive()
        upload_directory(service_account, output_directory)

def finalize_logs(logs_json: dict, log_file: Path):
    log_file.write_text(json.dumps(logs_json, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Evernote-to-Drive Migrator",
        description=(
            "Exports and processes Evernote ENEX files, replicating notebook structure "
            "into Google Drive. Supports dry-run mode to skip actual upload."
        )
    )

    parser.add_argument(
        "-o", "--output-directory",
        type=Path,
        default=Path("./EverNote Notes"),
        help="Directory where the converted notes will be saved (default: ./EverNote Notes)"
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Run without uploading to Google Drive (for testing output structure only)"
    )

    args = parser.parse_args()
    output_directory: Path = args.output_directory
    dry_run: bool = args.dry_run

    output_directory.mkdir(parents=True, exist_ok=True)

    process_files(output_directory, dry_run)

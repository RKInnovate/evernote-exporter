"""
PDF utilities for converting and merging note content into PDFs.

TODO: Future enhancements for unsupported file types
------------------------------------------------------
The following file types are NOT currently supported in multi-item PDFs:
- ZIP/Archive files (.zip, .rar, .7z, .tar, .gz)
- HTML files (.html, .htm)
- Video files (.mp4, .avi, .mov, .mkv, .webm)
- Audio files (.mp3, .wav, .flac, .ogg)
- Office documents (.doc, .docx, .xls, .xlsx, .ppt, .pptx)
- Other binary formats

These files are saved separately with ID prefix. Future handling requires discussion:
1. Generate thumbnail previews for videos?
2. Convert HTML to PDF with proper rendering?
3. Create info pages in PDF listing attached files?
4. Extract text from office documents?
5. Create archive manifests for ZIP files?
"""

import io
import random
import string
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_LEFT
from pypdf import PdfReader, PdfWriter


# Supported file types for PDF conversion
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
SUPPORTED_PDF_FORMAT = {'.pdf'}
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_PDF_FORMAT

# Unsupported file types that need separate handling
UNSUPPORTED_ARCHIVE_FORMATS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
UNSUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
UNSUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
UNSUPPORTED_HTML_FORMATS = {'.html', '.htm', '.mhtml'}
UNSUPPORTED_OFFICE_FORMATS = {'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
UNSUPPORTED_FORMATS = (
    UNSUPPORTED_ARCHIVE_FORMATS |
    UNSUPPORTED_VIDEO_FORMATS |
    UNSUPPORTED_AUDIO_FORMATS |
    UNSUPPORTED_HTML_FORMATS |
    UNSUPPORTED_OFFICE_FORMATS
)


def generate_unique_id(length: int = 6) -> str:
    """
    Generate a unique alphanumeric ID.

    Args:
        length (int): Length of the ID (default: 6)

    Returns:
        str: A random alphanumeric string
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


def categorize_file_type(file_path: Path) -> str:
    """
    Categorize a file based on its extension.

    Args:
        file_path (Path): Path to the file

    Returns:
        str: Category - 'image', 'pdf', 'unsupported', or 'unknown'
    """
    suffix = file_path.suffix.lower()

    if suffix in SUPPORTED_IMAGE_FORMATS:
        return 'image'
    elif suffix in SUPPORTED_PDF_FORMAT:
        return 'pdf'
    elif suffix in UNSUPPORTED_FORMATS:
        return 'unsupported'
    else:
        return 'unknown'


def separate_supported_unsupported_resources(
    resource_paths: List[Path]
) -> Tuple[List[Path], List[Path]]:
    """
    Separate resources into supported (can be in PDF) and unsupported (must be saved separately).

    Args:
        resource_paths (List[Path]): List of resource file paths

    Returns:
        Tuple[List[Path], List[Path]]: (supported_files, unsupported_files)
    """
    supported = []
    unsupported = []

    for path in resource_paths:
        file_type = categorize_file_type(path)
        if file_type in ['image', 'pdf']:
            supported.append(path)
        else:
            unsupported.append(path)

    return supported, unsupported


def create_text_pdf(text_content: str, output_path: Path) -> None:
    """
    Create a PDF from text content.

    Args:
        text_content (str): The text to convert to PDF
        output_path (Path): Path where the PDF will be saved
    """
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Create a custom style for the content
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    # Split text into paragraphs and add to story
    paragraphs = text_content.split('\n')
    for para_text in paragraphs:
        if para_text.strip():
            para = Paragraph(para_text.strip(), content_style)
            story.append(para)
        else:
            story.append(Spacer(1, 0.2 * inch))

    doc.build(story)


def image_to_pdf(image_path: Path, output_path: Path) -> None:
    """
    Convert an image file to PDF.

    Args:
        image_path (Path): Path to the image file
        output_path (Path): Path where the PDF will be saved
    """
    try:
        img = Image.open(image_path)

        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Create PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []

        # Calculate image size to fit page
        page_width, page_height = letter
        margin = 0.5 * inch
        max_width = page_width - 2 * margin
        max_height = page_height - 2 * margin

        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        if img_width > max_width or img_height > max_height:
            if aspect_ratio > 1:
                # Landscape
                display_width = max_width
                display_height = display_width / aspect_ratio
            else:
                # Portrait
                display_height = max_height
                display_width = display_height * aspect_ratio
        else:
            display_width = img_width
            display_height = img_height

        # Add image to PDF
        rl_img = RLImage(str(image_path), width=display_width, height=display_height)
        story.append(rl_img)

        doc.build(story)
    except Exception as e:
        print(f"Error converting image {image_path} to PDF: {e}")
        raise


def merge_pdfs(pdf_paths: List[Path], output_path: Path) -> None:
    """
    Merge multiple PDF files into one.

    Args:
        pdf_paths (List[Path]): List of PDF file paths to merge
        output_path (Path): Path where the merged PDF will be saved
    """
    writer = PdfWriter()

    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(str(pdf_path))
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            continue

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)


def create_multi_item_pdf(
    text_content: Optional[str],
    resource_paths: List[Path],
    output_path: Path
) -> Tuple[bool, List[Path]]:
    """
    Create a single PDF containing text and multiple resources (images/PDFs only).

    Args:
        text_content (Optional[str]): Text content to include (can be None)
        resource_paths (List[Path]): List of resource file paths
        output_path (Path): Path where the final PDF will be saved

    Returns:
        Tuple[bool, List[Path]]: (success, list of unsupported files that were skipped)

    Note:
        Only images and PDFs are included in the merged PDF.
        Unsupported files (ZIP, HTML, video, etc.) are returned in the list
        and must be handled separately by the caller.
    """
    temp_pdfs = []
    unsupported_files = []
    temp_dir = output_path.parent / ".temp_pdfs"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Convert text to PDF if exists
        if text_content:
            text_pdf = temp_dir / f"text_{generate_unique_id()}.pdf"
            create_text_pdf(text_content, text_pdf)
            temp_pdfs.append(text_pdf)

        # Convert resources to PDFs (only supported types)
        for idx, resource_path in enumerate(resource_paths):
            file_type = categorize_file_type(resource_path)

            if file_type == 'pdf':
                # Already a PDF, just add to list
                temp_pdfs.append(resource_path)
            elif file_type == 'image':
                # Convert image to PDF
                temp_pdf = temp_dir / f"img_{idx}_{generate_unique_id()}.pdf"
                image_to_pdf(resource_path, temp_pdf)
                temp_pdfs.append(temp_pdf)
            elif file_type in ['unsupported', 'unknown']:
                # Cannot include in PDF - must be saved separately
                unsupported_files.append(resource_path)
                print(f"⚠️  Unsupported file type for PDF merge: {resource_path.name}")

        # Merge all PDFs
        if temp_pdfs:
            merge_pdfs(temp_pdfs, output_path)
            return (True, unsupported_files)
        else:
            return (False, unsupported_files)

    finally:
        # Clean up temporary PDFs
        for temp_pdf in temp_pdfs:
            if temp_pdf.parent == temp_dir and temp_pdf.exists():
                try:
                    temp_pdf.unlink()
                except Exception:
                    pass

        # Remove temp directory if empty
        try:
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
        except Exception:
            pass


def should_create_multi_item_pdf(text_content: Optional[str], resources_count: int) -> bool:
    """
    Determine if a multi-item PDF should be created.

    Args:
        text_content (Optional[str]): Text content of the note
        resources_count (int): Number of resources/attachments

    Returns:
        bool: True if should create multi-item PDF, False otherwise
    """
    # Create multi-item PDF if:
    # 1. There are multiple resources, OR
    # 2. There is both text content and at least one resource
    has_text = text_content is not None and text_content.strip()

    if resources_count > 1:
        return True
    if has_text and resources_count >= 1:
        return True

    return False

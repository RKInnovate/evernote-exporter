"""
PDF Utilities Module

This module handles all PDF-related operations:
- Converting text to PDF
- Converting images to PDF
- Merging multiple PDFs into one
- Generating unique IDs for notes

Key Concepts:
- ReportLab: Library for creating PDFs from scratch
- PyPDF: Library for manipulating existing PDFs (merging, reading)
- PIL/Pillow: Library for image processing

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

# Standard library imports
import io        # For working with in-memory file-like objects (currently unused but imported)
import random    # For generating random IDs
import string    # For character sets used in ID generation
from pathlib import Path  # For handling file paths
from typing import List, Optional, Tuple  # Type hints for better code documentation

# Third-party library imports for PDF and image processing
from PIL import Image  # Python Imaging Library - for opening and processing images
from reportlab.lib.pagesizes import letter, A4  # Standard page sizes (letter = 8.5x11 inches)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # For text styling in PDFs
from reportlab.lib.units import inch  # Unit conversion (1 inch = 72 points)
from reportlab.platypus import (  # ReportLab's document layout system
    SimpleDocTemplate,  # Creates PDF documents
    Paragraph,          # Formats text as paragraphs
    Spacer,             # Adds vertical spacing
    PageBreak,          # Forces new page (imported but currently unused)
    Image as RLImage    # ReportLab's Image class (renamed to avoid conflict with PIL.Image)
)
from reportlab.lib.enums import TA_LEFT  # Text alignment constant (left align)
from pypdf import PdfReader, PdfWriter  # For reading and merging existing PDF files


# ============================================================================
# FILE TYPE CONSTANTS
# ============================================================================
# These constants define which file types we can handle and which we cannot
# They're used throughout the code to categorize files

# Supported file types for PDF conversion
# These file types can be directly included in merged PDFs
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
SUPPORTED_PDF_FORMAT = {'.pdf'}  # Note: singular name but could contain multiple formats
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_PDF_FORMAT  # Combines both sets using union operator

# Unsupported file types that need separate handling
# These file types CANNOT be merged into PDFs and must be saved separately
UNSUPPORTED_ARCHIVE_FORMATS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
UNSUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
UNSUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
UNSUPPORTED_HTML_FORMATS = {'.html', '.htm', '.mhtml'}
UNSUPPORTED_OFFICE_FORMATS = {'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}

# Combine all unsupported formats into one set for easy checking
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

    WHAT THIS DOES:
    Creates a random string of uppercase letters and numbers.
    Used to prefix note filenames to prevent conflicts.

    HOW IT WORKS:
    1. Combines uppercase letters (A-Z) and digits (0-9)
    2. Randomly selects 'length' characters from this set
    3. Joins them into a string

    Args:
        length (int): How many characters in the ID (default: 6)

    Returns:
        str: A random alphanumeric string like "A3B9K2" or "X7Y1Z4"

    EXAMPLE:
        id1 = generate_unique_id()      # Might return "A3B9K2"
        id2 = generate_unique_id(8)     # Might return "X7Y1Z4M9"
    
    IMPORTANT:
        - IDs are random, not sequential
        - Very small chance of duplicates (with 6 chars = 36^6 combinations)
        - Uses uppercase only for readability (no confusing 0/O, 1/l)
    """
    # Create character set: uppercase letters A-Z and digits 0-9
    # string.ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # string.digits = "0123456789"
    characters = string.ascii_uppercase + string.digits
    
    # random.choices() randomly selects 'length' characters (with replacement)
    # ''.join() combines them into a single string
    # k=length means select this many characters
    return ''.join(random.choices(characters, k=length))


def categorize_file_type(file_path: Path) -> str:
    """
    Categorize a file based on its extension.

    WHAT THIS DOES:
    Looks at a file's extension (like .jpg, .pdf, .mp4) and determines
    what category it belongs to. This helps decide how to process the file.

    HOW IT WORKS:
    1. Gets the file extension (the part after the dot)
    2. Converts to lowercase for case-insensitive matching
    3. Checks against known format lists
    4. Returns category string

    Args:
        file_path (Path): Path to the file (e.g., Path("./photo.jpg"))

    Returns:
        str: One of:
            - 'image': Supported image formats (can be merged into PDF)
            - 'pdf': PDF files (can be merged into PDF)
            - 'unsupported': Known unsupported formats (videos, archives, etc.)
            - 'unknown': Extension not in any category

    EXAMPLE:
        categorize_file_type(Path("photo.jpg"))      # Returns 'image'
        categorize_file_type(Path("document.pdf"))   # Returns 'pdf'
        categorize_file_type(Path("video.mp4"))      # Returns 'unsupported'
        categorize_file_type(Path("file.xyz"))       # Returns 'unknown'
    
    IMPORTANT:
        - Only looks at file extension, not actual file content
        - Case-insensitive: .JPG and .jpg are treated the same
        - Unknown files are treated separately (not merged, but also not blocked)
    """
    # Get the file extension (everything after the last dot)
    # .lower() makes it case-insensitive (.JPG = .jpg)
    # Example: Path("photo.JPG") → suffix = ".jpg"
    suffix = file_path.suffix.lower()

    # Check which category this file belongs to
    if suffix in SUPPORTED_IMAGE_FORMATS:
        # It's a supported image format
        return 'image'
    elif suffix in SUPPORTED_PDF_FORMAT:
        # It's a PDF file
        return 'pdf'
    elif suffix in UNSUPPORTED_FORMATS:
        # It's a known unsupported format (video, audio, archive, etc.)
        return 'unsupported'
    else:
        # Extension not recognized - treat as unknown
        return 'unknown'


def separate_supported_unsupported_resources(
    resource_paths: List[Path]
) -> Tuple[List[Path], List[Path]]:
    """
    Separate resources into supported (can be in PDF) and unsupported (must be saved separately).

    WHAT THIS DOES:
    Takes a list of files and splits them into two groups:
    - Files that can be merged into a PDF (images and PDFs)
    - Files that must be saved separately (videos, archives, etc.)

    HOW IT WORKS:
    1. Loops through each file path
    2. Categorizes each file (image, pdf, unsupported, unknown)
    3. Adds to appropriate list based on category

    Args:
        resource_paths (List[Path]): List of file paths to categorize
                                     Example: [Path("img.jpg"), Path("video.mp4"), Path("doc.pdf")]

    Returns:
        Tuple[List[Path], List[Path]]: A tuple containing:
            - First list: Supported files (images, PDFs) - can be merged
            - Second list: Unsupported files - must be saved separately

    EXAMPLE:
        files = [Path("photo.jpg"), Path("video.mp4"), Path("document.pdf"), Path("archive.zip")]
        supported, unsupported = separate_supported_unsupported_resources(files)
        # supported = [Path("photo.jpg"), Path("document.pdf")]
        # unsupported = [Path("video.mp4"), Path("archive.zip")]
    
    NOTE:
        Unknown file types go into unsupported list (better safe than sorry)
    """
    # Initialize empty lists to store categorized files
    supported = []      # Files we can merge into PDF
    unsupported = []    # Files we must save separately

    # Loop through each file path
    for path in resource_paths:
        # Determine what type of file this is
        file_type = categorize_file_type(path)
        
        # If it's an image or PDF, we can include it in the merged PDF
        if file_type in ['image', 'pdf']:
            supported.append(path)
        else:
            # Everything else (unsupported, unknown) goes to separate list
            unsupported.append(path)

    # Return both lists as a tuple
    # Tuple = immutable ordered pair, like (list1, list2)
    return supported, unsupported


def create_text_pdf(text_content: str, output_path: Path) -> None:
    """
    Create a PDF from text content.

    WHAT THIS DOES:
    Takes plain text and converts it into a formatted PDF document.
    Handles paragraph breaks, spacing, and text formatting.

    HOW IT WORKS:
    1. Creates a PDF document template (letter-sized pages)
    2. Defines text styling (font size, spacing, alignment)
    3. Splits text into paragraphs (by newlines)
    4. Adds each paragraph to the document
    5. Builds (renders) the PDF file

    Args:
        text_content (str): The plain text to convert to PDF
                           Example: "First paragraph\n\nSecond paragraph"
        output_path (Path): Where to save the PDF file
                           Example: Path("./output.pdf")

    EXAMPLE:
        text = "Hello World\n\nThis is a test document."
        create_text_pdf(text, Path("./output.pdf"))
        # Creates output.pdf with formatted text
    
    IMPORTANT CONCEPTS:
        - SimpleDocTemplate: ReportLab's document builder
        - story: A list of elements (paragraphs, images, etc.) to add to PDF
        - Paragraph: Formatted text block with styling
        - Spacer: Empty vertical space between elements
    """
    # Create a PDF document template
    # SimpleDocTemplate manages pages, margins, etc.
    # str(output_path) converts Path to string (ReportLab needs string)
    # pagesize=letter means 8.5 x 11 inch pages
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    
    # "story" is ReportLab's term for the list of elements to add to the PDF
    # We'll add paragraphs, spacers, etc. to this list
    story = []
    
    # Get default text styles from ReportLab
    # These provide basic formatting options
    styles = getSampleStyleSheet()

    # Create a custom style for our text content
    # This gives us control over how text looks
    content_style = ParagraphStyle(
        'CustomContent',          # Style name (can be anything)
        parent=styles['Normal'],  # Start with normal style, then customize
        fontSize=11,              # Font size in points (11pt is readable)
        leading=14,               # Line spacing (space between lines)
        alignment=TA_LEFT,        # Left-align text (TA_LEFT = text align left)
        spaceAfter=12,            # Space after each paragraph (in points)
    )

    # Split text into paragraphs based on newline characters
    # Example: "Line1\nLine2\n\nLine3" → ["Line1", "Line2", "", "Line3"]
    paragraphs = text_content.split('\n')
    
    # Process each paragraph
    for para_text in paragraphs:
        # Check if paragraph has actual content (not just whitespace)
        if para_text.strip():  # .strip() removes leading/trailing whitespace
            # Create a formatted paragraph with our custom style
            para = Paragraph(para_text.strip(), content_style)
            story.append(para)  # Add paragraph to the document
        else:
            # Empty line - add vertical spacing instead of empty paragraph
            # Spacer(width, height) - width=1 doesn't matter, height is what we want
            # 0.2 * inch = about 14 points of space
            story.append(Spacer(1, 0.2 * inch))

    # Build (render) the PDF document
    # This takes all elements in 'story' and creates the actual PDF file
    doc.build(story)


def image_to_pdf(image_path: Path, output_path: Path) -> None:
    """
    Convert an image file to PDF.

    WHAT THIS DOES:
    Takes an image file (JPG, PNG, etc.) and creates a PDF containing that image.
    The image is scaled to fit on a letter-sized page while maintaining its aspect ratio.

    HOW IT WORKS:
    1. Opens the image file using PIL (Pillow)
    2. Converts color modes (RGBA → RGB) for PDF compatibility
    3. Calculates proper size to fit on page (maintaining aspect ratio)
    4. Creates a PDF with the image centered/fitted on the page

    Args:
        image_path (Path): Path to the image file to convert
                           Example: Path("./photo.jpg")
        output_path (Path): Where to save the PDF
                            Example: Path("./photo.pdf")

    EXAMPLE:
        image_to_pdf(Path("photo.jpg"), Path("photo.pdf"))
        # Creates photo.pdf containing the image
    
    IMPORTANT CONCEPTS:
        - RGBA: Red-Green-Blue-Alpha (alpha = transparency)
        - PDFs don't support transparency, so we convert RGBA to RGB
        - Aspect ratio: width/height ratio (keeps image from being stretched)
        - Scaling: Making image larger or smaller to fit page
    
    COLOR MODE EXPLANATION:
        - RGB: Standard color mode (red, green, blue) - PDF compatible
        - RGBA: RGB + Alpha channel (transparency) - needs conversion
        - Other modes (grayscale, etc.) are converted to RGB
    """
    try:
        # Open the image file using PIL (Pillow library)
        img = Image.open(image_path)

        # Convert image color mode if necessary
        # PDFs work best with RGB (no transparency)
        
        # Handle RGBA images (with transparency/alpha channel)
        if img.mode == 'RGBA':
            # Create a white RGB image the same size as original
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))  # White background
            
            # Paste the RGBA image onto RGB background, using alpha as mask
            # split()[3] gets the alpha channel (transparency info)
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img  # Use the converted image
        elif img.mode != 'RGB':
            # Any other color mode (grayscale, etc.) - convert to RGB
            img = img.convert('RGB')

        # Create PDF document (letter-sized pages)
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []  # List to hold PDF elements

        # Calculate how big the image should be to fit on the page
        # letter page size in points: (612, 792) for 8.5" x 11"
        page_width, page_height = letter
        
        # Set margins (0.5 inch on all sides)
        margin = 0.5 * inch
        
        # Maximum size for image (page size minus margins on both sides)
        max_width = page_width - 2 * margin   # Left + right margins
        max_height = page_height - 2 * margin # Top + bottom margins

        # Get original image dimensions (in pixels)
        img_width, img_height = img.size
        
        # Calculate aspect ratio (width divided by height)
        # aspect_ratio > 1 = landscape (wider than tall)
        # aspect_ratio < 1 = portrait (taller than wide)
        aspect_ratio = img_width / img_height

        # Check if image needs to be scaled down to fit on page
        if img_width > max_width or img_height > max_height:
            # Image is too big - need to scale it down
            if aspect_ratio > 1:
                # Landscape image (wider than tall)
                # Scale to fit width, then adjust height proportionally
                display_width = max_width
                display_height = display_width / aspect_ratio
            else:
                # Portrait image (taller than wide) or square
                # Scale to fit height, then adjust width proportionally
                display_height = max_height
                display_width = display_height * aspect_ratio
        else:
            # Image fits on page at original size
            display_width = img_width
            display_height = img_height

        # Create ReportLab Image object with calculated dimensions
        # RLImage is ReportLab's Image class (renamed to avoid conflict with PIL.Image)
        rl_img = RLImage(str(image_path), width=display_width, height=display_height)
        story.append(rl_img)  # Add image to PDF

        # Build (render) the PDF
        doc.build(story)
        
    except Exception as e:
        # If anything goes wrong (file can't be opened, invalid format, etc.)
        print(f"Error converting image {image_path} to PDF: {e}")
        raise  # Re-raise the exception so caller knows it failed


def merge_pdfs(pdf_paths: List[Path], output_path: Path) -> None:
    """
    Merge multiple PDF files into one.

    WHAT THIS DOES:
    Takes several PDF files and combines them into a single PDF.
    All pages from all input PDFs are added in order.

    HOW IT WORKS:
    1. Creates a PDF writer object (for building new PDF)
    2. Loops through each input PDF
    3. Reads all pages from each PDF
    4. Adds each page to the writer
    5. Writes the combined PDF to output file

    Args:
        pdf_paths (List[Path]): List of PDF files to merge
                                Example: [Path("page1.pdf"), Path("page2.pdf")]
        output_path (Path): Where to save the merged PDF
                            Example: Path("merged.pdf")

    EXAMPLE:
        pdfs = [Path("text.pdf"), Path("image.pdf"), Path("document.pdf")]
        merge_pdfs(pdfs, Path("combined.pdf"))
        # Creates combined.pdf with all pages from all input PDFs
    
    IMPORTANT:
        - Pages are added in the order PDFs appear in the list
        - If a PDF can't be read, it's skipped (error message printed)
        - All successfully read PDFs are still merged
    """
    # Create a PDF writer object
    # PdfWriter is from pypdf library - it builds new PDF files
    writer = PdfWriter()

    # Loop through each PDF file to merge
    for pdf_path in pdf_paths:
        try:
            # Open and read the PDF file
            # PdfReader reads existing PDF files
            reader = PdfReader(str(pdf_path))
            
            # Loop through each page in this PDF
            for page in reader.pages:
                # Add the page to our writer (will be part of final merged PDF)
                writer.add_page(page)
                
        except Exception as e:
            # If we can't read this PDF (corrupted, permission error, etc.)
            # Print error but continue with other PDFs
            print(f"Error reading PDF {pdf_path}: {e}")
            continue  # Skip to next PDF

    # Write the merged PDF to the output file
    # 'wb' = write binary mode (PDFs are binary files)
    # with statement ensures file is properly closed after writing
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)  # Write all collected pages to file


def create_multi_item_pdf(
    text_content: Optional[str],
    resource_paths: List[Path],
    output_path: Path
) -> Tuple[bool, List[Path]]:
    """
    Create a single PDF containing text and multiple resources (images/PDFs only).

    WHAT THIS DOES:
    Combines text content and multiple file attachments into one unified PDF.
    This is the main function for creating multi-item PDFs.
    
    Process:
    1. Converts text to PDF (if provided)
    2. Converts images to PDFs
    3. Includes existing PDFs
    4. Merges everything into one PDF
    5. Returns list of files that couldn't be included

    Args:
        text_content (Optional[str]): Text to include (can be None if no text)
        resource_paths (List[Path]): List of file paths to include
                                     Can contain images, PDFs, or unsupported files
        output_path (Path): Where to save the final merged PDF

    Returns:
        Tuple[bool, List[Path]]: 
            - First value (bool): True if PDF was created, False if no content
            - Second value (List[Path]): Files that couldn't be merged (videos, ZIPs, etc.)

    EXAMPLE:
        text = "Meeting notes"
        files = [Path("photo.jpg"), Path("document.pdf"), Path("video.mp4")]
        success, unsupported = create_multi_item_pdf(text, files, Path("output.pdf"))
        # Creates output.pdf with text + photo + document
        # Returns: (True, [Path("video.mp4")])
    
    IMPORTANT CONCEPTS:
        - Temporary files: We create intermediate PDFs, then merge them
        - Unsupported files: Videos, ZIPs, etc. can't be in PDF - returned to caller
        - Cleanup: Temporary files are deleted after merging (in 'finally' block)
    
    WORKFLOW:
        Text → PDF → |
        Image1 → PDF → | → Merge all → Final PDF
        Image2 → PDF → |
        PDF1 → PDF → |
    """
    # Lists to track files we're working with
    temp_pdfs = []          # PDFs we'll merge (text PDF, image PDFs, existing PDFs)
    unsupported_files = []  # Files we can't merge (returned to caller)
    
    # Create temporary directory for intermediate PDF files
    # These will be deleted after we merge them
    temp_dir = output_path.parent / ".temp_pdfs"
    temp_dir.mkdir(exist_ok=True)

    # Use try/finally to ensure cleanup happens even if errors occur
    try:
        # STEP 1: Convert text to PDF (if text content exists)
        if text_content:
            # Create temporary PDF filename for text
            text_pdf = temp_dir / f"text_{generate_unique_id()}.pdf"
            
            # Convert text to PDF
            create_text_pdf(text_content, text_pdf)
            
            # Add to list of PDFs to merge
            temp_pdfs.append(text_pdf)

        # STEP 2: Process each resource file
        for idx, resource_path in enumerate(resource_paths):
            # Determine what type of file this is
            file_type = categorize_file_type(resource_path)

            if file_type == 'pdf':
                # Already a PDF - can merge directly
                # No conversion needed, just add to merge list
                temp_pdfs.append(resource_path)
                
            elif file_type == 'image':
                # Image file - convert to PDF first
                # Create temporary PDF filename
                temp_pdf = temp_dir / f"img_{idx}_{generate_unique_id()}.pdf"
                
                # Convert image to PDF
                image_to_pdf(resource_path, temp_pdf)
                
                # Add converted PDF to merge list
                temp_pdfs.append(temp_pdf)
                
            elif file_type in ['unsupported', 'unknown']:
                # Can't include this in PDF (video, ZIP, etc.)
                # Add to unsupported list - caller must handle separately
                unsupported_files.append(resource_path)
                print(f"⚠️  Unsupported file type for PDF merge: {resource_path.name}")

        # STEP 3: Merge all PDFs into one
        if temp_pdfs:
            # We have PDFs to merge - combine them all
            merge_pdfs(temp_pdfs, output_path)
            return (True, unsupported_files)  # Success!
        else:
            # No PDFs to merge (maybe only unsupported files?)
            return (False, unsupported_files)  # Nothing created

    finally:
        # CLEANUP: Always runs, even if errors occurred
        # Delete temporary PDF files we created
        
        # Loop through all temporary PDFs
        for temp_pdf in temp_pdfs:
            # Only delete files in temp directory (not original PDFs)
            # Check exists() to avoid errors if already deleted
            if temp_pdf.parent == temp_dir and temp_pdf.exists():
                try:
                    temp_pdf.unlink()  # Delete the temporary file
                except Exception:
                    # If deletion fails, continue anyway
                    pass

        # Remove temporary directory if it's empty
        try:
            # Check if directory exists and has no files
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()  # Delete empty directory
        except Exception:
            # If removal fails, continue anyway
            pass


def should_create_multi_item_pdf(text_content: Optional[str], resources_count: int) -> bool:
    """
    Determine if a multi-item PDF should be created.

    WHAT THIS DOES:
    Decides whether a note should become a multi-item PDF or be handled differently.
    This is a decision-making function that routes notes to the right handler.

    LOGIC:
    Create multi-item PDF if:
    1. Note has multiple resources (2+ attachments), OR
    2. Note has both text AND at least one resource
    
    Otherwise, handle as single-item or text-only.

    Args:
        text_content (Optional[str]): Text content of the note (can be None)
        resources_count (int): Number of attachments/resources in the note

    Returns:
        bool: 
            - True: Create multi-item PDF (text + resources merged)
            - False: Handle as single resource or text-only

    EXAMPLE:
        # Multiple resources → multi-item PDF
        should_create_multi_item_pdf(None, 2) → True
        
        # Text + resource → multi-item PDF
        should_create_multi_item_pdf("Hello", 1) → True
        
        # Only text → text-only PDF
        should_create_multi_item_pdf("Hello", 0) → False
        
        # Only one resource → single resource handler
        should_create_multi_item_pdf(None, 1) → False
    
    DECISION TABLE:
        Text?  Resources?  Result
        ------  ----------  --------
        No     0           False (skip - no content)
        No     1           False (single resource)
        No     2+          True  (multiple resources)
        Yes    0           False (text-only)
        Yes    1           True  (text + resource)
        Yes    2+          True  (text + multiple resources)
    """
    # Check if note has text content
    # text_content is not None AND has non-whitespace characters
    # .strip() removes leading/trailing spaces/tabs/newlines
    has_text = text_content is not None and text_content.strip()

    # CASE 1: Multiple resources (2 or more)
    # Even without text, multiple resources should be combined
    if resources_count > 1:
        return True  # Create multi-item PDF
    
    # CASE 2: Text AND at least one resource
    # Combining text with attachments creates a unified document
    if has_text and resources_count >= 1:
        return True  # Create multi-item PDF

    # All other cases: single resource or text-only
    # These are handled by other functions
    return False

import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import io
import os
import re
try:
    from spellchecker import SpellChecker
except ImportError:
    # Fallback if library not yet installed in the current environment
    SpellChecker = None

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PDF OCR Extractor",
    page_icon="📄",
    layout="centered"
)

# --- UTILITY FUNCTIONS ---

def enhance_image(image):
    """Enhance image for better OCR accuracy."""
    # Convert to grayscale
    image = image.convert('L')
    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)
    # Sharpen
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    # Binarization (thresholding)
    # Using a slightly adaptive approach: values below 140 become black
    image = image.point(lambda x: 0 if x < 140 else 255, '1')
    return image

def reflow_ocr_text(text):
    """Reconstruct paragraphs from narrow columns and handle hyphenation."""
    if not text:
        return ""
    # Split by double newline to identify potential paragraph blocks
    blocks = re.split(r'\n\s*\n', text)
    reflowed_blocks = []
    
    for block in blocks:
        if not block.strip():
            continue
        # Join lines within the block
        lines = block.split('\n')
        cleaned_block = ""
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # Handle hyphenation at end of line (e.g., "word-" + "break" -> "wordbreak")
            if line.endswith('-') and i < len(lines) - 1:
                cleaned_block += line[:-1]
            else:
                cleaned_block += line + " "
        reflowed_blocks.append(cleaned_block.strip())
        
    return "\n\n".join(reflowed_blocks)

def correct_text_logic(text):
    """Attempt to correct fragmented words using a spell checker."""
    if not SpellChecker:
        return text
    
    spell = SpellChecker()
    # Process text line by line to preserve structure
    lines = text.split('\n')
    corrected_lines = []
    
    for line in lines:
        words = line.split()
        if not words:
            corrected_lines.append("")
            continue
            
        corrected_words = []
        for word in words:
            # Clean word for checking (remove punctuation)
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 2 and clean_word.isalpha():
                # Get the most likely correction
                corrected = spell.correction(clean_word)
                if corrected and corrected.lower() != clean_word.lower():
                    # We found a correction!
                    corrected_words.append(corrected)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        corrected_lines.append(" ".join(corrected_words))
        
    return "\n".join(corrected_lines)

# --- UI HEADER ---
st.title("📄 PDF OCR Extractor")
st.markdown("""
Extract text from scanned PDF documents using Optical Character Recognition (OCR).
Upload your file to get started.
""")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ Configuration")

st.sidebar.subheader("OCR Quality")
boost_accuracy = st.sidebar.checkbox(
    "Accuracy Booster", 
    value=False,
    help="Enhances contrast and sharpness before OCR. Recommended for faint or noisy documents."
)

st.sidebar.subheader("Text Formatting")
reflow_text = st.sidebar.checkbox(
    "Reflow Text", 
    value=True,
    help="Joins narrow column lines into natural paragraphs and handles hyphenation."
)

spell_correction = st.sidebar.checkbox(
    "Spell Correction (Experimental)", 
    value=False,
    help="Attempts to predict and fix fragmented words or typos."
)

st.sidebar.divider()
st.sidebar.markdown("### Advanced Paths")
tesseract_path = st.sidebar.text_input(
    "Tesseract Binary Path",
    placeholder="e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
    help="Path to the tesseract executable (Windows users)."
)

poppler_path = st.sidebar.text_input(
    "Poppler Bin Path",
    placeholder="e.g. C:\\poppler-23.01.0\\Library\\bin",
    help="Path to the 'bin' folder containing poppler binaries."
)

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader(
    "Drag and drop a PDF file here",
    type=["pdf"],
    help="Only scanned or text-based PDF files are supported."
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    try:
        # 1. Convert PDF to Images
        with st.spinner("📦 Converting PDF pages to images (300 DPI)..."):
            conv_kwargs = {"dpi": 300}
            if poppler_path:
                conv_kwargs["poppler_path"] = poppler_path
            images = convert_from_bytes(pdf_bytes, **conv_kwargs)
            
        num_pages = len(images)
        st.info(f"Detected {num_pages} page(s). Starting OCR processing...")
        
        # 2. Iterate through pages
        extracted_text = ""
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        for i, image in enumerate(images):
            # Update progress
            progress_val = (i + 1) / num_pages
            progress_bar.progress(progress_val)
            status_text.text(f"Processing page {i + 1} of {num_pages}...")
            
            # Application of Image Enhancement
            if boost_accuracy:
                image = enhance_image(image)
            
            # OCR Extraction
            page_text = pytesseract.image_to_string(image)
            
            # Post-processing per page (Reflow)
            if reflow_text:
                page_text = reflow_ocr_text(page_text)
                
            extracted_text += f"\n--- Page {i + 1} ---\n\n" + page_text + "\n"
            
        # 3. Final Post-processing (Spell Correction)
        if spell_correction:
            with st.spinner("🔮 Applying spell correction/prediction..."):
                extracted_text = correct_text_logic(extracted_text)
                
        # 4. Final Output
        status_text.empty()
        progress_bar.empty()
        st.success("✅ OCR Processing Complete!")
        
        st.subheader("Extracted Text")
        st.text_area(
            label="Result",
            value=extracted_text,
            height=400
        )
        
        st.download_button(
            label="💾 Download Extracted Text (.txt)",
            data=extracted_text,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr_refined.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("Check the sidebar configuration if you are on Windows or missing dependencies.")
else:
    st.info("Please upload a PDF file to begin.")

# --- FOOTER ---
st.markdown("---")
st.caption("PDF OCR Extractor - Enhanced for high accuracy and clean formatting.")

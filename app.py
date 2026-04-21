import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Local PDF OCR Extractor",
    page_icon="📄",
    layout="centered"
)

# --- UI HEADER ---
st.title("📄 Local PDF OCR Extractor")
st.markdown("""
Extract text from scanned PDF documents using Optical Character Recognition (OCR).
This tool runs entirely on your local machine.
""")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("Use these if the tools are not in your system PATH.")

tesseract_path = st.sidebar.text_input(
    "Tesseract Binary Path",
    placeholder="e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
    help="Path to the tesseract executable."
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
    # Read the file bytes
    pdf_bytes = uploaded_file.read()
    
    # 1. Convert PDF to Images
    try:
        with st.spinner("📦 Converting PDF pages to images (300 DPI)..."):
            # Prepare poppler_path argument if provided
            conv_kwargs = {"dpi": 300}
            if poppler_path:
                conv_kwargs["poppler_path"] = poppler_path
                
            # High DPI (300) is recommended for accurate OCR
            images = convert_from_bytes(pdf_bytes, **conv_kwargs)
            
        num_pages = len(images)
        st.info(f"Detected {num_pages} page(s). Starting OCR processing...")
        
        # 2. Iterate through pages and perform OCR
        extracted_text = ""
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        for i, image in enumerate(images):
            # Update progress bar
            progress_val = (i + 1) / num_pages
            progress_bar.progress(progress_val)
            status_text.text(f"Processing page {i + 1} of {num_pages}...")
            
            # Perform OCR on the PIL image
            page_text = pytesseract.image_to_string(image)
            extracted_text += f"\n--- Page {i + 1} ---\n\n" + page_text + "\n"
            
        # 3. Final Output
        status_text.empty()
        progress_bar.empty()
        st.success("✅ OCR Processing Complete!")
        
        # Display text in a text area
        st.subheader("Extracted Text")
        st.text_area(
            label="Result",
            value=extracted_text,
            height=400,
            help="You can copy the text from here."
        )
        
        # 4. Download Button
        st.download_button(
            label="💾 Download Extracted Text (.txt)",
            data=extracted_text,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Ensure **Tesseract OCR** is installed on your system.
        2. Ensure **Poppler** (required by pdf2image) is installed.
        3. For Windows users, make sure both are added to your System PATH or configured in the code.
        """)
else:
    st.info("Please upload a PDF file to begin.")

# --- FOOTER ---
st.markdown("---")
st.caption("Built with Streamlit, pdf2image, and PyTesseract.")

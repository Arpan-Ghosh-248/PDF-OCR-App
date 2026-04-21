# Local PDF OCR Extractor

A Streamlit-based web application that extracts text from scanned PDF documents using Tesseract OCR and Poppler.

## 🚀 Features
- **Simple UI**: Clean drag-and-drop interface.
- **High Accuracy**: Uses 300 DPI image conversion for better OCR results.
- **Progress Tracking**: Real-time feedback during processing.
- **Downloadable Output**: Save extracted text directly as a `.txt` file.

---

## 🛠️ Prerequisites

This application requires two system-level tools to be installed on your machine:
1. **Tesseract OCR**: The engine that converts images to text.
2. **Poppler**: The library that converts PDF pages to images.

### 1. Installation on macOS
Use [Homebrew](https://brew.sh/):
```bash
brew install tesseract poppler
```

### 2. Installation on Linux (Ubuntu)
```bash
sudo apt update
sudo apt install tesseract-ocr poppler-utils
```

### 3. Installation on Windows
#### **Tesseract OCR:**
- Download the installer from the [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
- After installation, note the path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- **Option A:** Add this folder to your System environment variable `PATH`.
- **Option B:** In `app.py`, uncomment and update the line:
  `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

#### **Poppler:**
- Download the latest binary zip from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases).
- Extract it to a folder (e.g., `C:\Program Files\poppler-xx.xx.x`).
- Add the `bin` folder within that extracted folder to your System environment variable `PATH` (recommended).

---

## 📦 Setup & Running

1. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 📝 Robustness Notes
- **DPI 300**: The app uses 300 DPI for conversion to ensure Tesseract has enough pixel density for accurate OCR.
- **Error Handling**: The app includes clear error messages if system dependencies are missing, helping users troubleshoot quickly.
- **Resource Management**: Uses `io.BytesIO` and direct memory conversion to avoid creating temporary image files on disk.

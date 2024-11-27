import os
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF

# Set the path to the Tesseract executable (macOS path)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Path to the folder containing PDF files
pdf_folder = "/Users/aarushisharma/downloads/scans"

# Function to preprocess image to improve OCR accuracy
def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        # Convert to grayscale
        image = image.convert('L')
        # Apply thresholding (binarization)
        image = image.point(lambda p: p > 128 and 255)
        # Optionally, apply sharpening
        image = image.filter(ImageFilter.SHARPEN)
        return image
    except Exception as e:
        print(f"Error preprocessing image {image_path}: {e}")
        return None

# Function to extract name and year from OCR text
def extract_name_and_year(image_path):
    try:
        # Perform OCR on the image after preprocessing
        processed_image = preprocess_image(image_path)
        if processed_image:
            text = pytesseract.image_to_string(processed_image)
        else:
            text = pytesseract.image_to_string(Image.open(image_path))
        
        # Initialize placeholders
        name = None
        year = None
        
        # Look for "709" form in the text
        if "709" in text:
            lines = text.splitlines()

            for line in lines:
                # Look for a name (e.g., first and last name, assuming capitalized text)
                if "LAWRENCE" in line:  # You can modify or add more specific keywords
                    name_line = line.split(":")[-1] if ":" in line else line
                    name = " ".join(name_line.strip().split())
                
                # Look for a 4-digit year
                if len(line.strip()) == 4 and line.strip().isdigit():
                    year = line.strip()

        if name and year:
            # Format the name (replace spaces with underscores) and return the formatted name and year
            name = name.replace(" ", "_").upper()
            return f"{name}_{year}"
        else:
            return None

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# Function to extract images from a PDF and rename them
def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract images from the page
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            image_filename = f"extracted_image_{page_num+1}_{img_index+1}.png"
            
            # Save the image as a temporary file
            with open(image_filename, "wb") as img_file:
                img_file.write(image_data)
            
            # Extract name and year from the image
            new_file_name = extract_name_and_year(image_filename)
            
            if new_file_name:
                new_file_path = os.path.join(pdf_folder, new_file_name + ".png")
                
                # Rename the extracted image
                try:
                    os.rename(image_filename, new_file_path)
                    print(f"Renamed image: {image_filename} -> {new_file_name}.png")
                except Exception as e:
                    print(f"Error renaming image {image_filename}: {e}")
            else:
                print(f"Could not extract name and year for image: {image_filename}")

# Iterate through all PDF files in the folder
for file_name in os.listdir(pdf_folder):
    file_path = os.path.join(pdf_folder, file_name)
    
    # Ensure it's a PDF file
    if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
        print(f"Processing PDF file: {file_name}")
        process_pdf(file_path)

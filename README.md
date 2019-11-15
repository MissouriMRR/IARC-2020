# IARC-2020

# Detect Russian Word: 'модули иртибот'
#Download pytesseract for OCR (optical character recognition)

#-----Using Mac and Homebrew-----
#(1) Downlaod tesseract:
		brew install tesseract

#(2) Download tesseract-lang (to use Russian)
		brew install tesseract-lang
#(3) Download Python wrapper
        pip install pytesseract

#-----Using Linux/Windows-----
#(1) Downlaod tesseract and language:
    sudo apt-get install tesseract-ocr-[rus]
#(2) Download Python wrapper
    pip install pytesseract
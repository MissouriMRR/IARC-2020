# Text

Algorithms relating to the text, the mast and the russian words on mast.

## Detect Russian Word: 'модули иртибот'

Download pytesseract for OCR (optical character recognition)

* IMPORTANT: * Make sure to install extra language pack for Uzbek Cyrilic

### Using Linux

1.  Download tesseract and language

```bash
    sudo apt-get install tesseract-ocr
    sudo apt-get install tesseract-ocr-uzb-cyrl
```

### Using Windows

* Download Python wrapper

```bash
    pip install pytesseract
```
* Include the tesseract in your path

### Using Mac and Homebrew

1.  Download tesseract

```bash
   brew install tesseract
```

2.  Download tesseract-lang (to use Russian)

```bash
   brew install tesseract-lang
```

## Using in Python
1.  Download Python wrapper

```bash
    pip3 install pytesseract
```
2.  Include the tesseract in your path if necessary
3.  Import pytesseract

# OCRApp 📄🔍
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Config-Driven OCR Pipeline for Structured Data Extraction**

A desktop application that extracts structured data from images  
using **template-based OCR** and automatically inserts it into a database.

Built with **Python**, **Tesseract OCR**, and a **modular extraction engine**.

---

## 🎬 Demo

https://github.com/user-attachments/assets/61a088df-193c-48a8-ae5c-5d5d93112350

Example workflow:

```
Image → Preprocessing → OCR → Extraction → Validation → Database
```

---

## ❗ Problem

Extracting structured information from documents is difficult because:

- OCR returns **unstructured text**
- Documents have **different layouts**
- Data must often be **manually entered into databases**

This project solves the problem by using **template-driven OCR extraction**.

---

## 💡 Solution

OCRApp allows users to define templates describing:

- **What data to extract**
- **Where it appears in the document**
- **How to validate it**

The application then:

1. Runs OCR on the image
2. Extracts fields using configured methods
3. Validates the data
4. Inserts results directly into a database

---

## 🏗 Architecture

```
OCRAPP
│
├── configs/        → OCR templates
├── data/           → extracted database
├── db/             → database layer
├── logs/           → application logs
├── ocr_core/       → OCR engine & extractors
├── ui/             → desktop interface
└── utils/          → shared utilities
```

### Core Components

**OCR Engine**  
Handles preprocessing and text extraction.

**Extractors**  
Multiple extraction strategies:

- Bounding Box extraction
- Regex extraction
- Label-nearby detection
- Registry lookup

**Template System**  
Allows users to configure extraction logic without modifying code.

---

## ✨ Features

- Template-driven OCR extraction
- Multiple extraction methods
- Built-in preprocessing pipeline
- Data validation
- Automatic database insertion
- Editable results via UI
- Modular architecture

---

## 🔎 Extraction Methods

OCRApp supports multiple extraction strategies:

| Method | Description |
|------|------|
| bbox_region | Extract text from bounding box |
| regex | Extract using pattern matching |
| label_nearby | Detect value near label |
| registry | Lookup structured values |

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourname/ocrapp.git
cd ocrapp
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install **Tesseract OCR**

Windows:  
https://github.com/UB-Mannheim/tesseract/wiki

Make sure the path is configured:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ▶️ Run the Application

```bash
python app.py
```

---

## 🧾 Template Example

```json
{
  "fields": {
    "name": {
      "method": "label_nearby",
      "label": "Name"
    },
    "credits": {
      "method": "bbox_region",
      "bbox": [0.3,0.4,0.6,0.5]
    }
  }
}
```

---

## 📚 What I Learned

- Designing modular Python project architectures
- Building config-driven systems using templates
- Implementing an OCR processing pipeline
- Improving OCR accuracy through image preprocessing
- Creating multiple extraction strategies (bbox, regex, label detection)
- Structuring applications into logical modules
- Integrating SQLite for structured data storage
- Implementing logging and debugging workflows

---

## 🚀 Future Improvements

- PDF batch processing
- ML-based layout detection
- Automatic template generation
- REST API support
- Batch OCR processing for large datasets

---

## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

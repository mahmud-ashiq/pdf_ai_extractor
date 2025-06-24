# PDF Auditor Form Extractor

A Python tool that extracts form data and embedded documents from PDF files and generates AI-powered summaries using Google Gemini.

## Features

- Extract form field data from PDF files
- Process embedded documents using OCR
- Generate professional summaries using Google Gemini AI
- Export structured data as JSON

## Prerequisites

- Python 3.13.2+
- Google Gemini API key

## Installation

#### 1. Clone the repository:

```bash
git clone https://github.com/mahmud-ashiq/pdf_ai_extractor.git
cd pdf_ai_extractor
```

#### 2. Install required dependencies:

```bash
pip install -r requirements.txt
```

#### 3. Setup environment:

- For Windows:

```bash
cp .env.example .env
```

- For Linux/MacOS:

```bash
copy .env.example .env
```

#### 4. Set up your Google Gemini API key:

- [Get your API here](https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChsSEwjJm9TnhYiOAxUHwkwCHQIyCF0YACICCAEQABoCdG0&co=1&ase=2&gclid=CjwKCAjw9uPCBhATEiwABHN9K9oc5a_xaqkmRTTGyLuOH-1Hb41z5E8gVIXhHQbJ8HCH6KICzrr9sxoCvSgQAvD_BwE&ei=xItZaJmGMLu9seMPlovLmQ0&ohost=www.google.com&cid=CAESVuD2vd4sbbnY2tSJBC448cAMj3exRQoq6tixV90YMfzc2rmRSdkHSAB16jzcc3O2oIducry9Tvff9891azwcsA1Z7n4YElzWUJ2RQwf7V7yzC85Mksc3&category=acrcp_v1_45&sig=AOD64_3X4BULVq-oo-5RUPVNYhWIDz7C8w&q&sqi=2&nis=4&adurl&ved=2ahUKEwiZ-M3nhYiOAxW7XmwGHZbFMtMQ0Qx6BAgJEAE)
- Add your API key to **`.env `**:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Usage

#### 1. Place your PDF file in the project directory

#### 2. Run the extractor:

```bash
python extractor.py
```

The script will automatically:

- Detect PDF files in the current directory
- Extract form data and embedded documents (if any)
- Generate AI summaries
- Save outputs to `data.json` and `summary.txt`

## Output Files

- **`data.json`**: Structured form data in JSON format
- **`summary.txt`**: AI-generated summaries of the form data and attachments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

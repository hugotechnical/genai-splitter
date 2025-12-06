# GenAI Splitter

**GenAI Splitter** is a powerful Python-based tool designed to automate the classification and splitting of complex loan document sets (PDFs). It utilizes Optical Character Recognition (OCR) text outputs, fuzzy string matching, and rule-based logic to identify distinct document types within a single large PDF file and split them into separate, named files.

## Features

-   **Intelligent Document Classification**: Uses keyword matching with fuzzy logic (`thefuzz`) to identify document types even with minor OCR errors.
-   **Rule-Based Splitting**: Defines specific rules (keywords, categories, document names) to recognize headers and classify pages.
-   **Context Awareness**: Features logic to handle "Page Break" delimiters, blank pages, and noise reduction.
-   **Multi-Domain Support**: Includes specialized logic for different loan profiles:
    -   **Hồ Sơ Phê Duyệt (Approval Profiles)**: `main.py`
    -   **Hồ Sơ Ô Tô (Car Loan Profiles)**: `main_o_to.py`
    -   **Hồ Sơ Nhà Dự Án (Project Property Profiles)**: `main_nha_du_an.py`
    -   **Hồ Sơ Giải Ngân (Disbursement Profiles)**: `main_hsgn.py`
-   **PDF Manipulation**: Automatically splits the original source PDF into individual files named according to their classified content.

## Project Structure

```
genai-splitter/
├── data_input/             # Directory for input PDF files
├── data_parser/            # Directory for input JSON files (OCR text content)
├── data_output/            # Directory for output split PDFs (used by some scripts)
├── results_*/              # Output directories for specific modules
├── main.py                 # Main entry point for "Hồ Sơ Phê Duyệt"
├── main_o_to.py            # Entry point for "Hồ Sơ Ô Tô"
├── main_hsgn.py            # Entry point for "Hồ Sơ Giải Ngân"
├── rules.py                # shared rule definitions and keyword lists
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Prerequisites

-   Python 3.8 or higher
-   Pip (Python Package Installer)

## Installation

1.  Clone the repository or download the source code.
2.  Navigate to the project directory:
    ```bash
    cd genai-splitter
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Prepare Input Data

The tool works by matching text from a JSON file against the pages of a PDF file.
1.  **PDF File**: Place your source PDF file in the `data_input` directory (e.g., `ho-so-phe-duyet.pdf`).
2.  **JSON Content**: Ensure you have a JSON file containing the extracted text content of the PDF in the `data_parser` directory. The JSON structure usually expects an `extracted_content` field containing the text with `--- Page Break ---` delimiters.

### 2. Run the Splitter

Run the appropriate script based on the type of document you are processing.

**For Approval Profiles (Hồ Sơ Phê Duyệt):**
```bash
python main.py
```
*Note: Check `main.py` to ensure `json_filename` and `pdf_filename` variables point to your correct input files.*

**For Car Loan Profiles (Hồ Sơ Ô Tô):**
```bash
python main_o_to.py
```

### 3. Check Results

The tool will process the pages, print the classification results to the console, and generate split PDF files in the configured output directory (e.g., `results_ho_so_phe_duyet` or `data_output/results_o_to`).

The console output will show:
-   Processing progress per page.
-   Identified document triggers (keywords).
-   A summary table of classified documents with page ranges.

## Configuration

You can adjust processing parameters in the `Config` class at the top of each `main_*.py` file:

-   `LINES_THRESHOLD`: Number of lines from the top of the page to scan for headers.
-   `FUZZY_THRESHOLD`: Similarity score required for a match (0-100).
-   `MIN_CONTENT_LENGTH`: Minimum characters to consider a page valid (ignores blank pages).
-   `PAGE_BREAK_DELIMITER`: Delimiter used in the input JSON to separate pages.

## Customizing Rules

To add or modify document types, edit `rules.py` or the `DocumentRules` class in the specific `main` script. A rule typically consists of:
-   **Key**: The keyword to search for (upper case).
-   **Category**: The group the document belongs to.
-   **Name**: The descriptive name for the output file.
-   **Exclude Keys**: (Optional) Keywords that should disqualify a match.

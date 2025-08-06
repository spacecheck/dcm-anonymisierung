# DICOM Anonymizer

A Python script for anonymizing DICOM files while preserving the hierarchical folder structure.

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the input and output directory paths:

```bash
python main.py /path/to/input/directory /path/to/output/directory
```

## Directory Structure

This script is designed to work with the following directory structure:

```
input_directory/
├── patient1/
│   ├── study1/
│   │   ├── series1/
│   │   │   ├── dicom_file1
│   │   │   ├── dicom_file2
│   │   │   └── ...
│   │   └── series2/
│   │       └── ...
│   └── study2/
│       └── ...
├── patient2/
└── ...
```

The script will create an identical structure in the output directory, but will rename patient folders to anonymous IDs (pat0000001, pat0000002, etc.).

## Anonymization Settings

The script applies the following anonymization rules:

### Modified Fields:
- **Patient's Birth Date** (0010,0030): Only preserves the year (sets month and day to January 1st)
- **Study Date** (0008,0020): Only preserves the year (sets month and day to January 1st)

### Preserved Fields:
- **Patient Sex** (0010,0040): Kept as is
- **Accession Number** (0008,0050): Kept as is
- **Series Description** (0008,103E): Kept as is

All private tags are removed during the anonymization process.

# Studio ETL Image Ingestion Pipeline

A modular, robust, and production-ready Python Extract-Transform-Load (ETL) pipeline designed for high-volume photography studios. This system maps sequential camera files (e.g., `IMG_0001.jpg`) to student master records, verifies image integrity, downscales portal previews, and records execution analytics.

---

## Features

1.  **Validation Layer (Data Quality Check)**: Uses Pillow's `verify()` method to analyze image headers and structural integrity without loading raw pixel data into memory. Corrupted images are caught, logged, and skipped without crashing the run.
2.  **Web Portal Proxy Optimization**: Downscales copy actions to a maximum width of `800px` (preserving aspect ratio) for portal uploads, saving bandwidth.
3.  **Production Logging & Ledger**: Appends timestamped execution statistics (execution time, successes, missing items, corruptions) to a persistent markdown history file (`pipeline_history.md`).
4.  **Multi-Shot Suffix Tracking**: Automatically detects when a student has multiple consecutive shots and suffixes the outputs (`_1`, `_2`) to prevent file overwrites.

---

## Directory Structure

```text
Data-image-pipeline/
├── raw_camera_dump/         # Source folder containing raw photo dumps (e.g., IMG_0001.jpg)
├── organized_output/        # Target folder for successfully mapped high-res files
├── web_portal_proxies/      # Target folder for compressed, web-ready preview files
├── generate_mock_data.py    # Mock environment creator
├── etl_pipeline.py          # Core ETL pipeline executor
├── requirements.txt         # Package dependencies (Pandas, Pillow)
├── student_roster.csv       # Master metadata roster
└── pipeline_history.md      # Run execution statistics ledger
```

---

## Getting Started

### 1. Install Dependencies
Ensure you have Python installed, then install the package requirements:
```bash
pip install -r requirements.txt
```

### 2. Generate Mock Data
Initialize the test environment. This will programmatically create the camera folders, dummy image files (including valid, corrupted, and missing cases), and the roster CSV:
```bash
python generate_mock_data.py
```

### 3. Run the ETL Pipeline
Process the roster database and ingest the photos:
```bash
python etl_pipeline.py
```

---

## Execution Summary & Ledger
After executing the pipeline, check **[pipeline_history.md](file:///c:/Users/deeno/Documents/Juvio/Data-image-pipeline/pipeline_history.md)** to see the run durations and processing diagnostics.

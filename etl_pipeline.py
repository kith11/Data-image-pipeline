import os
import time
import shutil
import pandas as pd
import logging
from datetime import datetime
from PIL import Image, UnidentifiedImageError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ETL_Pipeline")

def validate_image(file_path):
    """
    1. THE VALIDATION LAYER (Data Quality Check):
    Verifies that the image file is valid and not corrupted.
    Uses Pillow's img.verify() to check headers and file integrity.
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, SyntaxError) as e:
        logger.error(f"Validation failed (corrupted file format): {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected file validation error: {e}")
        return False


def create_web_proxy(source_path, target_path, max_width=800):
    """
    3. LOW-RES WEB PROXY GENERATION:
    Creates a downscaled web-friendly version of the image (max 800px width),
    preserving the original aspect ratio, for fast loading on portals.
    """
    try:
        with Image.open(source_path) as img:
            width, height = img.size
            if width > max_width:
                ratio = max_width / float(width)
                new_height = int(float(height) * float(ratio))
                resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(target_path, "JPEG")
            else:
                img.save(target_path, "JPEG")
        logger.info(f" -> Generated low-res web proxy: '{os.path.basename(target_path)}'")
        return True
    except Exception as e:
        logger.error(f" -> Failed to generate web proxy for {source_path}. Error: {e}")
        return False


def log_execution_metrics(metrics, elapsed_time):
    """
    2. PIPELINE EXECUTION METRICS (The Production Ledger):
    Appends a timestamped Markdown summary of the run metrics to 'pipeline_history.md'.
    """
    history_file = "pipeline_history.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = (
        f"## Pipeline Execution - {timestamp}\n"
        f"- **Total Duration**: {elapsed_time:.4f} seconds\n"
        f"- **Total Records Evaluated**: {metrics['total_records']}\n"
        f"- **Successful Maps**: {metrics['successful_maps']}\n"
        f"- **Missing/Failed Files**: {metrics['missing_files']}\n"
        f"- **Corrupted Files**: {metrics['corrupted_files']}\n"
        f"--------------------------------------------------\n\n"
    )
    
    try:
        write_header = not os.path.exists(history_file)
        with open(history_file, "a") as f:
            if write_header:
                f.write("# ETL Pipeline Execution Ledger\n\n")
            f.write(log_entry)
        logger.info(f"Successfully wrote execution ledger entry to '{history_file}'")
    except Exception as e:
        logger.error(f"Failed to write to execution history file. Error: {e}")


def run_etl_pipeline():
    """
    Coordinates the robust pipeline operations.
    Organizes high-res outputs into dedicated student subfolders.
    """
    start_time = time.time()
    logger.info("Initializing ETL Production Pipeline...")
    
    csv_file = "student_roster.csv"
    raw_dir = "raw_camera_dump"
    output_dir = "organized_output"
    web_dir = "web_portal_proxies"
    
    # Ensure root output directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)
    
    # In-memory metrics tracking
    metrics = {
        "total_records": 0,
        "successful_maps": 0,
        "missing_files": 0,
        "corrupted_files": 0
    }
    
    student_photo_counters = {}
    
    # ------------------ EXTRACT ------------------
    logger.info("--- EXTRACT PHASE ---")
    try:
        roster_df = pd.read_csv(csv_file)
        metrics["total_records"] = len(roster_df)
        logger.info(f"Extracted {metrics['total_records']} student records.")
    except FileNotFoundError:
        logger.error(f"FATAL: Master roster '{csv_file}' not found. Please run 'generate_mock_data.py' first.")
        return
    except Exception as e:
        logger.error(f"FATAL: Ingestion failed. Error: {e}")
        return

    # ------------------ TRANSFORM & LOAD ------------------
    logger.info("--- TRANSFORM & LOAD PHASE ---")
    for index, row in roster_df.iterrows():
        student_id = row['Student_ID']
        full_name = row['Full_Name']
        seq_num = row['Expected_Sequence_Num']
        
        logger.info(f"Processing student {student_id}: {full_name}")
        
        # 1. Transform Name
        cleaned_name = str(full_name).strip().replace(" ", "_").upper()
        
        # Determine paths
        expected_filename = f"IMG_{str(seq_num).zfill(4)}.jpg"
        source_path = os.path.join(raw_dir, expected_filename)
        
        # Check if source file exists (Missing File check)
        if not os.path.exists(source_path):
            logger.warning(f" -> SKIPPED: Source file '{expected_filename}' is missing.")
            metrics["missing_files"] += 1
            continue
            
        # Check if image is corrupted (Validation Layer check)
        if not validate_image(source_path):
            logger.error(f" -> SKIPPED: Source file '{expected_filename}' is corrupted.")
            metrics["corrupted_files"] += 1
            continue
            
        # Increment photo index counter for this student
        student_photo_counters[student_id] = student_photo_counters.get(student_id, 0) + 1
        photo_num = student_photo_counters[student_id]
        
        # Create student-specific folder inside organized_output
        student_folder_name = f"{student_id}_{cleaned_name}"
        student_output_dir = os.path.join(output_dir, student_folder_name)
        os.makedirs(student_output_dir, exist_ok=True)
        
        # Unique target file path inside the student's subfolder
        target_filename = f"{student_id}_{cleaned_name}_{photo_num}_TOGA.jpg"
        target_path = os.path.join(student_output_dir, target_filename)
        
        # Web preview filename
        preview_filename = f"{student_id}_preview_{photo_num}.jpg"
        preview_path = os.path.join(web_dir, preview_filename)
        
        # Copy high-res file (Load phase)
        try:
            shutil.copy2(source_path, target_path)
            logger.info(f" -> Successfully mapped: {expected_filename} -> {student_folder_name}/{target_filename}")
            
            # Generate Web Proxy (Optimization layer)
            proxy_success = create_web_proxy(source_path, preview_path)
            if proxy_success:
                metrics["successful_maps"] += 1
            else:
                metrics["corrupted_files"] += 1
        except Exception as e:
            logger.error(f" -> ERROR: Failed to load image files. Reason: {e}")
            metrics["corrupted_files"] += 1

    # End timer and save metrics
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    logger.info("="*50)
    logger.info("ETL Production Ingestion Complete.")
    log_execution_metrics(metrics, elapsed_time)

if __name__ == "__main__":
    run_etl_pipeline()

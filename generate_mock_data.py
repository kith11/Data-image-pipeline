import os
import shutil
import pandas as pd
import logging
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MockDataGenerator")

def generate_mock_environment():
    """
    Generates a mock dataset where:
    - Each student has exactly 2 photos.
    - Students STU001 and STU002 have the specific actual names.
    - Students STU003 to STU018 have realistic dummy names.
    - Students STU001 to STU016 are valid (32 valid photos: IMG_0001.jpg to IMG_0032.jpg).
    - Student STU017 has one valid photo (IMG_0033.jpg) and one corrupted file (IMG_0034.jpg).
    - Student STU018 has missing photos (expected sequence 35 and 36, files not present).
    """
    logger.info("Starting automated environment setup...")
    
    raw_dir = "raw_camera_dump"
    output_dir = "organized_output"
    web_dir = "web_portal_proxies"
    
    # Reset directories
    for directory in [raw_dir, output_dir, web_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logger.info(f"Cleaned up directory: '{directory}'")
        os.makedirs(directory, exist_ok=True)
    
    # 1. Generate 33 VALID JPEG images (1 to 32 for STU001-STU016, and 33 for STU017)
    colors = ["blue", "green", "red", "purple"]
    for i in range(1, 34):
        file_name = f"IMG_{str(i).zfill(4)}.jpg"
        file_path = os.path.join(raw_dir, file_name)
        
        color_choice = colors[(i - 1) % len(colors)]
        img = Image.new("RGB", (1600, 1200), color=color_choice)
        img.save(file_path, "JPEG")
        logger.info(f"Generated VALID image: '{file_path}'")
        
    # 2. Generate 1 CORRUPTED image file (IMG_0034.jpg for STU017's second photo)
    corrupted_path = os.path.join(raw_dir, "IMG_0034.jpg")
    with open(corrupted_path, "w") as f:
        f.write("THIS FILE IS CORRUPTED. NOT A REAL JPEG IMAGE.")
    logger.info(f"Generated CORRUPTED image placeholder: '{corrupted_path}'")
    
    # 3. Generate student roster CSV file
    mock_students = []
    
    # Realistic dummy names pool for STU003 to STU018
    realistic_dummy_names = [
        "Alice N. Dwonderland",
        "Bob B. Builder",
        "Charlie A. Green",
        "Eva M. White",
        "James W. Smith",
        "Mary E. Johnson",
        "Robert J. Williams",
        "Patricia L. Brown",
        "Michael S. Jones",
        "Linda K. Miller",
        "William D. Davis",
        "Elizabeth R. Garcia",
        "David A. Rodriguez",
        "Barbara J. Wilson",
        "Richard E. Martinez",
        "Susan M. Anderson"
    ]
    
    # Generate 16 valid students, each with 2 consecutive photos
    # STU001 -> John Keith A. Barrientos
    # STU002 -> Jason G. Barrientos
    # STU003 to STU016 -> Realistic dummy names
    seq = 1
    for s_idx in range(1, 17):
        student_id = f"STU{str(s_idx).zfill(3)}"
        
        if s_idx == 1:
            full_name = "John Keith A. Barrientos"
        elif s_idx == 2:
            full_name = "Jason G. Barrientos"
        else:
            # Map index to realistic dummy names list
            full_name = realistic_dummy_names[s_idx - 3]
        
        # Row 1 for student
        mock_students.append({
            "Student_ID": student_id,
            "Full_Name": full_name,
            "Expected_Sequence_Num": seq
        })
        seq += 1
        
        # Row 2 for student
        mock_students.append({
            "Student_ID": student_id,
            "Full_Name": full_name,
            "Expected_Sequence_Num": seq
        })
        seq += 1
        
    # Add STU017 (Corrupted case): 1 valid (seq 33), 1 corrupted (seq 34)
    # Using the next name in the realistic dummy list (index 14)
    mock_students.append({
        "Student_ID": "STU017",
        "Full_Name": realistic_dummy_names[14],
        "Expected_Sequence_Num": 33
    })
    mock_students.append({
        "Student_ID": "STU017",
        "Full_Name": realistic_dummy_names[14],
        "Expected_Sequence_Num": 34
    })
    
    # Add STU018 (Missing case): 2 missing images (seq 35, 36)
    # Using the final name in the realistic dummy list (index 15)
    mock_students.append({
        "Student_ID": "STU018",
        "Full_Name": realistic_dummy_names[15],
        "Expected_Sequence_Num": 35
    })
    mock_students.append({
        "Student_ID": "STU018",
        "Full_Name": realistic_dummy_names[15],
        "Expected_Sequence_Num": 36
    })
    
    df = pd.DataFrame(mock_students)
    csv_path = "student_roster.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Successfully generated master student roster: '{csv_path}'")
    logger.info("Mock environment setup complete!\n" + "="*50)

if __name__ == "__main__":
    generate_mock_environment()

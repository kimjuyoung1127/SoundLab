import numpy as np
from scipy.io import wavfile
import os
import warnings
from src.config import MAX_FILE_SIZE_MB

def load_audio(file_path_or_buffer):
    """
    Loads audio file with memory safety checks.
    """
    size_mb = 0
    
    # Check size if it's a file path
    if isinstance(file_path_or_buffer, str):
        if os.path.exists(file_path_or_buffer):
            size_mb = os.path.getsize(file_path_or_buffer) / (1024 * 1024)
    # Check size if it's a Streamlit UploadedFile
    elif hasattr(file_path_or_buffer, 'size'):
         size_mb = file_path_or_buffer.size / (1024 * 1024)
            
    if size_mb > MAX_FILE_SIZE_MB:
        warnings.warn(f"File size ({size_mb:.1f}MB) exceeds {MAX_FILE_SIZE_MB}MB safety limit. Using memory mapping (mmap).")
        # Note: wavfile.read with mmap=True is read-only and faster for large files
        sample_rate, data = wavfile.read(file_path_or_buffer, mmap=True)
    else:
        sample_rate, data = wavfile.read(file_path_or_buffer)
        
    return sample_rate, data

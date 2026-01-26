import numpy as np
from scipy.io import wavfile
import os
import warnings
from typing import Tuple, Union, Any
from src.config import MAX_FILE_SIZE_MB

def load_audio(file_path_or_buffer: Union[str, Any]) -> Tuple[int, np.ndarray]:
    """
    메모리 안전성 검사와 함께 오디오 파일을 로드합니다.
    
    Args:
        file_path_or_buffer: 파일 경로 또는 Streamlit UploadedFile 객체.
    
    Returns:
        Tuple[int, np.ndarray]: 샘플 레이트와 오디오 데이터.
    """
    size_mb = 0
    
    # 파일 경로인 경우 크기 확인
    if isinstance(file_path_or_buffer, str):
        if os.path.exists(file_path_or_buffer):
            size_mb = os.path.getsize(file_path_or_buffer) / (1024 * 1024)
    # Streamlit UploadedFile인 경우 크기 확인
    elif hasattr(file_path_or_buffer, 'size'):
         size_mb = file_path_or_buffer.size / (1024 * 1024)
            
    if size_mb > MAX_FILE_SIZE_MB:
        warnings.warn(f"파일 크기 ({size_mb:.1f}MB)가 안전 한도인 {MAX_FILE_SIZE_MB}MB를 초과했습니다. 메모리 매핑(mmap)을 사용합니다.")
        # 참고: mmap=True를 사용한 wavfile.read는 읽기 전용이며 대용량 파일에 더 빠릅니다.
        sample_rate, data = wavfile.read(file_path_or_buffer, mmap=True)
    else:
        sample_rate, data = wavfile.read(file_path_or_buffer)
        
    return sample_rate, data

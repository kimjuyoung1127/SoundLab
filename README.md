# SoundLab (SignalCraft Light-Lab)

SoundLab is a lightweight, Streamlit-based audio analysis tool designed to detect frequency anomalies effectively. It utilizes the **Goertzel algorithm** (optimized with Numba) to detect specific frequency signatures in WAV files.

## 🚀 Features

*   **Audio Upload**: Support for WAV files with size safety checks.
*   **Signal Analysis**:
    *   **Heavy Processing**: Uses a robust Goertzel algorithm (MAGI) to analyze target frequencies.
    *   **Light Processing**: Fast re-calculation of thresholds using Otsu's method.
*   **Performance**:
    *   **Smart Caching**: Optimized caching strategy that hashes file references instead of large data arrays, ensuring smooth UI performance even with large files.
    *   **Numba JIT**: Core math loops are compiled to machine code for near-C speed.
    *   **Memory Efficiency**: Memory-mapped file reading (`mmap`) prevents crashes on large files.
*   **Visualization**: Interactive Plotly charts showing magnitude vs. time and anomaly thresholds.

## 🛠️ Installation & Usage

### Prerequisites
*   Python 3.9+ recommended.

### Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

Run the Streamlit application from the `frontend` directory:

```bash
streamlit run src/main.py
```

---

# 📝 Code Review & Improvements Report

Based on the automated code review using the `code-review` skill, here are the findings and suggested improvements for the current codebase.

## ✅ Implemented Improvements & Good Practices
1.  **Optimized Caching Strategy (Performance)**:
    *   **Improvement**: Refactored `src/core/analysis.py` to accept the `uploaded_file` object directly instead of raw NumPy arrays.
    *   **Benefit**: Eliminates the need for Streamlit to hash large audio arrays (e.g., 100MB+), significantly reducing UI freeze times during analysis.
2.  **Performance**: Excellent use of `@jit(nopython=True)` in `src/core/magi.py`.
3.  **Safety**: The memory safety check (`MAX_FILE_SIZE_MB`) and usage of `mmap=True` in `src/core/audio.py` prevents the app from crashing on large files.
4.  **Architecture**: Clean separation of concerns (`core/` vs `ui/`).

## ⚠️ Remaining Suggestions

### 1. Type Hinting (Maintenance)
**Issue**: Many functions (e.g., `process_signal_heavy`, `render_app`) lack Python type hints.
**Solution**: Add type hints to improve developer experience and catch bugs early.
```python
# Before
def process_signal_heavy(signal, ...):

# Recommended After
def process_signal_heavy(signal: np.ndarray, ...) -> Tuple[np.ndarray, np.ndarray]:
```

### 2. Real Metrics Implementation (Correctness)
**Issue**: In `src/ui/layout.py`, the memory usage metric is currently hardcoded (`200`).
**Solution**: Use `psutil` to get real process memory usage for accurate monitoring.

### 3. Robust File Loading (Robustness)
**Issue**: `scipy.io.wavfile` is strict and may crash if users upload non-WAV files (e.g., renamed MP3s).
**Solution**: Wrap the loader in a `try-except` block and use `st.error` to gracefully handle invalid file formats.

## 📋 Recommended Action Plan

1.  **Immediate**: Add `psutil` to requirements and implement real memory tracking.
2.  **Long-term**: Add full type hinting and docstrings to the `core` module.
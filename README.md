# SoundLab (SignalCraft Light-Lab) 📡

**SoundLab**은 대용량 오디오 신호 분석 및 이상 징후(Frequency Anomaly) 탐지를 위해 설계된 초경량 분석 도구입니다. 복잡한 신호 처리 알고리즘을 최적화된 Python 엔진으로 구현하여, 연구원들이 직관적으로 데이터를 시각화하고 분석할 수 있도록 돕습니다.

---

## � 핵심 작동 원리 (Technical Core)

SoundLab은 전통적인 신호 처리 이론과 현대적인 JIT 컴파일 기술을 결합하여 고성능 분석을 수행합니다.

### 1. Robust Goertzel Algorithm (MAGI)
*   **원리**: 전체 FFT(Fast Fourier Transform)를 수행하는 대신, 특정 **목표 주파수(Target Frequency)** 성분만을 정밀하게 추출합니다. 이는 마치 라디오 주파수를 맞추듯, 노이즈 속에서 특정 신호의 강도만을 선별적으로 계산합니다.
*   **최적화**: `Numba`의 JIT(Just-In-Time) 컴파일러를 사용하여 Python 코드를 C/C++ 수준의 기계어로 실시간 변환, 실행 속도를 약 100배 가속화했습니다.

### 2. Adaptive Thresholding (Otsu's Method)
*   **원리**: 사용자가 임계값을 일일이 설정하지 않아도 **오츠 알고리즘(Otsu's Method)**을 통해 신호의 '배경 노이즈'와 '이상 신호'를 구분하는 최적의 기준선을 자동으로 계산합니다.
*   **유연성**: 자동 계산된 값에 `Sensitivity Multiplier`를 적용하여, 연구 목적에 따라 민감도를 미세 조정할 수 있습니다.

### 3. Smart Universal Analyzer V5.7 (New 🚀)
*   **Safe Trimming**: 단순 임계값 판정이 아닌, 이전 구간 대비 에너지 비율(<0.5)과 절대 에너지 레벨을 동시에 고려하여 기계 종료 시점을 오차 없이 명확하게 잘라냅니다.
*   **Multi-Band Analysis**: 535Hz(주력 식별), 60/120Hz(서지), 180Hz(과부하) 대역을 동시에 모니터링하여 가동 상태를 입체적으로 판별합니다.
*   **Smart Caching**: 무거운 연산(FFT/Goertzel)과 가벼운 UI 연산을 분리하여, 슬라이더 조작 시 즉각적인 반응 속도(Zero Latency)를 보장합니다.

---

## 🚀 주요 기능 (Key Features)

| 기능 | 설명 |
| :--- | :--- |
| **스마트 분석 모드** | **V5.7 알고리즘** 탑재. 기계의 ON/OFF 구간을 자동으로 인식하고 불필요한 노이즈 구간을 제거(Trimming)합니다. |
| **정밀 주파수 탐지** | 535Hz 공진음 식별 및 Multi-Band 에너지를 분석하여 정밀한 상태 진단 수행 |
| **대용량 파일 처리** | Memory Mapped I/O 기술을 적용하여 RAM 용량을 초과하는 대형 WAV 파일도 안정적으로 처리 |
| **인터랙티브 시각화** | 분석 결과의 시간축을 `분:초(MM:SS)` 단위로 직관적으로 표시하고, 이상징후 클릭 시 차트와 연동(Sync)됩니다. |

---

## 🛠️ 기술 스택 (Tech Stack)

*   **Frontend**: Streamlit (Python Pure UI)
*   **Core Engine**: NumPy, SciPy (Signal Processing)
*   **Acceleration**: Numba (LLVM-based JIT Compiler)
*   **Visuals**: Plotly (WebGL High-performance Charting)

---

## 📥 설치 및 실행 (Quick Start)

이 프로젝트는 로컬 환경과 클라우드 환경 모두를 지원합니다.

### 1. 로컬 설치 (연구원용)
고사양 분석이 필요한 경우 로컬 설치를 권장합니다. 상세 가이드는 [설치 가이드(docs/installation_guide.md)](docs/installation_guide.md)를 참고하세요.

```bash
# 빠른 실행
pip install -r requirements.txt
streamlit run src/main.py
```

### 2. 웹 배포 (팀 공유용)
Streamlit Cloud를 통해 설치 없이 웹 브라우저로 접속할 수 있습니다. [배포 가이드(docs/deployment.md)](docs/deployment.md)를 확인하세요.

---

## 📂 프로젝트 구조 (Architecture)

```
SoundLab/
├── src/
│   ├── core/           # 핵심 연산 엔진 (독립적 비즈니스 로직)
│   │   ├── magi.py     # Goertzel 알고리즘 및 Numba 최적화 코드
│   │   └── analysis.py # 신호 처리 파이프라인
│   ├── ui/             # 사용자 인터페이스 (View Layer)
│   │   ├── layout.py   # 메인 레이아웃 및 인터랙션 핸들링
│   │   └── plots.py    # 시각화 컴포넌트
│   └── main.py         # 애플리케이션 진입점
├── docs/               # 문서 (가이드, 진행상황)
└── requirements.txt    # 의존성 패키지 목록
```

---
**License**: MIT  
**Contact**: R&D Team
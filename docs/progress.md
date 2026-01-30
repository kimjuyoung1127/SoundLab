# 📅 개발 진행 상황 (Development Progress)

## 1. 스킬 이관 및 분석 (Skill Transfer & Analysis)
- [x] **스킬 복사**: `DogCoach` 프로젝트에서 `SoundLab`으로 `code-review` 스킬 이관 완료
- [x] **코드 리뷰**: `code-review` 스킬을 활용하여 `frontend` 코드 분석 수행
- [x] **개선점 도출**: 성능(캐싱), 유지보수(타입힌트), 안전성(파일로딩) 측면의 개선 사항 식별

## 2. 문서화 (Documentation)
- [x] **README.md 작성**: 프로젝트 소개, 기능, 설치/실행 방법 문서화
- [x] **리뷰 리포트 포함**: 코드 리뷰 결과 및 개선 제안 사항을 README에 통합 작성
- [x] **사용자 요청 반영**: README 내용을 한국어로 번역 및 최신화
- [x] **설치/배포 가이드 분리**: `docs/installation_guide.md`, `docs/deployment.md` 작성

## 3. 환경 설정 및 실행 (Environment Setup)
- [x] **가상환경 생성**: `python -m venv venv`
- [x] **의존성 설치**: `pip install -r requirements.txt` 및 `psutil` 추가
- [x] **앱 실행**: Streamlit 애플리케이션 정상 구동 확인

## 4. 성능 최적화 및 기능 개선 (Improvements Implementation)
- [x] **캐싱 최적화 (Critical)**:
    - [x] `src/core/analysis.py`: 대형 NumPy 배열 해싱 방지를 위해 `uploaded_file` 객체 전달 방식으로 리팩토링
    - [x] `src/ui/layout.py`: 변경된 함수 시그니처 적용
- [x] **메모리 모니터링 구현**:
    - [x] `psutil` 라이브러리 도입
    - [x] `src/ui/layout.py`: 하드코딩된 값(200MB)을 실제 프로세스 메모리 사용량으로 교체
- [x] **타입 힌트 및 문서화 (Type Hinting & Docstrings)**:
    - [x] `src/core/analysis.py`: 주요 함수에 타입 힌트 및 반환 타입 명시
    - [x] `src/core/audio.py`: 파일 로딩 함수에 타입 힌트 추가
    - [x] `src/core/magi.py`: `robust_goertzel_magi` 함수에 Numba 호환 타입 힌트 추가

## 5. 아키텍처 리팩토링 (Architecture Refactoring)
- [x] **Service Layer 패턴 도입**: UI와 Core 로직의 분리 (1:1 매핑)
    - [x] `src/core/services.py` 생성 및 비즈니스 로직 캡슐화
    - [x] `Metrics` 및 `Analysis` 로직을 Service 계층으로 이동

## 6. 사용자 경험 (UX) 개선
- [x] **온보딩 대안 구현**:
    - [x] **'앱 사용 가이드' (Expander)** 추가
    - [x] **상세 툴팁(Tooltips) 적용**
- [x] **인터랙티브 시각화 (Interactive Features)**:
    - [x] **이상징후 클릭 하이라이트**: 로그-차트 연동
    - [x] **다중 선택(Multi-Select) 지원**: Shift/Ctrl 키 지원

## 7. 스마트 분석 (Smart Analysis Mode) - New 🌟
- [x] **ON/OFF 자동 감지**: 소음(Silence) 임계값을 자동 계산하여 기계 가동 중에만 분석 수행
- [x] **대역폭 자동 튜닝 (Auto-Bandwidth)**: FFT 피크 분석을 통해 신호의 대역폭을 스스로 감지
- [x] **상대 단위 변환**: Audacity 등 타 툴과의 비교 용이성을 위해 크기를 %(퍼센트) 단위로 정규화
- [x] **UI 통합**: '스마트 분석 모드' 토글 및 결과 리포트(감지된 대역폭 등) 표시 구현

## 8. 알고리즘 고도화 (Algorithm Upgrade) - V5.7 🚀
- [x] **V5.7 핵심 로직 이식**: Node.js 레퍼런스(Smart Universal Analyzer V5.7)의 Python(NumPy/Numba) 이식 완료
    - [x] **Safe Trimming (안전 절삭)**: 급격한 종료 오판을 방지하기 위해 비율(<0.5)과 절대 에너지를 동시에 고려
    - [x] **535Hz 식별 주파수 적용**: 기계 가동 감지를 위한 공진 주파수(535Hz) 적용 및 멀티 밴드(60/120/180Hz) 분석 동시 수행
    - [x] **Otsu 임계값 고도화**: 에너지 분포에 따른 동적 임계값 계산 최적화
- [x] **UI 직관성 개선 (Readability)**:
    - [x] **시간 포맷 변경**: `초(sec)` 단위에서 `분:초(MM:SS)` 형식으로 변경하여 가독성 강화
    - [x] **용어 명확화**: `Magnitude` -> `신호 추출 정밀도`, `Threshold` -> `가동 판단 기준점` 등 직관적인 한글화
    - [x] **타임라인 시각화**: 가동 구간을 시각적으로 보여주는 **Gantt Chart** 및 요약(가동 횟수, 총 시간) 뷰 구현

## 9. 대시보드 고도화 및 인프라 (Dashboard & Infra) - New 🌟
- [x] **UI 컴포넌트화 (Modularity)**:
    - [x] `live_tab.py`, `file_tab.py`, `sidebar.py`로 로직 분리 및 모듈화
    - [x] `layout.py`를 오케스트레이터 구조로 슬림화하여 유지보수성 향상
- [x] **데이터 내보내기 (Data Export)**:
    - [x] 실시간/파일 분석 결과 전체를 CSV 형식으로 저장하는 기능 구현 (UTF-8-BOM 지원)
- [x] **차트 인터랙션 강화 (UX Polish)**:
    - [x] **Spike Lines**: 마우스 위치에 따른 정밀 타겟팅 라인 추가
    - [x] **Anomaly Highlighting**: 이상 징후 포인트 호버 시 강조 효과 및 맞춤형 툴팁 적용
    - [x] **Auto-Zoom**: 분석 시 이상 징후 발생 구간으로 자동 줌인 기능 구현


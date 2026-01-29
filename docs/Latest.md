# 분석 로직 통합 요약 (Latest Analysis Logic Integration)

이 문서는 `Guardian-1` 연구원의 최신 하드웨어(Arduino) 및 소프트웨어(Python) 로직을 분석하고, `SoundLab` 프로젝트와의 통합 방향을 정리합니다.

## 1. 하드웨어 로직 (sketch_jan27_hotspot.ino)
**역할**: ESP32에서 진동 신호 획득 및 특징값(Feature) 추출 후 Supabase 전송.

### 핵심 알고리즘
- **고이젤(Goertzel) 알고리즘**:
  - 특정 주파수(60Hz, 120Hz) 성분의 에너지를 효율적으로 계산.
  - 샘플링 속도(16kHz)와 분석 길이(16,000 샘플) 기반으로 정밀도 확보.
- **스캔 범위**:
  - **60Hz Band**: 58.0 ~ 62.0Hz (0.1Hz 간격, 41개 데이터)
  - **120Hz Band**: 116.0 ~ 124.0Hz (0.2Hz 간격, 41개 데이터)
  - **총 82개 데이터 포인트**를 JSON 배열(`features`)로 생성.
- **데이터 전송**:
  - 10초 주기로 Supabase `sound_logs` 테이블에 `POST` 요청.

## 2. 대시보드 로직 (sound_logs.py)
**역할**: Supabase에서 특징값을 읽어와 정밀 주파수 밴드 시각화.

### 시각화 및 노이즈 관리
- **실시간 폴링**: 5초마다 Supabase의 최신 데이터를 1건 조회.
- **데이터 분리**: 82개 데이터를 60Hz 밴드(41개)와 120Hz 밴드(41개)로 분리하여 막대 그래프(Bar Chart)로 표시.
- **중복 방지**: Plotly 차트ের 고유 `key`를 타임스탬프 기반으로 생성하여 데이터 업데이트 시 UI 충돌 방지.

## 3. SoundLab 로직과의 비교 및 향후 과제

| 기능 | 현재 하드웨어/연구원 로직 | SoundLab (V5.7 적용 필요) |
| :--- | :--- | :--- |
| **분석 주파수** | 60Hz, 120Hz | 60Hz, 120Hz, **180Hz** |
| **판단 로직** | 단순 시각화 (수동 판단) | **자동 판정 (스마트 분석 모드)** |
| **임계값 설정** | 없음 (Raw Data만 전송) | **Otsu 알고리즘 기반 자동 설정** |
| **상태 머신** | 없음 | **가동(ON)/비가동(OFF) 자동 감지** |

### 통합 전략 (Next Steps)
1.  **하드웨어 고도화**: `sketch_jan27_hotspot.ino`에 180Hz 스캔 로직 추가 고려.
2.  **클라이언트 사이드 인텔리전스**: `sound_logs.py` 방식의 대시보드에 `SoundLab`의 **Safe Trimming** 및 **Hysteresis** 로직을 이식하여 "이상징후(Anomaly)"를 자동 탐지하도록 개선.
3.  **데이터베이스 활용**: 판정된 결과(정상/이상)를 Supabase에 다시 기록하여 이력 관리 시스템 구축.

## 4. 인계 및 연결 설정 (Hand-over & Connection)
인계 시 ESP32 하드웨어와 즉시 연동될 수 있도록 아래 환경 변수를 프로젝트 설정(`.env` 또는 `secrets.toml`)에 동일하게 적용합니다.

### Supabase 접속 정보
SUPABASE_URL = "https://zigwndnmxmxctcayeavx.supabase.co"
SUPABASE_KEY = "sb_publishable_b8Cotvjt7qt3HOVgVY0KwA_f3h-yOuw"
- **Target Table**: `sound_logs` (현재 하드웨어가 데이터를 적재하는 테이블)

### 하드웨어(ESP32) 설정 정보
- **Wi-Fi SSID**: `theowl`
- **Wi-Fi Password**: `12345678`
- **Device ID**: `machine_01` (또는 `esp32_01`)
- **Sampling Rate**: `16000 Hz`
- **Analysis Length (N)**: `16000`


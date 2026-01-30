🧠 Final Execution Plan: Serverless Intelligence
전체 흐름:  
ESP32 (Gather) → Supabase (Store) → SoundLab (Think & Show)

Phase 1: Connection (Body) 🔗
ESP32가 Supabase에 JSON 업로드

SoundLab이 Supabase에서 데이터를 읽음

supabase_client.py에서 fetch_latest_logs(limit=10) 구현

Phase 2: Logic Adaptation (Brain) 🧠
기존 analysis.py를 JSON 기반으로 수정

stream_processor.py 생성

60Hz: 인덱스 0~40

120Hz: 인덱스 41~81

Otsu Threshold + Hysteresis 적용

Phase 3: Real-Time Dashboard (Face) 📊
monitor.py 페이지 생성

2~5초마다 자동 새로고침

UI 구성:

상태 표시: 🟢 정상 / 🔴 이상

실시간 차트: 최근 5분간 60Hz/120Hz

진단 로그: "10:00 - Motor Started", "10:15 - 이상 감지"

Phase 4: Hand-over 🤝
.env 또는 secrets.toml 구성

ESP32가 데이터 전송 시 대시보드가 실시간으로 반응하는지 확인
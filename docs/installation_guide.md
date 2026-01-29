# 💻 로컬 설치 및 실행 가이드 (Local Installation Guide)

클라우드 환경의 리소스 제한(메모리, 파일 크기)을 극복하고, 대용량 WAV 파일을 빠르고 안정적으로 분석하기 위해 연구원 개인 PC에 직접 설치하여 사용하는 방법입니다.

## 1. 전제 조건 (Prerequisites)
설치 전 다음 프로그램들이 컴퓨터에 설치되어 있어야 합니다.

*   **Python (3.9 이상)**: [Python 공식 홈페이지](https://www.python.org/downloads/)에서 다운로드
*   **Git**: [Git 공식 홈페이지](https://git-scm.com/downloads)에서 다운로드
*   **VS Code (선택 사항)**: 코드 확인 및 수정 시 권장

## 2. 설치 단계 (Installation Steps)

### 단계 1: 프로젝트 다운로드 (Clone)
터미널(CMD 또는 PowerShell)을 열고 원하는 폴더로 이동한 뒤, 다음 명령어를 입력합니다.

```bash
git clone https://github.com/kimjuyoung1127/SoundLab.git
cd SoundLab
```

### 단계 2: 가상환경 생성 (Virtual Environment)
다른 파이썬 프로젝트와 충돌을 방지하기 위해 격리된 가상환경을 만듭니다.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(성공 시 터미널 프롬프트 앞에 `(venv)`가 표시됩니다.)*

### 단계 3: 필수 라이브러리 설치 (Dependencies)
루트 폴더에 있는 `requirements.txt`를 통해 필요한 패키지들을 일괄 설치합니다.

```bash
pip install -r requirements.txt
```

## 3. 실행 방법 (Run Application)
설치가 완료되면 다음 명령어로 분석 도구를 실행합니다.

```bash
python -m streamlit run src/main.py
```

브라우저가 자동으로 열리며 `http://localhost:8501` 주소로 접속됩니다.

## 4. 로컬 실행의 장점
*   **대용량 처리**: 클라우드(1GB 제한)와 달리, PC의 메모리(RAM)를 온전히 사용하여 GB 단위의 파일도 분석 가능합니다.
*   **보안**: 데이터가 외부 서버로 전송되지 않고 로컬 PC 내에서만 처리됩니다.
*   **속도**: 네트워크 업로드/다운로드 과정이 없어 분석이 즉각적입니다.

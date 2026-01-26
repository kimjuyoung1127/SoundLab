# 🚀 배포 가이드 (Deployment Guide)

이 문서는 **Streamlit Community Cloud**를 사용하여 프로젝트를 배포하고, Git Push를 통해 자동으로 업데이트되도록 설정하는 방법을 안내합니다.

## 1. 전제 조건 (Prerequisites)
- [x] 프로젝트가 GitHub에 업로드되어 있어야 합니다. (현재 완료됨)
- [x] `requirements.txt`에 모든 의존성 패키지가 포함되어 있어야 합니다. (현재 완료됨)

## 2. Streamlit Cloud 설정 (Setup)
1.  **[Streamlit Community Cloud](https://streamlit.io/cloud)**에 접속하여 `Sign up` 또는 `Log in`을 클릭합니다.
2.  **GitHub 계정으로 로그인**을 선택하여 연동합니다.
3.  로그인 후 우측 상단의 **'New app'** 버튼을 클릭합니다.

## 3. 앱 배포 설정 (Deploy App)
다음 정보를 입력하여 앱을 생성합니다:

| 항목 | 설정 값 (예시) | 비고 |
| :--- | :--- | :--- |
| **Repository** | `kimjuyoung1127/SoundLab` | 본인의 리포지토리 선택 |
| **Branch** | `main` | 배포할 브랜치 |
| **Main file path** | `frontend/src/main.py` | **중요**: 실행 진입점 파일 경로 |

4.  **'Deploy!'** 버튼을 클릭합니다.

## 4. 배포 후 관리
*   **자동 업데이트**: 이제 로컬에서 코드를 수정하고 `git push`를 하면, Streamlit Cloud가 변경 사항을 감지하고 자동으로 앱을 재배포합니다.
*   **로그 확인**: 앱 화면 우측 하단의 'Manage app' > 'Logs'에서 실행 로그를 확인할 수 있습니다.
*   **공유**: 배포된 **URL**을 복사하여 팀원들에게 공유하세요. 어디서든 접속 가능합니다.

## ⚠️ 주의사항
*   **Python 버전**: Streamlit Cloud 설정에서 **Python Version**을 로컬 환경과 동일하게(예: 3.9, 3.10) 설정하는 것이 좋습니다.
*   **메모리 제한**: 무료 플랜은 1GB 내외의 리소스를 제공합니다. 대용량 WAV 파일 처리 시 주의가 필요합니다.

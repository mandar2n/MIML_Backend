# MIML_BACKEND

## 프로젝트 실행 방법

1. **Conda 환경 생성 및 의존성 설치**:
   `environment.yml` 파일에 정의된 패키지를 사용하여 Conda 환경을 생성한다. 이 과정에서 필요한 의존성도 함께 설치된다.
   ```bash
   conda env create -f environment.yml

2. **가상환경 활성화**:
   ```bash
   conda activate fastapi

3. **프로젝트 실행**:
   ```bash
   uvicorn src.main:app --reload

# ProductOrder-BE/Dockerfile

# Python 3.10 기반 이미지 사용
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 프로젝트 파일 복사
COPY ./app .

# 필요한 패키지 설치
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir poetry

# Poetry 설정 파일 복사
COPY pyproject.toml poetry.lock /app/

# 가상환경을 생성하지 않고 패키지 설치
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi



# uvicorn을 통해 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
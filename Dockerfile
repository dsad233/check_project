# ProductOrder-BE/Dockerfile

# Python 3.13 기반 이미지 사용
FROM python:3.13

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

# Poetry 설정 파일 복사
COPY pyproject.toml poetry.lock /app/

# 가상환경을 생성하지 않고 패키지 설치
RUN poetry config virtualenvs.create false && \
    poetry lock --no-update && \
    poetry install --no-interaction --no-ansi

# 프로젝트 파일 복사
COPY ./app

# uvicorn을 통해 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables to optimize Python's behavior in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MODE=dev

# Install system dependencies required for building Python packages with C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Set the working directory inside the container
WORKDIR /app

# Copy only the dependency files first to leverage Docker's caching
COPY ./pyproject.toml ./poetry.lock /app/

# Configure Poetry to not create virtual environments within the Docker container
RUN poetry config virtualenvs.create false

# Install project dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app/

# Expose the port your FastAPI app runs on (adjust if necessary)
EXPOSE 8000

# Define the default command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

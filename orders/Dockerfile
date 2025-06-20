FROM python:3.9-slim

# ---- Install system dependencies ----
RUN apt-get update && \
    apt-get install --yes netcat-openbsd gcc libffi-dev libssl-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- Set environment variables ----
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ---- Create and set working directory ----
WORKDIR /var/nameko

# ---- Copy project files ----
COPY . .

# ---- Install Python dependencies ----
RUN pip install --upgrade pip && \
    pip install .

# ---- Make run.sh executable ----
RUN chmod +x run.sh

# ---- Expose the port for the service ----
EXPOSE 8000

# ---- Run the service ----
CMD ["./run.sh"]
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install --yes netcat-openbsd gcc libffi-dev libssl-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set working directory
# All subsequent COPY commands will be relative to this WORKDIR
WORKDIR /var/nameko

# Copy requirements.txt first to leverage Docker layer caching
# Assuming requirements.txt is in the top-level orders/ directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project structure (including the nested 'orders' folder and alembic)
# The '.' here refers to the build context, which is your top-level 'orders' directory
COPY . .

# Ensure run.sh is executable
# Assuming run.sh is in the top-level orders/ directory
RUN chmod +x run.sh

# Run the service
CMD ["./run.sh"]
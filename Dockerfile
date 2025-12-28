# Base image with Python
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files to container
COPY main.py docker_manager.py vm_manager.py ./

# Optional: install dependencies if you have a requirements.txt
# RUN pip install -r requirements.txt

# Default command to run your app
CMD ["python", "main.py"]
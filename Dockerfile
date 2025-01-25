# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    festival \
    espeak && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory to /app
WORKDIR /app

# Install Python packages
RUN pip install phonemizer pandas

# Create a directory to store data files
RUN mkdir -p /app/data

# Copy the current directory contents into the container at /app
COPY . /app

# Expose any ports if necessary (optional)
EXPOSE 80

# Command to run your Python script
CMD ["python", "main.py"]


# Build the Docker image
#docker build -t phonemizer .

# Run the Docker container
#docker run -it --rm phonemizer

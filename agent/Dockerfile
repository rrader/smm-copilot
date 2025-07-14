# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y imagemagick

# Copy requirements and install dependencies
COPY instagram_bot/requirements.txt ./instagram_bot/requirements.txt
RUN pip install --no-cache-dir -r instagram_bot/requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables (optional, e.g., PYTHONUNBUFFERED for logging)
ENV PYTHONUNBUFFERED=1

# Run the main module
ENTRYPOINT ["python", "-m", "instagram_bot.main"] 
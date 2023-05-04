# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY req.txt .

RUN python -m pip install --upgrade pip
# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

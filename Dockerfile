# Use an official Python runtime as a base image
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your application will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
